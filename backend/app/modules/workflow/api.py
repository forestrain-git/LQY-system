"""
工单模块API路由 / Workflow Module API Routes

提供工单、任务、人员、部门的RESTful接口
Provides RESTful APIs for work orders, tasks, staff, and departments

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.db import get_session
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
def list_departments(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """获取部门列表 / Get department list"""
    departments = session.exec(select(Department).offset(skip).limit(limit)).all()
    return departments


@router.post("/departments", response_model=DepartmentRead)
def create_department(
    department: DepartmentCreate,
    session: Session = Depends(get_session)
):
    """创建部门 / Create department"""
    db_department = Department.model_validate(department)
    session.add(db_department)
    session.commit()
    session.refresh(db_department)
    return db_department


@router.get("/departments/{department_id}", response_model=DepartmentRead)
def get_department(department_id: int, session: Session = Depends(get_session)):
    """获取部门详情 / Get department details"""
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


# ============== 人员管理 / Staff Management ==============

@router.get("/staff", response_model=List[StaffRead])
def list_staff(
    status: Optional[str] = None,
    department_id: Optional[int] = None,
    role: Optional[str] = None,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """
    获取人员列表 / Get staff list

    Args:
        status: 按状态过滤 / Filter by status
        department_id: 按部门过滤 / Filter by department
        role: 按角色过滤 / Filter by role
    """
    query = select(Staff)
    if status:
        query = query.where(Staff.status == status)
    if department_id:
        query = query.where(Staff.department_id == department_id)
    if role:
        query = query.where(Staff.role == role)

    staff_list = session.exec(query.offset(skip).limit(limit)).all()
    return staff_list


@router.post("/staff", response_model=StaffRead)
def create_staff(
    staff: StaffCreate,
    session: Session = Depends(get_session)
):
    """创建人员 / Create staff"""
    db_staff = Staff.model_validate(staff)
    session.add(db_staff)
    session.commit()
    session.refresh(db_staff)
    return db_staff


@router.get("/staff/{staff_id}", response_model=StaffRead)
def get_staff(staff_id: int, session: Session = Depends(get_session)):
    """获取人员详情 / Get staff details"""
    staff = session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff


@router.patch("/staff/{staff_id}", response_model=StaffRead)
def update_staff(
    staff_id: int,
    staff_update: StaffUpdate,
    session: Session = Depends(get_session)
):
    """更新人员信息 / Update staff"""
    staff = session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    update_data = staff_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(staff, key, value)

    staff.updated_at = datetime.now()
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return staff


@router.get("/staff/{staff_id}/location")
def get_staff_location(staff_id: int, session: Session = Depends(get_session)):
    """
    获取人员实时位置 / Get staff real-time location

    返回GPS坐标和最后更新时间
    Returns GPS coordinates and last update time
    """
    staff = session.get(Staff, staff_id)
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
def update_staff_location(
    staff_id: int,
    latitude: float,
    longitude: float,
    session: Session = Depends(get_session)
):
    """更新人员位置 / Update staff location"""
    staff = session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    staff.gps_latitude = latitude
    staff.gps_longitude = longitude
    staff.gps_updated_at = datetime.now()

    session.add(staff)
    session.commit()
    session.refresh(staff)

    return {"message": "Location updated", "staff": staff}


# ============== 工单管理 / Work Order Management ==============

@router.get("/work-orders", response_model=List[WorkOrderRead])
def list_work_orders(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    order_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """
    获取工单列表 / Get work order list

    Args:
        status: 按状态过滤 / Filter by status
        priority: 按优先级过滤 / Filter by priority
        order_type: 按类型过滤 / Filter by type
        assignee_id: 按执行人过滤 / Filter by assignee
    """
    query = select(WorkOrder)
    if status:
        query = query.where(WorkOrder.status == status)
    if priority:
        query = query.where(WorkOrder.priority == priority)
    if order_type:
        query = query.where(WorkOrder.order_type == order_type)
    if assignee_id:
        query = query.where(WorkOrder.assignee_id == assignee_id)

    # 按创建时间倒序 / Descending by creation time
    query = query.order_by(WorkOrder.created_at.desc())

    orders = session.exec(query.offset(skip).limit(limit)).all()
    return orders


@router.post("/work-orders", response_model=WorkOrderRead)
def create_work_order(
    order: WorkOrderCreate,
    session: Session = Depends(get_session)
):
    """
    创建工单 / Create work order

    自动生成工单编号，初始状态为待处理
    Auto-generates order number, initial status is pending
    """
    # 生成工单编号 / Generate order number
    order_no = f"WO{datetime.now().strftime('%Y%m%d%H%M%S')}"

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
    session.commit()
    session.refresh(db_order)
    return db_order


@router.get("/work-orders/{order_id}", response_model=WorkOrderRead)
def get_work_order(order_id: int, session: Session = Depends(get_session)):
    """获取工单详情 / Get work order details"""
    order = session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return order


@router.patch("/work-orders/{order_id}", response_model=WorkOrderRead)
def update_work_order(
    order_id: int,
    order_update: WorkOrderUpdate,
    session: Session = Depends(get_session)
):
    """更新工单信息 / Update work order"""
    order = session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)

    order.updated_at = datetime.now()
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.post("/work-orders/{order_id}/assign")
def assign_work_order(
    order_id: int,
    assignee_id: int,
    session: Session = Depends(get_session)
):
    """
    分配工单 / Assign work order

    将工单分配给指定执行人
    Assigns work order to specified assignee
    """
    order = session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    assignee = session.get(Staff, assignee_id)
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee not found")

    order.assignee_id = assignee_id
    order.status = WorkOrderStatus.ASSIGNED
    order.updated_at = datetime.now()

    session.add(order)
    session.commit()
    session.refresh(order)

    return {"message": "Work order assigned", "order": order}


@router.post("/work-orders/{order_id}/start")
def start_work_order(
    order_id: int,
    session: Session = Depends(get_session)
):
    """开始工单 / Start work order"""
    order = session.get(WorkOrder, order_id)
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
    session.commit()
    session.refresh(order)

    return {"message": "Work order started", "order": order}


@router.post("/work-orders/{order_id}/complete")
def complete_work_order(
    order_id: int,
    result_summary: Optional[str] = None,
    satisfaction: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """
    完成工单 / Complete work order

    Args:
        result_summary: 处理结果摘要 / Result summary
        satisfaction: 满意度评分(1-5) / Satisfaction rating
    """
    order = session.get(WorkOrder, order_id)
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
    session.commit()
    session.refresh(order)

    return {"message": "Work order completed", "order": order}


@router.post("/work-orders/{order_id}/cancel")
def cancel_work_order(
    order_id: int,
    reason: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """取消工单 / Cancel work order"""
    order = session.get(WorkOrder, order_id)
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
    session.commit()
    session.refresh(order)

    return {"message": "Work order cancelled", "order": order}


# ============== 工单统计 / Work Order Statistics ==============

@router.get("/work-orders/stats/overview")
def get_work_order_stats(session: Session = Depends(get_session)):
    """
    获取工单统计概览 / Get work order statistics overview
    """
    # 各状态数量 / Count by status
    status_counts = {}
    for status in WorkOrderStatus:
        count = session.exec(
            select(WorkOrder).where(WorkOrder.status == status)
        ).all()
        status_counts[status.value] = len(count)

    # 各优先级数量 / Count by priority
    priority_counts = {}
    for priority in WorkOrderPriority:
        count = session.exec(
            select(WorkOrder).where(WorkOrder.priority == priority)
        ).all()
        priority_counts[priority.value] = len(count)

    # 各类型数量 / Count by type
    type_counts = {}
    for order_type in WorkOrderType:
        count = session.exec(
            select(WorkOrder).where(WorkOrder.order_type == order_type)
        ).all()
        type_counts[order_type.value] = len(count)

    return {
        "by_status": status_counts,
        "by_priority": priority_counts,
        "by_type": type_counts,
        "total": sum(status_counts.values()),
    }


# ============== 任务管理 / Task Management ==============

@router.get("/work-orders/{order_id}/tasks", response_model=List[TaskRead])
def list_work_order_tasks(
    order_id: int,
    session: Session = Depends(get_session)
):
    """获取工单任务列表 / Get work order task list"""
    order = session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    tasks = session.exec(
        select(WorkOrderTask).where(WorkOrderTask.work_order_id == order_id)
    ).all()
    return tasks


@router.post("/work-orders/{order_id}/tasks", response_model=TaskRead)
def create_task(
    order_id: int,
    task: TaskCreate,
    session: Session = Depends(get_session)
):
    """创建工单任务 / Create work order task"""
    order = session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    # 获取当前最大任务序号 / Get current max task number
    existing_tasks = session.exec(
        select(WorkOrderTask).where(WorkOrderTask.work_order_id == order_id)
    ).all()
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
    session.commit()
    session.refresh(db_task)
    return db_task


@router.patch("/work-orders/{order_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    order_id: int,
    task_id: int,
    status: Optional[str] = None,
    actual_time_minutes: Optional[int] = None,
    result_notes: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """更新任务状态 / Update task status"""
    task = session.get(WorkOrderTask, task_id)
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
    session.commit()
    session.refresh(task)
    return task
