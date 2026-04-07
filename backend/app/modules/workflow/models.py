"""
工单模块数据模型 / Workflow Module Data Models

包含工单、任务、人员、部门相关的数据模型
Includes data models for work orders, tasks, staff, and departments

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, Text
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.dispatch.models import Vehicle


# ============== 枚举类型 / Enums ==============

class WorkOrderType(str, Enum):
    """
    工单类型 / Work Order Type

    不同类型的维护作业
    Different types of maintenance operations
    """
    INSPECTION = "inspection"       # 巡检 / Inspection
    MAINTENANCE = "maintenance"     # 保养 / Maintenance
    REPAIR = "repair"               # 维修 / Repair
    EMERGENCY = "emergency"         # 紧急抢修 / Emergency repair
    CLEANING = "cleaning"           # 清洁 / Cleaning
    SAFETY = "safety"               # 安全检查 / Safety check


class WorkOrderStatus(str, Enum):
    """
    工单状态 / Work Order Status

    工单生命周期状态流转
    Work order lifecycle status flow
    """
    PENDING = "pending"             # 待处理 / Pending
    ASSIGNED = "assigned"           # 已分派 / Assigned
    IN_PROGRESS = "in_progress"     # 进行中 / In progress
    PAUSED = "paused"               # 已暂停 / Paused
    COMPLETED = "completed"         # 已完成 / Completed
    VERIFIED = "verified"           # 已验收 / Verified
    CLOSED = "closed"               # 已关闭 / Closed
    CANCELLED = "cancelled"         # 已取消 / Cancelled


class WorkOrderPriority(str, Enum):
    """
    工单优先级 / Work Order Priority
    """
    LOW = "low"                     # 低 / Low
    MEDIUM = "medium"               # 中 / Medium
    HIGH = "high"                   # 高 / High
    URGENT = "urgent"               # 紧急 / Urgent


class TaskStatus(str, Enum):
    """
    任务状态 / Task Status
    """
    PENDING = "pending"             # 待执行 / Pending
    IN_PROGRESS = "in_progress"     # 执行中 / In progress
    COMPLETED = "completed"         # 已完成 / Completed
    SKIPPED = "skipped"             # 已跳过 / Skipped


class StaffRole(str, Enum):
    """
    人员角色 / Staff Role

    环卫站工种分类
    Job classification for sanitation station
    """
    DRIVER = "driver"               # 司机 / Driver
    OPERATOR = "operator"           # 操作工 / Operator
    MAINTENANCE = "maintenance"     # 维修工 / Maintenance worker
    CLEANER = "cleaner"             # 保洁员 / Cleaner
    SAFETY_OFFICER = "safety_officer"  # 安全员 / Safety officer
    MANAGER = "manager"             # 管理员 / Manager
    INSPECTOR = "inspector"         # 巡检员 / Inspector


class StaffStatus(str, Enum):
    """
    人员状态 / Staff Status
    """
    ACTIVE = "active"               # 在职 / Active
    ON_LEAVE = "on_leave"           # 休假 / On leave
    SUSPENDED = "suspended"         # 暂停 / Suspended
    RESIGNED = "resigned"           # 离职 / Resigned


# ============== 部门模型 / Department Model ==============

class Department(SQLModel, table=True):
    """
    部门模型 / Department Model

    组织架构中的部门/班组
    Department/team in organizational structure
    """

    __tablename__ = "departments"

    id: int | None = Field(default=None, primary_key=True)

    # 基本信息 / Basic Information
    code: str = Field(
        ...,
        max_length=20,
        sa_column=Column(String(20), unique=True, nullable=False),
        description="部门编号 / Department code",
    )
    name: str = Field(
        ...,
        max_length=50,
        sa_column=Column(String(50), nullable=False),
        description="部门名称 / Department name",
    )
    description: str | None = Field(
        default=None,
        sa_column=Column(String(200)),
        description="部门描述 / Department description",
    )

    # 层级 / Hierarchy
    parent_id: int | None = Field(
        default=None,
        foreign_key="departments.id",
        description="上级部门ID / Parent department ID",
    )

    # 时间戳 / Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="创建时间 / Creation time",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="更新时间 / Update time",
    )

    # 关联关系 / Relationships
    staff: List["Staff"] = Relationship(
        back_populates="department",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def __repr__(self) -> str:
        return f"<Department: {self.name}>"


# ============== 人员模型 / Staff Model ==============

class Staff(SQLModel, table=True):
    """
    人员模型 / Staff Model

    表示一名员工/工作人员
    Represents an employee/staff member

    业务规则 / Business Rules:
    - 工号全局唯一 / Employee number is globally unique
    - 一人可属于多个工单 / One person can be assigned to multiple work orders
    - 支持GPS定位追踪 / Supports GPS location tracking
    """

    __tablename__ = "staff"

    id: int | None = Field(default=None, primary_key=True)

    # 基本信息 / Basic Information
    employee_no: str = Field(
        ...,
        max_length=20,
        sa_column=Column(String(20), unique=True, nullable=False, index=True),
        description="工号，全局唯一 / Employee number, globally unique",
    )
    name: str = Field(
        ...,
        max_length=50,
        sa_column=Column(String(50), nullable=False),
        description="姓名 / Name",
    )
    role: StaffRole = Field(
        default=StaffRole.OPERATOR,
        sa_column=Column(String(30), nullable=False),
        description="工种/角色 / Job role",
    )
    phone: str | None = Field(
        default=None,
        max_length=20,
        sa_column=Column(String(20)),
        description="联系电话 / Phone number",
    )
    email: str | None = Field(
        default=None,
        max_length=100,
        sa_column=Column(String(100)),
        description="邮箱 / Email",
    )

    # 所属部门 / Department
    department_id: int | None = Field(
        default=None,
        foreign_key="departments.id",
        description="所属部门ID / Department ID",
    )

    # GPS位置 / GPS Location
    gps_latitude: float | None = Field(
        default=None,
        description="GPS纬度 / GPS latitude",
    )
    gps_longitude: float | None = Field(
        default=None,
        description="GPS经度 / GPS longitude",
    )
    gps_updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="GPS更新时间 / GPS update time",
    )

    # 工牌信息 / Badge Information
    badge_id: str | None = Field(
        default=None,
        max_length=50,
        sa_column=Column(String(50), unique=True),
        description="工牌ID / Badge ID",
    )

    # 状态 / Status
    status: StaffStatus = Field(
        default=StaffStatus.ACTIVE,
        sa_column=Column(String(20), nullable=False, index=True),
        description="人员状态 / Staff status",
    )

    # 时间戳 / Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="创建时间 / Creation time",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="更新时间 / Update time",
    )

    # 关联关系 / Relationships
    department: Optional[Department] = Relationship(back_populates="staff")
    assigned_orders: List["WorkOrder"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "WorkOrder.assignee_id"},
    )
    created_orders: List["WorkOrder"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "WorkOrder.creator_id"},
    )
    tasks: List["WorkOrderTask"] = Relationship(
        back_populates="assignee",
    )

    def __repr__(self) -> str:
        return f"<Staff: {self.name} ({self.employee_no})>"

    class Config:
        json_schema_extra = {
            "example": {
                "employee_no": "EMP001",
                "name": "张三",
                "role": "operator",
                "status": "active",
            }
        }


# ============== 工单模型 / Work Order Model ==============

class WorkOrder(SQLModel, table=True):
    """
    工单模型 / Work Order Model

    表示一个维护/作业工单
    Represents a maintenance/operation work order

    业务规则 / Business Rules:
    - 工单编号全局唯一 / Work order number is globally unique
    - 状态按固定流程流转 / Status flows in fixed sequence
    - 支持关联设备和车辆 / Supports association with equipment and vehicles
    """

    __tablename__ = "work_orders"

    id: int | None = Field(default=None, primary_key=True)

    # 工单编号 / Work Order Number
    order_no: str = Field(
        ...,
        max_length=30,
        sa_column=Column(String(30), unique=True, nullable=False, index=True),
        description="工单编号，全局唯一 / Work order number, globally unique",
    )

    # 工单类型 / Work Order Type
    order_type: WorkOrderType = Field(
        default=WorkOrderType.INSPECTION,
        sa_column=Column(String(20), nullable=False),
        description="工单类型 / Work order type",
    )

    # 标题和描述 / Title and Description
    title: str = Field(
        ...,
        max_length=100,
        sa_column=Column(String(100), nullable=False),
        description="工单标题 / Work order title",
    )
    description: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="工单描述 / Work order description",
    )

    # 优先级 / Priority
    priority: WorkOrderPriority = Field(
        default=WorkOrderPriority.MEDIUM,
        sa_column=Column(String(20), nullable=False),
        description="优先级 / Priority",
    )

    # 关联设备 / Associated Equipment
    # 注意: 外键暂时禁用，等待设备模块完成后添加
    # Note: FK temporarily disabled until equipment module is ready
    equipment_id: int | None = Field(
        default=None,
        # foreign_key="devices.id",  # 暂时禁用 / Temporarily disabled
        description="关联设备ID / Associated equipment ID",
    )

    # 关联车辆 / Associated Vehicle
    vehicle_id: int | None = Field(
        default=None,
        foreign_key="vehicles.id",
        description="关联车辆ID / Associated vehicle ID",
    )

    # 人员 / Personnel
    creator_id: int = Field(
        ...,
        foreign_key="staff.id",
        nullable=False,
        description="创建人ID / Creator ID",
    )
    assignee_id: int | None = Field(
        default=None,
        foreign_key="staff.id",
        description="执行人ID / Assignee ID",
    )

    # 计划时间 / Planned Time
    planned_start: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="计划开始时间 / Planned start time",
    )
    planned_end: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="计划结束时间 / Planned end time",
    )

    # 实际时间 / Actual Time
    actual_start: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="实际开始时间 / Actual start time",
    )
    actual_end: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="实际结束时间 / Actual end time",
    )

    # 状态 / Status
    status: WorkOrderStatus = Field(
        default=WorkOrderStatus.PENDING,
        sa_column=Column(String(20), nullable=False, index=True),
        description="工单状态 / Work order status",
    )

    # 结果 / Result
    result_summary: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="处理结果 / Result summary",
    )
    satisfaction: int | None = Field(
        default=None,
        description="满意度评分(1-5) / Satisfaction rating (1-5)",
    )

    # 时间戳 / Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="创建时间 / Creation time",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="更新时间 / Update time",
    )

    # 关联关系 / Relationships
    # 注意: equipment 关系暂时禁用，等待设备模块完成后添加
    # Note: equipment relationship temporarily disabled
    # equipment: Optional["Device"] = Relationship(
    #     sa_relationship_kwargs={"foreign_keys": "WorkOrder.equipment_id"},
    # )
    vehicle: Optional["Vehicle"] = Relationship(
        back_populates="work_orders",
        sa_relationship_kwargs={"foreign_keys": "WorkOrder.vehicle_id"},
    )
    creator: "Staff" = Relationship(
        back_populates="created_orders",
        sa_relationship_kwargs={"foreign_keys": "WorkOrder.creator_id"},
    )
    assignee: Optional["Staff"] = Relationship(
        back_populates="assigned_orders",
        sa_relationship_kwargs={"foreign_keys": "WorkOrder.assignee_id"},
    )
    tasks: List["WorkOrderTask"] = Relationship(
        back_populates="work_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def __repr__(self) -> str:
        return f"<WorkOrder: {self.order_no} ({self.status.value})>"

    def calculate_duration(self) -> Optional[float]:
        """
        计算工单耗时(小时) / Calculate work order duration (hours)

        Returns:
            耗时(小时)或None / Duration in hours or None
        """
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return delta.total_seconds() / 3600
        return None

    class Config:
        json_schema_extra = {
            "example": {
                "order_no": "WO20260407001",
                "order_type": "inspection",
                "title": "压缩机日常巡检",
                "priority": "medium",
                "status": "pending",
            }
        }


# ============== 工单任务模型 / Work Order Task Model ==============

class WorkOrderTask(SQLModel, table=True):
    """
    工单任务模型 / Work Order Task Model

    表示一个工单中的具体任务项
    Represents a specific task item within a work order
    """

    __tablename__ = "work_order_tasks"

    id: int | None = Field(default=None, primary_key=True)

    # 关联工单 / Associated Work Order
    work_order_id: int = Field(
        ...,
        foreign_key="work_orders.id",
        nullable=False,
        description="工单ID / Work order ID",
    )

    # 任务信息 / Task Information
    task_no: int = Field(
        ...,
        description="任务序号 / Task sequence number",
    )
    description: str = Field(
        ...,
        max_length=200,
        sa_column=Column(String(200), nullable=False),
        description="任务描述 / Task description",
    )

    # 执行人 / Assignee
    assignee_id: int | None = Field(
        default=None,
        foreign_key="staff.id",
        description="执行人ID / Assignee ID",
    )

    # 标准作业时间 / Standard Operation Time
    standard_time_minutes: int | None = Field(
        default=None,
        description="标准作业时间(分钟) / Standard time (minutes)",
    )

    # 实际执行 / Actual Execution
    actual_time_minutes: int | None = Field(
        default=None,
        description="实际执行时间(分钟) / Actual time (minutes)",
    )

    # 状态 / Status
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        sa_column=Column(String(20), nullable=False),
        description="任务状态 / Task status",
    )

    # 结果 / Result
    result_notes: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="执行结果备注 / Result notes",
    )

    # 时间戳 / Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="创建时间 / Creation time",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="更新时间 / Update time",
    )

    # 关联关系 / Relationships
    work_order: WorkOrder = Relationship(back_populates="tasks")
    assignee: Optional["Staff"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"foreign_keys": "WorkOrderTask.assignee_id"},
    )

    def __repr__(self) -> str:
        return f"<WorkOrderTask: {self.task_no} - {self.description[:20]}>"

    class Config:
        json_schema_extra = {
            "example": {
                "work_order_id": 1,
                "task_no": 1,
                "description": "检查压缩机润滑油液位",
                "status": "pending",
            }
        }


# ============== Pydantic Schemas for API ==============

class DepartmentCreate(SQLModel):
    """部门创建Schema / Department create schema"""
    code: str
    name: str
    description: str | None = None
    parent_id: int | None = None


class DepartmentRead(SQLModel):
    """部门读取Schema / Department read schema"""
    id: int
    code: str
    name: str
    description: str | None
    parent_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StaffCreate(SQLModel):
    """人员创建Schema / Staff create schema"""
    employee_no: str
    name: str
    role: StaffRole = StaffRole.OPERATOR
    phone: str | None = None
    email: str | None = None
    department_id: int | None = None
    badge_id: str | None = None
    status: StaffStatus = StaffStatus.ACTIVE


class StaffRead(SQLModel):
    """人员读取Schema / Staff read schema"""
    id: int
    employee_no: str
    name: str
    role: StaffRole
    phone: str | None
    email: str | None
    department_id: int | None
    badge_id: str | None
    status: StaffStatus
    gps_latitude: float | None
    gps_longitude: float | None
    gps_updated_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StaffUpdate(SQLModel):
    """人员更新Schema / Staff update schema"""
    name: str | None = None
    role: StaffRole | None = None
    phone: str | None = None
    email: str | None = None
    department_id: int | None = None
    badge_id: str | None = None
    status: StaffStatus | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None


class WorkOrderCreate(SQLModel):
    """工单创建Schema / Work order create schema"""
    order_type: WorkOrderType = WorkOrderType.INSPECTION
    title: str
    description: str | None = None
    priority: WorkOrderPriority = WorkOrderPriority.MEDIUM
    equipment_id: int | None = None
    vehicle_id: int | None = None
    creator_id: int
    assignee_id: int | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None


class WorkOrderRead(SQLModel):
    """工单读取Schema / Work order read schema"""
    id: int
    order_no: str
    order_type: WorkOrderType
    title: str
    description: str | None
    priority: WorkOrderPriority
    equipment_id: int | None
    vehicle_id: int | None
    creator_id: int
    assignee_id: int | None
    planned_start: datetime | None
    planned_end: datetime | None
    actual_start: datetime | None
    actual_end: datetime | None
    status: WorkOrderStatus
    result_summary: str | None
    satisfaction: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkOrderUpdate(SQLModel):
    """工单更新Schema / Work order update schema"""
    title: str | None = None
    description: str | None = None
    priority: WorkOrderPriority | None = None
    assignee_id: int | None = None
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    status: WorkOrderStatus | None = None


class TaskCreate(SQLModel):
    """任务创建Schema / Task create schema"""
    description: str
    assignee_id: int | None = None
    standard_time_minutes: int | None = None


class TaskRead(SQLModel):
    """任务读取Schema / Task read schema"""
    id: int
    work_order_id: int
    task_no: int
    description: str
    assignee_id: int | None
    standard_time_minutes: int | None
    actual_time_minutes: int | None
    status: TaskStatus
    result_notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
