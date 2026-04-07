"""
调度模块API路由 / Dispatch Module API Routes

提供车辆调度、泊位管理、排队系统的RESTful接口
Provides RESTful APIs for vehicle dispatch, berth management, queue system

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.modules.dispatch.models import (
    Vehicle, VehicleCreate, VehicleRead, VehicleUpdate,
    Berth, BerthRead, BerthStatus,
    Schedule, ScheduleCreate, ScheduleRead, ScheduleUpdate, ScheduleStatus
)
from app.modules.dispatch.services import (
    SmartDispatchService, QueueManager, DispatchRecommendation
)

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


# ============== 车辆管理 / Vehicle Management ==============

@router.get("/vehicles", response_model=List[VehicleRead])
async def list_vehicles(
    status: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """获取车辆列表 / Get vehicle list"""
    query = select(Vehicle)
    if status:
        query = query.where(Vehicle.status == status)
    if vehicle_type:
        query = query.where(Vehicle.vehicle_type == vehicle_type)

    result = await session.execute(query.offset(skip).limit(limit))
    vehicles = result.scalars().all()
    return vehicles


@router.post("/vehicles", response_model=VehicleRead)
async def create_vehicle(
    vehicle: VehicleCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建车辆 / Create vehicle"""
    db_vehicle = Vehicle.model_validate(vehicle)
    session.add(db_vehicle)
    await session.commit()
    await session.refresh(db_vehicle)
    return db_vehicle


@router.get("/vehicles/{vehicle_id}", response_model=VehicleRead)
async def get_vehicle(vehicle_id: int, session: AsyncSession = Depends(get_session)):
    """获取车辆详情 / Get vehicle details"""
    vehicle = await session.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.patch("/vehicles/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: int,
    vehicle_update: VehicleUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新车辆信息 / Update vehicle"""
    vehicle = await session.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    update_data = vehicle_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)

    session.add(vehicle)
    await session.commit()
    await session.refresh(vehicle)
    return vehicle


# ============== 泊位管理 / Berth Management ==============

@router.get("/berths", response_model=List[BerthRead])
async def list_berths(
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """获取泊位列表 / Get berth list"""
    query = select(Berth)
    if status:
        query = query.where(Berth.status == status)

    result = await session.execute(query)
    berths = result.scalars().all()
    return berths


@router.get("/berths/{berth_id}", response_model=BerthRead)
async def get_berth(berth_id: int, session: AsyncSession = Depends(get_session)):
    """获取泊位详情 / Get berth details"""
    berth = await session.get(Berth, berth_id)
    if not berth:
        raise HTTPException(status_code=404, detail="Berth not found")
    return berth


@router.get("/berths/{berth_id}/status")
async def get_berth_status(berth_id: int, session: AsyncSession = Depends(get_session)):
    """获取泊位实时状态 / Get berth real-time status"""
    berth = await session.get(Berth, berth_id)
    if not berth:
        raise HTTPException(status_code=404, detail="Berth not found")

    # 查询当前占用该泊位的调度
    result = await session.execute(
        select(Schedule).where(
            Schedule.berth_id == berth_id,
            Schedule.status.in_([
                ScheduleStatus.CHECKED_IN,
                ScheduleStatus.UNLOADING
            ])
        )
    )
    current_schedule = result.scalar_one_or_none()

    return {
        "berth_id": berth_id,
        "code": berth.code,
        "status": berth.status.value,
        "current_vehicle_id": berth.current_vehicle_id,
        "current_schedule_id": current_schedule.id if current_schedule else None,
        "capacity_tons": berth.capacity_tons,
    }


# ============== 调度管理 / Schedule Management ==============

@router.get("/schedules", response_model=List[ScheduleRead])
async def list_schedules(
    status: Optional[str] = None,
    vehicle_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """获取调度列表 / Get schedule list"""
    query = select(Schedule)
    if status:
        query = query.where(Schedule.status == status)
    if vehicle_id:
        query = query.where(Schedule.vehicle_id == vehicle_id)

    query = query.order_by(Schedule.created_at.desc())
    result = await session.execute(query.offset(skip).limit(limit))
    schedules = result.scalars().all()
    return schedules


@router.post("/schedules", response_model=ScheduleRead)
async def create_schedule(
    schedule: ScheduleCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建调度记录 / Create schedule record"""
    # 获取所有泊位用于分配
    result = await session.execute(select(Berth))
    berths = result.scalars().all()
    dispatch_service = SmartDispatchService(berths)

    # 获取车辆信息
    vehicle = await session.get(Vehicle, schedule.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # 使用调度服务处理
    new_schedule = dispatch_service.schedule_arrival(
        vehicle=vehicle,
        expected_waste_type=schedule.expected_waste_type,
        expected_weight=schedule.expected_weight,
        appointment_time=schedule.appointment_time
    )

    # 保存到数据库
    db_schedule = Schedule(
        vehicle_id=new_schedule.vehicle_id,
        berth_id=new_schedule.berth_id,
        appointment_time=new_schedule.appointment_time,
        expected_waste_type=new_schedule.expected_waste_type,
        expected_weight=new_schedule.expected_weight,
        status=new_schedule.status,
        queue_number=new_schedule.queue_number,
        queue_entered_at=new_schedule.queue_entered_at,
        checked_in_at=new_schedule.checked_in_at,
    )
    session.add(db_schedule)
    await session.commit()
    await session.refresh(db_schedule)

    return db_schedule


@router.get("/schedules/{schedule_id}", response_model=ScheduleRead)
async def get_schedule(schedule_id: int, session: AsyncSession = Depends(get_session)):
    """获取调度详情 / Get schedule details"""
    schedule = await session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.post("/schedules/{schedule_id}/checkin")
async def check_in_vehicle(
    schedule_id: int,
    session: AsyncSession = Depends(get_session)
):
    """车辆签到 / Vehicle check-in"""
    schedule = await session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.status = ScheduleStatus.CHECKED_IN
    schedule.checked_in_at = datetime.now()

    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)

    return {"message": "Check-in successful", "schedule": schedule}


@router.post("/schedules/{schedule_id}/start-unloading")
async def start_unloading(
    schedule_id: int,
    session: AsyncSession = Depends(get_session)
):
    """开始卸货 / Start unloading"""
    schedule = await session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if schedule.status != ScheduleStatus.CHECKED_IN:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start unloading from status: {schedule.status}"
        )

    schedule.status = ScheduleStatus.UNLOADING
    schedule.unloading_started_at = datetime.now()

    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)

    return {"message": "Unloading started", "schedule": schedule}


@router.post("/schedules/{schedule_id}/complete")
async def complete_schedule(
    schedule_id: int,
    gross_weight: float,
    tare_weight: float,
    session: AsyncSession = Depends(get_session)
):
    """完成调度 / Complete schedule"""
    schedule = await session.get(Schedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if schedule.status != ScheduleStatus.UNLOADING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete from status: {schedule.status}"
        )

    # 更新重量数据
    schedule.gross_weight = gross_weight
    schedule.tare_weight = tare_weight
    schedule.net_weight = gross_weight - tare_weight
    schedule.status = ScheduleStatus.COMPLETED
    schedule.unloading_completed_at = datetime.now()
    schedule.completed_at = datetime.now()

    # 释放泊位
    if schedule.berth_id:
        berth = await session.get(Berth, schedule.berth_id)
        if berth:
            berth.status = BerthStatus.AVAILABLE
            berth.current_vehicle_id = None
            session.add(berth)

    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)

    return {
        "message": "Schedule completed",
        "schedule": schedule,
        "net_weight": schedule.net_weight
    }


# ============== 队列与优化 / Queue & Optimization ==============

@router.get("/queue/status")
async def get_queue_status(session: AsyncSession = Depends(get_session)):
    """获取队列状态 / Get queue status"""
    # 统计各状态调度
    queued_result = await session.execute(
        select(Schedule).where(Schedule.status == ScheduleStatus.QUEUED)
    )
    queued_count = queued_result.scalars().all()

    checked_in_result = await session.execute(
        select(Schedule).where(Schedule.status == ScheduleStatus.CHECKED_IN)
    )
    checked_in_count = checked_in_result.scalars().all()

    unloading_result = await session.execute(
        select(Schedule).where(Schedule.status == ScheduleStatus.UNLOADING)
    )
    unloading_count = unloading_result.scalars().all()

    avg_wait_minutes = len(queued_count) * 15

    return {
        "queued": len(queued_count),
        "checked_in": len(checked_in_count),
        "unloading": len(unloading_count),
        "estimated_avg_wait_minutes": avg_wait_minutes,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/recommendations")
async def get_dispatch_recommendations(
    session: AsyncSession = Depends(get_session)
):
    """获取调度建议 / Get dispatch recommendations"""
    # 获取待处理调度
    result = await session.execute(
        select(Schedule).where(
            Schedule.status.in_([
                ScheduleStatus.QUEUED,
                ScheduleStatus.CHECKED_IN
            ])
        )
    )
    pending = result.scalars().all()

    # 获取所有车辆
    vehicles_result = await session.execute(select(Vehicle))
    vehicles = vehicles_result.scalars().all()

    # 获取泊位
    berths_result = await session.execute(select(Berth))
    berths = berths_result.scalars().all()

    # 生成建议
    service = SmartDispatchService(berths)
    recommendations = service.optimizer.generate_recommendations(pending, vehicles)

    return {
        "recommendations": [
            {
                "vehicle_id": r.vehicle_id,
                "recommended_berth_id": r.recommended_berth_id,
                "estimated_wait_minutes": r.estimated_wait_minutes,
                "priority_score": r.priority_score,
                "reason": r.reason
            }
            for r in recommendations[:10]
        ],
        "generated_at": datetime.now().isoformat()
    }


@router.post("/queue/process")
async def process_queue(session: AsyncSession = Depends(get_session)):
    """手动触发队列处理 / Manually trigger queue processing"""
    berths_result = await session.execute(select(Berth))
    berths = berths_result.scalars().all()
    service = SmartDispatchService(berths)

    # 处理队列
    processed = service.process_queue()

    # 保存到数据库
    for schedule in processed:
        db_schedule = await session.get(Schedule, schedule.id)
        if db_schedule:
            db_schedule.berth_id = schedule.berth_id
            db_schedule.status = schedule.status
            session.add(db_schedule)

    await session.commit()

    return {
        "processed_count": len(processed),
        "processed_schedules": [s.id for s in processed]
    }
