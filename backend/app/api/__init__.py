"""API路由模块
"""

from app.api.v1 import devices_router, sensor_data_router

__all__ = ["devices_router", "sensor_data_router"]
