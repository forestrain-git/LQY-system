"""设备模型

管理环卫设备的基本信息和状态
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.sensor_data import SensorData


class DeviceType(str, Enum):
    """设备类型枚举"""

    COMPRESSOR = "compressor"  # 压缩机
    PUMP = "pump"  # 泵
    FAN = "fan"  # 风机
    CONVEYOR = "conveyor"  # 传送带
    OTHER = "other"  # 其他


class DeviceStatus(str, Enum):
    """设备状态枚举

    使用 disabled 代替物理删除，保持数据完整性
    """

    ONLINE = "online"  # 在线运行
    OFFLINE = "offline"  # 离线
    MAINTENANCE = "maintenance"  # 维护中
    DISABLED = "disabled"  # 已禁用（软删除）


class Device(SQLModel, table=True):
    """设备模型

    表示一个环卫设备，包含基本信息和状态
    """

    __tablename__ = "devices"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(
        ...,
        max_length=50,
        sa_column=Column(String(50), unique=True, nullable=False, index=True),
        description="设备名称，全局唯一",
    )
    type: DeviceType = Field(
        default=DeviceType.COMPRESSOR,
        sa_column=Column(String(20), nullable=False),
        description="设备类型",
    )
    location: str | None = Field(
        default=None,
        max_length=100,
        sa_column=Column(String(100)),
        description="设备安装位置",
    )
    status: DeviceStatus = Field(
        default=DeviceStatus.OFFLINE,
        sa_column=Column(String(20), nullable=False, index=True),
        description="设备状态，disabled表示软删除",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="创建时间，UTC",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
        description="更新时间，UTC",
    )

    # 关系
    sensor_data: List["SensorData"] = Relationship(
        back_populates="device",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    alerts: List["Alert"] = Relationship(
        back_populates="device",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def __repr__(self) -> str:
        return f"<Device: {self.name} ({self.status.value})>"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "压缩机-01",
                "type": "compressor",
                "location": "A区垃圾处理站",
                "status": "online",
            }
        }
