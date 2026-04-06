"""API v1 路由

包含所有v1版本的API路由
"""

from app.api.v1.devices import router as devices_router
from app.api.v1.sensor_data import router as sensor_data_router

__all__ = ["devices_router", "sensor_data_router"]
