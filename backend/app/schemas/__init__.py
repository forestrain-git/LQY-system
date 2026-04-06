"""Pydantic Schema

用于请求/响应数据验证
"""

from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from app.schemas.alert_rule import (
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
)
from app.schemas.common import ListResponse, Pagination, ResponseBase
from app.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate
from app.schemas.sensor_data import SensorDataCreate, SensorDataResponse

__all__ = [
    # 通用
    "ResponseBase",
    "ListResponse",
    "Pagination",
    # 设备
    "DeviceCreate",
    "DeviceUpdate",
    "DeviceResponse",
    # 传感器数据
    "SensorDataCreate",
    "SensorDataResponse",
    # 告警
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    # 告警规则
    "AlertRuleCreate",
    "AlertRuleUpdate",
    "AlertRuleResponse",
]
