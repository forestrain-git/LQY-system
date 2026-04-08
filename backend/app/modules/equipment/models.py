"""
设备模块数据模型 / Equipment Module Data Models

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, Text, Float
from sqlmodel import Field, Relationship, SQLModel


# ============== 枚举类型 / Enums ==============

class EquipmentType(str, Enum):
    """设备类型 / Equipment Type"""
    COMPRESSOR = "compressor"        # 压缩机
    CONVEYOR = "conveyor"            # 输送带
    WEIGHBRIDGE = "weighbridge"      # 地磅
    FENCE_SYSTEM = "fence_system"    # 电子围栏
    GPS_TRACKER = "gps_tracker"      # GPS追踪器
    BADGE_READER = "badge_reader"    # 工牌读取器
    SENSOR = "sensor"                # 传感器
    CAMERA = "camera"                # 摄像头
    OTHER = "other"                  # 其他


class EquipmentStatus(str, Enum):
    """设备状态 / Equipment Status"""
    NORMAL = "normal"                # 正常
    WARNING = "warning"              # 警告
    ERROR = "error"                  # 故障
    MAINTENANCE = "maintenance"      # 维护中
    OFFLINE = "offline"              # 离线
    DECOMMISSIONED = "decommissioned"  # 已报废


class MaintenanceType(str, Enum):
    """维保类型 / Maintenance Type"""
    INSPECTION = "inspection"        # 巡检
    PREVENTIVE = "preventive"        # 预防性维护
    CORRECTIVE = "corrective"        # 修复性维护
    UPGRADE = "upgrade"              # 升级
    CALIBRATION = "calibration"      # 校准


class MaintenanceStatus(str, Enum):
    """维保状态 / Maintenance Status"""
    SCHEDULED = "scheduled"          # 已计划
    IN_PROGRESS = "in_progress"      # 进行中
    COMPLETED = "completed"          # 已完成
    CANCELLED = "cancelled"          # 已取消


# ============== 设备模型 / Equipment Model ==============

class Equipment(SQLModel, table=True):
    """
    设备模型 / Equipment Model

    表示一个环卫站设备，包含全生命周期信息
    Represents a sanitation station equipment with full lifecycle info
    """

    __tablename__ = "equipment"

    id: int | None = Field(default=None, primary_key=True)

    # 基本信息 / Basic Information
    code: str = Field(
        ...,
        max_length=50,
        sa_column=Column(String(50), unique=True, nullable=False, index=True),
        description="设备编号 / Equipment code",
    )
    name: str = Field(
        ...,
        max_length=100,
        sa_column=Column(String(100), nullable=False),
        description="设备名称 / Equipment name",
    )
    equipment_type: EquipmentType = Field(
        default=EquipmentType.OTHER,
        sa_column=Column(String(30), nullable=False),
        description="设备类型 / Equipment type",
    )
    model: str | None = Field(
        default=None,
        max_length=100,
        sa_column=Column(String(100)),
        description="型号 / Model",
    )
    manufacturer: str | None = Field(
        default=None,
        max_length=100,
        sa_column=Column(String(100)),
        description="制造商 / Manufacturer",
    )
    serial_number: str | None = Field(
        default=None,
        max_length=100,
        sa_column=Column(String(100)),
        description="序列号 / Serial number",
    )

    # 位置信息 / Location
    location: str | None = Field(
        default=None,
        max_length=200,
        sa_column=Column(String(200)),
        description="安装位置 / Installation location",
    )

    # 生命周期 / Lifecycle
    purchase_date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="购买日期 / Purchase date",
    )
    warranty_until: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="保修截止日期 / Warranty expiration",
    )
    commissioning_date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="投运日期 / Commissioning date",
    )
    expected_lifetime_years: int = Field(
        default=10,
        description="预期寿命(年) / Expected lifetime (years)",
    )

    # 状态 / Status
    status: EquipmentStatus = Field(
        default=EquipmentStatus.NORMAL,
        sa_column=Column(String(20), nullable=False, index=True),
        description="设备状态 / Equipment status",
    )

    # 运行数据 / Operating Data
    total_operating_hours: float = Field(
        default=0.0,
        description="总运行时长(小时) / Total operating hours",
    )
    last_maintenance_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="上次维护时间 / Last maintenance time",
    )
    next_maintenance_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="下次维护时间 / Next scheduled maintenance",
    )

    # 配置 / Configuration
    config: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="配置参数(JSON) / Configuration parameters (JSON)",
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
    maintenance_records: List["MaintenanceRecord"] = Relationship(
        back_populates="equipment",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def __repr__(self) -> str:
        return f"<Equipment: {self.code} ({self.name})>"


# ============== 维保记录模型 / Maintenance Record Model ==============

class MaintenanceRecord(SQLModel, table=True):
    """
    维保记录模型 / Maintenance Record Model

    记录设备的维护保养历史
    Records equipment maintenance history
    """

    __tablename__ = "maintenance_records"

    id: int | None = Field(default=None, primary_key=True)

    # 关联设备 / Associated Equipment
    equipment_id: int = Field(
        ...,
        foreign_key="equipment.id",
        nullable=False,
        description="设备ID / Equipment ID",
    )

    # 维保信息 / Maintenance Info
    record_no: str = Field(
        ...,
        max_length=30,
        sa_column=Column(String(30), unique=True, nullable=False),
        description="维保单号 / Maintenance record number",
    )
    maintenance_type: MaintenanceType = Field(
        default=MaintenanceType.INSPECTION,
        sa_column=Column(String(20), nullable=False),
        description="维保类型 / Maintenance type",
    )
    title: str = Field(
        ...,
        max_length=100,
        sa_column=Column(String(100), nullable=False),
        description="维保标题 / Maintenance title",
    )
    description: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="维保内容描述 / Description",
    )

    # 执行人员 / Personnel
    technician_id: int | None = Field(
        default=None,
        foreign_key="staff.id",
        description="执行技术员ID / Technician ID",
    )

    # 计划时间 / Planned Time
    planned_date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="计划日期 / Planned date",
    )

    # 实际执行 / Actual Execution
    started_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="开始时间 / Start time",
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="完成时间 / Completion time",
    )

    # 耗材与成本 / Materials & Cost
    parts_used: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="使用备件 / Parts used",
    )
    labor_hours: float | None = Field(
        default=None,
        description="工时(小时) / Labor hours",
    )
    cost: float | None = Field(
        default=None,
        description="费用(元) / Cost",
    )

    # 状态 / Status
    status: MaintenanceStatus = Field(
        default=MaintenanceStatus.SCHEDULED,
        sa_column=Column(String(20), nullable=False),
        description="维保状态 / Maintenance status",
    )

    # 结果 / Result
    result_notes: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="维保结果 / Result notes",
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
    equipment: Equipment = Relationship(back_populates="maintenance_records")

    def __repr__(self) -> str:
        return f"<MaintenanceRecord: {self.record_no}>"


# ============== Pydantic Schemas ==============

class EquipmentCreate(SQLModel):
    """设备创建Schema"""
    code: str
    name: str
    equipment_type: EquipmentType = EquipmentType.OTHER
    model: str | None = None
    manufacturer: str | None = None
    serial_number: str | None = None
    location: str | None = None
    purchase_date: datetime | None = None
    warranty_until: datetime | None = None
    expected_lifetime_years: int = 10


class EquipmentRead(SQLModel):
    """设备读取Schema"""
    id: int
    code: str
    name: str
    equipment_type: EquipmentType
    model: str | None
    manufacturer: str | None
    location: str | None
    status: EquipmentStatus
    total_operating_hours: float
    last_maintenance_at: datetime | None
    next_maintenance_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class EquipmentUpdate(SQLModel):
    """设备更新Schema"""
    name: str | None = None
    model: str | None = None
    location: str | None = None
    status: EquipmentStatus | None = None
    total_operating_hours: float | None = None


class MaintenanceCreate(SQLModel):
    """维保创建Schema"""
    maintenance_type: MaintenanceType = MaintenanceType.INSPECTION
    title: str
    description: str | None = None
    technician_id: int | None = None
    planned_date: datetime | None = None


class MaintenanceRead(SQLModel):
    """维保读取Schema"""
    id: int
    record_no: str
    maintenance_type: MaintenanceType
    title: str
    description: str | None
    technician_id: int | None
    planned_date: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    status: MaintenanceStatus
    result_notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True
