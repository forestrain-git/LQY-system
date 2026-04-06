"""告警Schema

告警相关的请求/响应数据模型
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.alert import AlertLevel, AlertMetric, AlertStatus, AlertType


class AlertBase(BaseModel):
    """告警基础Schema"""

    device_id: int = Field(..., description="设备ID")
    alert_type: AlertType = Field(default=AlertType.THRESHOLD, description="告警类型")
    metric: AlertMetric = Field(default=AlertMetric.SYSTEM, description="告警指标")
    message: str = Field(..., max_length=200, description="告警消息")
    level: AlertLevel = Field(default=AlertLevel.INFO, description="告警级别")


class AlertCreate(AlertBase):
    """创建告警请求Schema"""

    pass


class AlertUpdate(BaseModel):
    """更新告警请求Schema"""

    status: AlertStatus | None = Field(default=None, description="告警状态")


class AlertResponse(AlertBase):
    """告警响应Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="告警ID")
    status: AlertStatus = Field(..., description="告警状态")
    created_at: datetime = Field(..., description="创建时间")
    acknowledged_at: datetime | None = Field(default=None, description="确认时间")
    resolved_at: datetime | None = Field(default=None, description="解决时间")
    device_name: str = Field(..., description="设备名称")
