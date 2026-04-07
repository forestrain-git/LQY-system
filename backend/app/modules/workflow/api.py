"""
工单模块API路由 / Workflow Module API Routes

提供工单、任务、人员、部门的RESTful接口
Provides RESTful APIs for work orders, tasks, staff, and departments

Author: AI Sprint
Date: 2026-04-07
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlmodel import select

from app.database import get_session
from app.modules.workflow.models import (
    Staff, StaffCreate, StaffRead, StaffUpdate,
    Department, DepartmentCreate, DepartmentRead,
    WorkOrder, WorkOrderCreate, WorkOrderRead, WorkOrderUpdate,
    WorkOrderStatus, WorkOrderPriority, WorkOrderType,
    WorkOrderTask, TaskCreate, TaskRead, TaskStatus
)

router = APIRouter(prefix="/workflow", tags=["workflow"])


# ============== 部门管理 / Department Management ==============

@router.get("/departments", response_model=List[DepartmentRead])
async def list_departments(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """获取部门列表 / Get department list"""
    result = await session.execute(select(Department).offset(skip).limit(limit))
    departments = result.scalars().all()
    return departments


@router.post("/departments", response_model=DepartmentRead)
async def create_department(
    department: DepartmentCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建部门 / Create department"""
    db_department = Department.model_validate(department)
    session.add(db_department)
    await session.commit()
    await session.refresh(db_department)
    return db_department


@router.get("/departments/{department_id}", response_model=DepartmentRead)
async def get_department(department_id: int, session: AsyncSession = Depends(get_session)):
    """获取部门详情 / Get department details"""
    department = await session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


# ============== 人员管理 / Staff Management ==============

@router.get("/staff", response_model=List[StaffRead])
async def list_staff(
    status: Optional[str] = None,
    department_id: Optional[int] = None,
    role: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """获取人员列表 / Get staff list"""
    query = select(Staff)
    if status:
        query = query.where(Staff.status == status)
    if department_id:
        query = query.where(Staff.department_id == department_id)
    if role:
        query = query.where(Staff.role == role)

    result = await session.execute(query.offset(skip).limit(limit))
    staff_list = result.scalars().all()
    return staff_list


@router.post("/staff", response_model=StaffRead)
async def create_staff(
    staff: StaffCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建人员 / Create staff"""
    db_staff = Staff.model_validate(staff)
    session.add(db_staff)
    await session.commit()
    await session.refresh(db_staff)
    return db_staff


@router.get("/staff/{staff_id}", response_model=StaffRead)
async def get_staff(staff_id: int, session: AsyncSession = Depends(get_session)):
    """获取人员详情 / Get staff details"""
    staff = await session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff


@router.patch("/staff/{staff_id}", response_model=StaffRead)
async def update_staff(
    staff_id: int,
    staff_update: StaffUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新人员信息 / Update staff"""
    staff = await session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    update_data = staff_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(staff, key, value)

    staff.updated_at = datetime.now()
    session.add(staff)
    await session.commit()
    await session.refresh(staff)
    return staff


@router.get("/staff/{staff_id}/location")
async def get_staff_location(staff_id: int, session: AsyncSession = Depends(get_session)):
    """获取人员实时位置 / Get staff real-time location"""
    staff = await session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    return {
        "staff_id": staff_id,
        "name": staff.name,
        "gps_latitude": staff.gps_latitude,
        "gps_longitude": staff.gps_longitude,
        "gps_updated_at": staff.gps_updated_at.isoformat() if staff.gps_updated_at else None,
    }


@router.post("/staff/{staff_id}/location")
async def update_staff_location(
    staff_id: int,
    latitude: float,
    longitude: float,
    session: AsyncSession = Depends(get_session)
):
    """更新人员位置 / Update staff location"""
    staff = await session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    staff.gps_latitude = latitude
    staff.gps_longitude = longitude
    staff.gps_updated_at = datetime.now()

    session.add(staff)
    await session.commit()
    await session.refresh(staff)
    return {"message": "Location updated", "staff": staff}


# ============== 工单管理 / Work Order Management ==============

@router.get("/work-orders", response_model=List[WorkOrderRead])
async def list_work_orders(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    order_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """获取工单列表 / Get work order list"""
    query = select(WorkOrder)
    if status:
        query = query.where(WorkOrder.status == status)
    if priority:
        query = query.where(WorkOrder.priority == priority)
    if order_type:
        query = query.where(WorkOrder.order_type == order_type)
    if assignee_id:
        query = query.where(WorkOrder.assignee_id == assignee_id)

    query = query.order_by(WorkOrder.created_at.desc())
    result = await session.execute(query.offset(skip).limit(limit))
    orders = result.scalars().all()
    return orders


@router.post("/work-orders", response_model=WorkOrderRead)
async def create_work_order(
    order: WorkOrderCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建工单 / Create work order"""
    # 生成工单编号 (含UUID防止并发冲突) / Generate order number with UUID
    order_no = f"WO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

    db_order = WorkOrder(
        order_no=order_no,
        order_type=order.order_type,
        title=order.title,
        description=order.description,
        priority=order.priority,
        equipment_id=order.equipment_id,
        vehicle_id=order.vehicle_id,
        creator_id=order.creator_id,
        assignee_id=order.assignee_id,
        planned_start=order.planned_start,
        planned_end=order.planned_end,
        status=WorkOrderStatus.PENDING,
    )

    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)
    return db_order


@router.get("/work-orders/{order_id}", response_model=WorkOrderRead)
async def get_work_order(order_id: int, session: AsyncSession = Depends(get_session)):
    """获取工单详情 / Get work order details"""
    order = await session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return order


@router.patch("/work-orders/{order_id}", response_model=WorkOrderRead)
async def update_work_order(
    order_id: int,
    order_update: WorkOrderUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新工单信息 / Update work order"""
    order = await session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)

    order.updated_at = datetime.now()
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


@router.post("/work-orders/{order_id}/assign")
async def assign_work_order(
    order_id: int,
    assignee_id: int,
    session: AsyncSession = Depends(get_session)
):
    """分配工单 / Assign work order"""
    order = await session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    assignee = await session.get(Staff, assignee_id)
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee not found")

    order.assignee_id = assignee_id
    order.status = WorkOrderStatus.ASSIGNED
    order.updated_at = datetime.now()

    session.add(order)
    await session.commit()
    await session.refresh(order)
    return {"message": "Work order assigned", "order": order}


@router.post("/work-orders/{order_id}/start")
async def start_work_order(
    order_id: int,
    session: AsyncSession = Depends(get_session)
):
    """开始工单 / Start work order"""
    order = await session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    if order.status not in [WorkOrderStatus.PENDING, WorkOrderStatus.ASSIGNED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start from status: {order.status}"
        )

    order.status = WorkOrderStatus.IN_PROGRESS
    order.actual_start = datetime.now()
    order.updated_at = datetime.now()

    session.add(order)
    await session.commit()
    await session.refresh(order)
    return {"message": "Work order started", "order": order}


@router.post("/work-orders/{order_id}/complete")
async def complete_work_order(
    order_id: int,
    result_summary: Optional[str] = None,
    satisfaction: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    """完成工单 / Complete work order"""
    order = await session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    if order.status != WorkOrderStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete from status: {order.status}"
        )

    order.status = WorkOrderStatus.COMPLETED
    order.actual_end = datetime.now()
    order.result_summary = result_summary
    order.satisfaction = satisfaction
    order.updated_at = datetime.now()

    session.add(order)
    await session.commit()
    await session.refresh(order)
    return {"message": "Work order completed", "order": order}


@router.post("/work-orders/{order_id}/cancel")
async def cancel_work_order(
    order_id: int,
    reason: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """取消工单 / Cancel work order"""
    order = await session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    if order.status in [WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel completed or closed order"
        )

    order.status = WorkOrderStatus.CANCELLED
    order.result_summary = reason or "Cancelled"
    order.updated_at = datetime.now()

    session.add(order)
    await session.commit()
    await session.refresh(order)
    return {"message": "Work order cancelled", "order": order}


# ============== 工单统计 / Work Order Statistics ==============

@router.get("/work-orders/stats/overview")
async def get_work_order_stats(session: AsyncSession = Depends(get_session)):
    """获取工单统计概览 / Get work order statistics overview"""
    # 使用聚合查询优化性能 / Use aggregation for better performance
    stats = {}

    # 状态统计 / Status counts
    status_result = await session.execute(
        select(WorkOrder.status, func.count(WorkOrder.id)).group_by(WorkOrder.status)
    )
    stats["by_status"] = {row[0].value: row[1] for row in status_result.all()}

    # 优先级统计 / Priority counts
    priority_result = await session.execute(
        select(WorkOrder.priority, func.count(WorkOrder.id)).group_by(WorkOrder.priority)
    )
    stats["by_priority"] = {row[0].value: row[1] for row in priority_result.all()}

    # 类型统计 / Type counts
    type_result = await session.execute(
        select(WorkOrder.order_type, func.count(WorkOrder.id)).group_by(WorkOrder.order_type)
    )
    stats["by_type"] = {row[0].value: row[1] for row in type_result.all()}

    stats["total"] = sum(stats["by_status"].values())
    return stats


# ============== 任务管理 / Task Management ==============

@router.get("/work-orders/{order_id}/tasks", response_model=List[TaskRead])
async def list_work_order_tasks(
    order_id: int,
    session: AsyncSession = Depends(get_session)
):
    """获取工单任务列表 / Get work order task list"""
    order = await session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    result = await session.execute(
        select(WorkOrderTask).where(WorkOrderTask.work_order_id == order_id)
    )
    tasks = result.scalars().all()
    return tasks


@router.post("/work-orders/{order_id}/tasks", response_model=TaskRead)
async def create_task(
    order_id: int,
    task: TaskCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建工单任务 / Create work order task"""
    order = await session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    # 获取当前最大任务序号 / Get current max task number
    result = await session.execute(
        select(WorkOrderTask).where(WorkOrderTask.work_order_id == order_id)
    )
    existing_tasks = result.scalars().all()
    next_task_no = len(existing_tasks) + 1

    db_task = WorkOrderTask(
        work_order_id=order_id,
        task_no=next_task_no,
        description=task.description,
        assignee_id=task.assignee_id,
        standard_time_minutes=task.standard_time_minutes,
        status=TaskStatus.PENDING,
    )

    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task


@router.patch("/work-orders/{order_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    order_id: int,
    task_id: int,
    status: Optional[str] = None,
    actual_time_minutes: Optional[int] = None,
    result_notes: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """更新任务状态 / Update task status"""
    task = await session.get(WorkOrderTask, task_id)
    if not task or task.work_order_id != order_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if status:
        task.status = status
    if actual_time_minutes:
        task.actual_time_minutes = actual_time_minutes
    if result_notes:
        task.result_notes = result_notes

    task.updated_at = datetime.now()
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
