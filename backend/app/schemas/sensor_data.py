"""传感器数据Schema

传感器数据相关的请求/响应数据模型
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SensorDataBase(BaseModel):
    """传感器数据基础Schema"""

    device_id: int = Field(..., description="设备ID")
    temperature: float | None = Field(default=None, description="温度(℃)")
    vibration: float | None = Field(default=None, description="振动(mm/s)")
    current: float | None = Field(default=None, description="电流(A)")


class SensorDataCreate(SensorDataBase):
    """创建传感器数据请求Schema"""

    pass


class SensorDataResponse(SensorDataBase):
    """传感器数据响应Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="数据ID")
    timestamp: datetime = Field(..., description="采集时间")
    device_name: str = Field(..., description="设备名称")
