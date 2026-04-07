"""
调度模块数据模型 / Dispatch Module Data Models

包含车辆、泊位、调度相关的数据模型
Includes data models for vehicles, berths, and scheduling

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, Float
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.workflow.models import WorkOrder


# ============== 枚举类型 / Enums ==============

class VehicleType(str, Enum):
    """
    车辆类型 / Vehicle Type

    根据运输垃圾的类型分类
    Classified by the type of waste transported
    """
    DOMESTIC = "domestic"           # 生活垃圾车 / Domestic waste
    KITCHEN = "kitchen"             # 厨余垃圾车 / Kitchen waste
    RECYCLABLE = "recyclable"       # 可回收物车 / Recyclable waste
    HAZARDOUS = "hazardous"         # 有害垃圾车 / Hazardous waste
    BULKY = "bulky"                 # 大件垃圾车 / Bulky waste
    GREEN = "green"                 # 绿化垃圾车 / Green waste


class VehicleStatus(str, Enum):
    """
    车辆状态 / Vehicle Status
    """
    IDLE = "idle"                   # 闲置 / Idle
    EN_ROUTE = "en_route"           # 行驶中 / En route
    QUEUING = "queuing"             # 排队中 / Queuing
    UNLOADING = "unloading"         # 卸料中 / Unloading
    MAINTENANCE = "maintenance"     # 维护中 / Maintenance
    OFFLINE = "offline"             # 离线 / Offline


class BerthType(str, Enum):
    """
    泊位类型 / Berth Type

    对应不同垃圾品类的卸料泊位
    Corresponds to unloading berths for different waste types
    """
    DOMESTIC = "domestic"           # 生活垃圾泊位 / Domestic waste berth
    KITCHEN = "kitchen"             # 厨余垃圾泊位 / Kitchen waste berth
    RECYCLABLE = "recyclable"       # 可回收物泊位 / Recyclable berth
    HAZARDOUS = "hazardous"         # 有害垃圾泊位 / Hazardous waste berth
    BULKY = "bulky"                 # 大件垃圾泊位 / Bulky waste berth
    GREEN = "green"                 # 绿化垃圾泊位 / Green waste berth
    EMERGENCY = "emergency"         # 应急泊位 / Emergency berth


class BerthStatus(str, Enum):
    """
    泊位状态 / Berth Status
    """
    AVAILABLE = "available"         # 空闲 / Available
    OCCUPIED = "occupied"           # 占用 / Occupied
    RESERVED = "reserved"           # 预留 / Reserved
    MAINTENANCE = "maintenance"     # 维护中 / Maintenance
    DISABLED = "disabled"           # 禁用 / Disabled


class ScheduleStatus(str, Enum):
    """
    调度状态 / Schedule Status

    车辆从预约到完成的完整状态流转
    Complete status flow from appointment to completion
    """
    APPOINTMENT = "appointment"     # 已预约 / Appointment made
    QUEUED = "queued"               # 排队中 / In queue
    CHECKED_IN = "checked_in"       # 已进场 / Checked in
    UNLOADING = "unloading"         # 卸料中 / Unloading
    COMPLETED = "completed"         # 已完成 / Completed
    CANCELLED = "cancelled"         # 已取消 / Cancelled


# ============== 车辆模型 / Vehicle Model ==============

class Vehicle(SQLModel, table=True):
    """
    车辆模型 / Vehicle Model

    表示一辆垃圾转运车辆，包含基本信息、状态、GPS位置
    Represents a waste transfer vehicle with basic info, status, and GPS location

    业务规则 / Business Rules:
    - 车牌号全局唯一 / License plate is globally unique
    - 车辆类型决定可运输的垃圾品类 / Vehicle type determines waste type
    - GPS位置实时更新 / GPS location updates in real-time
    """

    __tablename__ = "vehicles"

    id: int | None = Field(default=None, primary_key=True)

    # 基本信息 / Basic Information
    license_plate: str = Field(
        ...,
        max_length=20,
        sa_column=Column(String(20), unique=True, nullable=False, index=True),
        description="车牌号，全局唯一 / License plate, globally unique",
    )
    vehicle_type: VehicleType = Field(
        default=VehicleType.DOMESTIC,
        sa_column=Column(String(20), nullable=False),
        description="车辆类型 / Vehicle type",
    )
    brand: str | None = Field(
        default=None,
        max_length=50,
        sa_column=Column(String(50)),
        description="车辆品牌 / Vehicle brand",
    )
    model: str | None = Field(
        default=None,
        max_length=50,
        sa_column=Column(String(50)),
        description="车辆型号 / Vehicle model",
    )

    # 载重信息 / Capacity Information
    max_capacity: float = Field(
        default=5.0,
        description="最大载重(吨) / Maximum capacity (tons)",
    )
    current_load: float = Field(
        default=0.0,
        description="当前载重(吨) / Current load (tons)",
    )

    # 状态 / Status
    status: VehicleStatus = Field(
        default=VehicleStatus.IDLE,
        sa_column=Column(String(20), nullable=False, index=True),
        description="车辆状态 / Vehicle status",
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

    # 运行数据 / Operating Data
    total_mileage: float = Field(
        default=0.0,
        description="总里程(公里) / Total mileage (km)",
    )
    engine_hours: float = Field(
        default=0.0,
        description="发动机运行时长(小时) / Engine operating hours",
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
    schedules: List["Schedule"] = Relationship(
        back_populates="vehicle",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    work_orders: List["WorkOrder"] = Relationship(
        back_populates="vehicle",
    )

    def __repr__(self) -> str:
        return f"<Vehicle: {self.license_plate} ({self.vehicle_type.value})>"

    class Config:
        json_schema_extra = {
            "example": {
                "license_plate": "川A12345",
                "vehicle_type": "domestic",
                "max_capacity": 8.0,
                "status": "idle",
            }
        }


# ============== 泊位模型 / Berth Model ==============

class Berth(SQLModel, table=True):
    """
    泊位模型 / Berth Model

    表示一个垃圾卸料泊位，车辆在此卸料
    Represents a waste unloading berth where vehicles unload

    业务规则 / Business Rules:
    - 泊位编号在站内唯一 / Berth code is unique within station
    - 泊位类型决定可卸料的垃圾品类 / Berth type determines acceptable waste
    - 同一时间只能有一辆车占用 / Only one vehicle at a time
    """

    __tablename__ = "berths"

    id: int | None = Field(default=None, primary_key=True)

    # 基本信息 / Basic Information
    code: str = Field(
        ...,
        max_length=20,
        sa_column=Column(String(20), unique=True, nullable=False, index=True),
        description="泊位编号，站内唯一 / Berth code, unique within station",
    )
    name: str = Field(
        ...,
        max_length=50,
        sa_column=Column(String(50), nullable=False),
        description="泊位名称 / Berth name",
    )
    berth_type: BerthType = Field(
        default=BerthType.DOMESTIC,
        sa_column=Column(String(20), nullable=False),
        description="泊位类型 / Berth type",
    )

    # 位置信息 / Location Information
    location_x: float | None = Field(
        default=None,
        description="X坐标(米) / X coordinate (meters)",
    )
    location_y: float | None = Field(
        default=None,
        description="Y坐标(米) / Y coordinate (meters)",
    )

    # 容量 / Capacity
    capacity_tons: float = Field(
        default=10.0,
        description="设计容量(吨) / Design capacity (tons)",
    )

    # 状态 / Status
    status: BerthStatus = Field(
        default=BerthStatus.AVAILABLE,
        sa_column=Column(String(20), nullable=False, index=True),
        description="泊位状态 / Berth status",
    )

    # 当前占用 / Current Occupancy
    current_vehicle_id: int | None = Field(
        default=None,
        foreign_key="vehicles.id",
        description="当前占用车辆ID / Currently occupying vehicle ID",
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
    schedules: List["Schedule"] = Relationship(
        back_populates="berth",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def __repr__(self) -> str:
        return f"<Berth: {self.code} ({self.berth_type.value})>"

    class Config:
        json_schema_extra = {
            "example": {
                "code": "A01",
                "name": "生活垃圾泊位1号",
                "berth_type": "domestic",
                "status": "available",
            }
        }


# ============== 调度模型 / Schedule Model ==============

class Schedule(SQLModel, table=True):
    """
    调度记录模型 / Schedule Record Model

    记录车辆从预约到完成的完整调度过程
    Records the complete dispatch process from appointment to completion

    业务规则 / Business Rules:
    - 预约时需要选择目标泊位类型 / Appointment requires selecting target berth type
    - 车辆到达后分配具体泊位 / Specific berth assigned upon arrival
    - 状态按固定流程流转 / Status flows in fixed sequence
    """

    __tablename__ = "schedules"

    id: int | None = Field(default=None, primary_key=True)

    # 关联车辆 / Associated Vehicle
    vehicle_id: int = Field(
        ...,
        foreign_key="vehicles.id",
        nullable=False,
        description="车辆ID / Vehicle ID",
    )

    # 关联泊位 / Associated Berth
    berth_id: int | None = Field(
        default=None,
        foreign_key="berths.id",
        description="分配泊位ID / Assigned berth ID",
    )

    # 预约信息 / Appointment Information
    appointment_time: datetime = Field(
        ...,
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="预约时间 / Appointment time",
    )
    expected_waste_type: str = Field(
        default="domestic",
        sa_column=Column(String(20)),
        description="预期垃圾类型 / Expected waste type",
    )
    expected_weight: float | None = Field(
        default=None,
        description="预期重量(吨) / Expected weight (tons)",
    )

    # 排队信息 / Queue Information
    queue_number: int | None = Field(
        default=None,
        description="排队序号 / Queue number",
    )
    queue_entered_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="进入队列时间 / Queue entry time",
    )

    # 时间记录 / Time Records
    checked_in_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="进场时间 / Check-in time",
    )
    unloading_started_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="开始卸料时间 / Unloading start time",
    )
    unloading_completed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="卸料完成时间 / Unloading completion time",
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="完成时间 / Completion time",
    )

    # 称重数据 / Weighing Data
    gross_weight: float | None = Field(
        default=None,
        description="毛重(kg) / Gross weight (kg)",
    )
    tare_weight: float | None = Field(
        default=None,
        description="皮重(kg) / Tare weight (kg)",
    )
    net_weight: float | None = Field(
        default=None,
        description="净重(kg) / Net weight (kg)",
    )

    # 状态 / Status
    status: ScheduleStatus = Field(
        default=ScheduleStatus.APPOINTMENT,
        sa_column=Column(String(20), nullable=False, index=True),
        description="调度状态 / Schedule status",
    )

    # 备注 / Notes
    notes: str | None = Field(
        default=None,
        sa_column=Column(String(500)),
        description="备注 / Notes",
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
    vehicle: Vehicle = Relationship(back_populates="schedules")
    berth: Optional[Berth] = Relationship(back_populates="schedules")

    def __repr__(self) -> str:
        return f"<Schedule: {self.id} - {self.status.value}>"

    def calculate_net_weight(self) -> float | None:
        """
        计算净重 / Calculate net weight

        Returns:
            净重(kg)或None / Net weight (kg) or None
        """
        if self.gross_weight and self.tare_weight:
            return self.gross_weight - self.tare_weight
        return None

    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_id": 1,
                "appointment_time": "2026-04-07T10:00:00Z",
                "expected_waste_type": "domestic",
                "status": "appointment",
            }
        }


# ============== Pydantic Schemas for API ==============

class VehicleCreate(SQLModel):
    """车辆创建Schema / Vehicle create schema"""
    license_plate: str
    vehicle_type: VehicleType = VehicleType.DOMESTIC
    brand: str | None = None
    model: str | None = None
    max_capacity: float = 5.0
    current_load: float = 0.0
    status: VehicleStatus = VehicleStatus.IDLE
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    total_mileage: float = 0.0
    engine_hours: float = 0.0


class VehicleRead(SQLModel):
    """车辆读取Schema / Vehicle read schema"""
    id: int
    license_plate: str
    vehicle_type: VehicleType
    brand: str | None
    model: str | None
    max_capacity: float
    current_load: float
    status: VehicleStatus
    gps_latitude: float | None
    gps_longitude: float | None
    total_mileage: float
    engine_hours: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehicleUpdate(SQLModel):
    """车辆更新Schema / Vehicle update schema"""
    vehicle_type: VehicleType | None = None
    brand: str | None = None
    model: str | None = None
    max_capacity: float | None = None
    current_load: float | None = None
    status: VehicleStatus | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    total_mileage: float | None = None
    engine_hours: float | None = None


class BerthRead(SQLModel):
    """泊位读取Schema / Berth read schema"""
    id: int
    code: str
    name: str
    berth_type: BerthType
    location_x: float | None
    location_y: float | None
    capacity_tons: float
    status: BerthStatus
    current_vehicle_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleCreate(SQLModel):
    """调度创建Schema / Schedule create schema"""
    vehicle_id: int
    appointment_time: datetime
    expected_waste_type: str = "domestic"
    expected_weight: float | None = None


class ScheduleRead(SQLModel):
    """调度读取Schema / Schedule read schema"""
    id: int
    vehicle_id: int
    berth_id: int | None
    appointment_time: datetime
    expected_waste_type: str
    expected_weight: float | None
    queue_number: int | None
    queue_entered_at: datetime | None
    checked_in_at: datetime | None
    unloading_started_at: datetime | None
    unloading_completed_at: datetime | None
    completed_at: datetime | None
    gross_weight: float | None
    tare_weight: float | None
    net_weight: float | None
    status: ScheduleStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleUpdate(SQLModel):
    """调度更新Schema / Schedule update schema"""
    berth_id: int | None = None
    expected_waste_type: str | None = None
    expected_weight: float | None = None
    status: ScheduleStatus | None = None
    notes: str | None = None
