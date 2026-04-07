"""
设备模块API路由 / Equipment Module API Routes

Author: AI Sprint
Date: 2026-04-07
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlmodel import select

from app.database import get_session
from app.modules.equipment.models import (
    Equipment, EquipmentCreate, EquipmentRead, EquipmentUpdate,
    EquipmentStatus, EquipmentType,
    MaintenanceRecord, MaintenanceCreate, MaintenanceRead,
    MaintenanceStatus, MaintenanceType
)

router = APIRouter(prefix="/equipment", tags=["equipment"])


# ============== 设备管理 / Equipment Management ==============

@router.get("", response_model=List[EquipmentRead])
async def list_equipment(
    status: Optional[str] = None,
    equipment_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """获取设备列表 / Get equipment list"""
    query = select(Equipment)
    if status:
        query = query.where(Equipment.status == status)
    if equipment_type:
        query = query.where(Equipment.equipment_type == equipment_type)

    query = query.order_by(Equipment.created_at.desc())
    result = await session.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@router.post("", response_model=EquipmentRead)
async def create_equipment(
    equipment: EquipmentCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建设备 / Create equipment"""
    db_equipment = Equipment.model_validate(equipment)

    # 计算下次维护时间 (3个月后) / Calculate next maintenance (3 months later)
    db_equipment.next_maintenance_at = datetime.now() + timedelta(days=90)

    session.add(db_equipment)
    await session.commit()
    await session.refresh(db_equipment)
    return db_equipment


@router.get("/{equipment_id}", response_model=EquipmentRead)
async def get_equipment(equipment_id: int, session: AsyncSession = Depends(get_session)):
    """获取设备详情 / Get equipment details"""
    equipment = await session.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.patch("/{equipment_id}", response_model=EquipmentRead)
async def update_equipment(
    equipment_id: int,
    equipment_update: EquipmentUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新设备信息 / Update equipment"""
    equipment = await session.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    update_data = equipment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(equipment, key, value)

    equipment.updated_at = datetime.now()
    session.add(equipment)
    await session.commit()
    await session.refresh(equipment)
    return equipment


@router.post("/{equipment_id}/status")
async def update_equipment_status(
    equipment_id: int,
    status: EquipmentStatus,
    session: AsyncSession = Depends(get_session)
):
    """更新设备状态 / Update equipment status"""
    equipment = await session.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    equipment.status = status
    equipment.updated_at = datetime.now()

    session.add(equipment)
    await session.commit()
    await session.refresh(equipment)
    return {"message": "Status updated", "equipment": equipment}


# ============== 设备统计 / Equipment Statistics ==============

@router.get("/stats/overview")
async def get_equipment_stats(session: AsyncSession = Depends(get_session)):
    """获取设备统计概览 / Get equipment statistics"""
    # 状态统计
    status_result = await session.execute(
        select(Equipment.status, func.count(Equipment.id)).group_by(Equipment.status)
    )
    by_status = {row[0].value: row[1] for row in status_result.all()}

    # 类型统计
    type_result = await session.execute(
        select(Equipment.equipment_type, func.count(Equipment.id)).group_by(Equipment.equipment_type)
    )
    by_type = {row[0].value: row[1] for row in type_result.all()}

    # 即将过保修期的设备
    warranty_warning = await session.execute(
        select(Equipment).where(
            Equipment.warranty_until < datetime.now() + timedelta(days=30),
            Equipment.status != EquipmentStatus.DECOMMISSIONED
        )
    )
    warranty_count = len(warranty_warning.scalars().all())

    # 需要维护的设备
    maintenance_due = await session.execute(
        select(Equipment).where(
            Equipment.next_maintenance_at < datetime.now() + timedelta(days=7),
            Equipment.status == EquipmentStatus.NORMAL
        )
    )
    maintenance_count = len(maintenance_due.scalars().all())

    return {
        "by_status": by_status,
        "by_type": by_type,
        "total": sum(by_status.values()),
        "warranty_warning": warranty_count,
        "maintenance_due": maintenance_count
    }


# ============== 维保记录 / Maintenance Records ==============

@router.get("/{equipment_id}/maintenance", response_model=List[MaintenanceRead])
async def list_maintenance_records(
    equipment_id: int,
    session: AsyncSession = Depends(get_session)
):
    """获取设备维保记录 / Get equipment maintenance records"""
    equipment = await session.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    result = await session.execute(
        select(MaintenanceRecord)
        .where(MaintenanceRecord.equipment_id == equipment_id)
        .order_by(MaintenanceRecord.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{equipment_id}/maintenance", response_model=MaintenanceRead)
async def create_maintenance_record(
    equipment_id: int,
    maintenance: MaintenanceCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建维保记录 / Create maintenance record"""
    equipment = await session.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # 生成维保单号
    record_no = f"MR{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

    db_record = MaintenanceRecord(
        equipment_id=equipment_id,
        record_no=record_no,
        maintenance_type=maintenance.maintenance_type,
        title=maintenance.title,
        description=maintenance.description,
        technician_id=maintenance.technician_id,
        planned_date=maintenance.planned_date,
        status=MaintenanceStatus.SCHEDULED
    )

    session.add(db_record)
    await session.commit()
    await session.refresh(db_record)
    return db_record


@router.post("/{equipment_id}/maintenance/{record_id}/start")
async def start_maintenance(
    equipment_id: int,
    record_id: int,
    session: AsyncSession = Depends(get_session)
):
    """开始维保 / Start maintenance"""
    record = await session.get(MaintenanceRecord, record_id)
    if not record or record.equipment_id != equipment_id:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    record.status = MaintenanceStatus.IN_PROGRESS
    record.started_at = datetime.now()

    # 更新设备状态
    equipment = await session.get(Equipment, equipment_id)
    equipment.status = EquipmentStatus.MAINTENANCE
    equipment.updated_at = datetime.now()

    session.add(record)
    session.add(equipment)
    await session.commit()
    await session.refresh(record)
    return {"message": "Maintenance started", "record": record}


@router.post("/{equipment_id}/maintenance/{record_id}/complete")
async def complete_maintenance(
    equipment_id: int,
    record_id: int,
    result_notes: Optional[str] = None,
    labor_hours: Optional[float] = None,
    cost: Optional[float] = None,
    session: AsyncSession = Depends(get_session)
):
    """完成维保 / Complete maintenance"""
    record = await session.get(MaintenanceRecord, record_id)
    if not record or record.equipment_id != equipment_id:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    record.status = MaintenanceStatus.COMPLETED
    record.completed_at = datetime.now()
    record.result_notes = result_notes
    record.labor_hours = labor_hours
    record.cost = cost

    # 更新设备维护信息
    equipment = await session.get(Equipment, equipment_id)
    equipment.status = EquipmentStatus.NORMAL
    equipment.last_maintenance_at = datetime.now()
    equipment.next_maintenance_at = datetime.now() + timedelta(days=90)  # 3个月后
    equipment.total_operating_hours += labor_hours or 0
    equipment.updated_at = datetime.now()

    session.add(record)
    session.add(equipment)
    await session.commit()
    await session.refresh(record)
    return {"message": "Maintenance completed", "record": record}


# ============== 维护计划 / Maintenance Planning ==============

@router.get("/maintenance/planned")
async def get_planned_maintenance(
    days: int = 30,
    session: AsyncSession = Depends(get_session)
):
    """获取计划维护列表 / Get planned maintenance list"""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=days)

    result = await session.execute(
        select(MaintenanceRecord)
        .where(
            MaintenanceRecord.planned_date.between(start_date, end_date),
            MaintenanceRecord.status.in_([MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS])
        )
        .order_by(MaintenanceRecord.planned_date)
    )
    return result.scalars().all()
