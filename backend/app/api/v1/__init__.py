"""API v1 路由

包含所有v1版本的API路由
"""

from app.api.v1.alert_rules import router as alert_rules_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.devices import router as devices_router
from app.api.v1.sensor_data import router as sensor_data_router

__all__ = ["devices_router", "sensor_data_router", "alerts_router", "alert_rules_router"]
