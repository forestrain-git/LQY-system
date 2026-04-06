"""告警模型

记录设备告警信息，支持阈值、趋势、预测、系统告警
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.device import Device


class AlertType(str, Enum):
    """告警类型枚举"""

    THRESHOLD = "threshold"  # 阈值告警
    TREND = "trend"  # 趋势告警
    PREDICTION = "prediction"  # 预测告警
    SYSTEM = "system"  # 系统告警


class AlertMetric(str, Enum):
    """告警指标枚举"""

    TEMPERATURE = "temperature"  # 温度
    VIBRATION = "vibration"  # 振动
    CURRENT = "current"  # 电流
    SYSTEM = "system"  # 系统


class AlertLevel(str, Enum):
    """告警级别枚举

    三级告警体系：
    - critical: 需要立即处理
    - warning: 需要关注
    - info: 仅记录
    """

    CRITICAL = "critical"  # 严重
    WARNING = "warning"  # 警告
    INFO = "info"  # 信息


class AlertStatus(str, Enum):
    """告警状态枚举"""

    ACTIVE = "active"  # 活跃（未处理）
    ACKNOWLEDGED = "acknowledged"  # 已确认
    RESOLVED = "resolved"  # 已解决


class Alert(SQLModel, table=True):
    """告警模型

    记录设备异常和告警信息
    """

    __tablename__ = "alerts"
    __table_args__ = (
        Index("idx_alerts_device_id_status", "device_id", "status"),
        Index("idx_alerts_created_at", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    device_id: int = Field(
        ...,
        sa_column=Column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        description="关联设备ID",
    )
    alert_type: AlertType = Field(
        default=AlertType.THRESHOLD,
        sa_column=Column(String(20), nullable=False),
        description="告警类型",
    )
    metric: AlertMetric = Field(
        default=AlertMetric.SYSTEM,
        sa_column=Column(String(20), nullable=False),
        description="告警指标",
    )
    message: str = Field(
        ...,
        max_length=200,
        sa_column=Column(String(200), nullable=False),
        description="告警消息",
    )
    level: AlertLevel = Field(
        default=AlertLevel.INFO,
        sa_column=Column(String(20), nullable=False, index=True),
        description="告警级别",
    )
    status: AlertStatus = Field(
        default=AlertStatus.ACTIVE,
        sa_column=Column(String(20), nullable=False, index=True),
        description="告警状态",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="创建时间，UTC",
    )
    acknowledged_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="确认时间，UTC",
    )
    resolved_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="解决时间，UTC",
    )

    # 关系
    device: "Device" = Relationship(back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert: {self.level.value} - {self.message[:30]}>"

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": 1,
                "alert_type": "threshold",
                "metric": "temperature",
                "message": "温度超过阈值: 85℃ > 80℃",
                "level": "warning",
            }
        }
