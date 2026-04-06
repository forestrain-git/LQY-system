"""传感器数据模型

存储设备传感器采集的温度、振动、电流等数据
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Index
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.device import Device


class SensorData(SQLModel, table=True):
    """传感器数据模型

    记录设备运行时的传感器读数
    """

    __tablename__ = "sensor_data"
    __table_args__ = (
        Index("idx_sensor_data_device_id_timestamp", "device_id", "timestamp"),
    )

    id: int | None = Field(default=None, primary_key=True)
    device_id: int = Field(
        ...,
        sa_column=Column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        description="关联设备ID",
    )
    temperature: float | None = Field(
        default=None,
        description="温度(℃)",
    )
    vibration: float | None = Field(
        default=None,
        description="振动(mm/s)",
    )
    current: float | None = Field(
        default=None,
        description="电流(A)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
        description="数据采集时间，UTC",
    )

    # 关系
    device: "Device" = Relationship(back_populates="sensor_data")

    def __repr__(self) -> str:
        return f"<SensorData: device={self.device_id} at {self.timestamp}>"

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": 1,
                "temperature": 65.5,
                "vibration": 2.3,
                "current": 12.5,
            }
        }
