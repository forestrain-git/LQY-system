"""设备Schema

设备相关的请求/响应数据模型
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.device import DeviceStatus, DeviceType


class DeviceBase(BaseModel):
    """设备基础Schema"""

    name: str = Field(..., max_length=50, description="设备名称")
    type: DeviceType = Field(default=DeviceType.COMPRESSOR, description="设备类型")
    location: str | None = Field(default=None, max_length=100, description="安装位置")
    status: DeviceStatus = Field(default=DeviceStatus.OFFLINE, description="设备状态")


class DeviceCreate(DeviceBase):
    """创建设备请求Schema"""

    pass


class DeviceUpdate(BaseModel):
    """更新设备请求Schema

    所有字段可选，只更新提供的字段
    """

    name: str | None = Field(default=None, max_length=50, description="设备名称")
    type: DeviceType | None = Field(default=None, description="设备类型")
    location: str | None = Field(default=None, max_length=100, description="安装位置")
    status: DeviceStatus | None = Field(default=None, description="设备状态")


class DeviceResponse(DeviceBase):
    """设备响应Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="设备ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    latest_sensor_data: SensorDataResponse | None = Field(
        default=None, description="最新传感器数据"
    )


# 前向引用 - 在sensor_data.py定义后重建模型
from app.schemas.sensor_data import SensorDataResponse  # noqa: E402, F401

DeviceResponse.model_rebuild()
