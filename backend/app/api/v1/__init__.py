"""API v1 路由 / API v1 Routes

包含所有v1版本的API路由
Includes all v1 version API routes
"""

from app.api.v1.alert_rules import router as alert_rules_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.devices import router as devices_router
from app.api.v1.sensor_data import router as sensor_data_router
from app.api.v1.predictions import router as predictions_router

__all__ = [
    "devices_router",
    "sensor_data_router",
    "alerts_router",
    "alert_rules_router",
    "predictions_router"
]
