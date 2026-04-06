"""告警规则模型

定义设备告警触发条件
"""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Index, String
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    pass


class RuleMetric(str, Enum):
    """规则指标枚举"""

    TEMPERATURE = "temperature"  # 温度
    VIBRATION = "vibration"  # 振动
    CURRENT = "current"  # 电流


class RuleOperator(str, Enum):
    """规则操作符枚举

    - gt: 大于 (greater than)
    - lt: 小于 (less than)
    - eq: 等于 (equal to)
    """

    GT = "gt"  # 大于
    LT = "lt"  # 小于
    EQ = "eq"  # 等于


class AlertRule(SQLModel, table=True):
    """告警规则模型

    定义触发告警的条件规则
    device_id 为空表示适用于所有设备
    """

    __tablename__ = "alert_rules"
    __table_args__ = (
        Index("idx_alert_rules_device_metric", "device_id", "metric"),
    )

    id: int | None = Field(default=None, primary_key=True)
    device_id: int | None = Field(
        default=None,
        sa_column=Column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=True),
        description="关联设备ID，空表示所有设备",
    )
    metric: RuleMetric = Field(
        ...,
        sa_column=Column(String(20), nullable=False),
        description="监控指标",
    )
    operator: RuleOperator = Field(
        ...,
        sa_column=Column(String(10), nullable=False),
        description="比较操作符",
    )
    threshold: float = Field(
        ...,
        description="阈值",
    )
    duration: int = Field(
        default=0,
        description="持续时间（秒），0表示立即触发",
    )
    enabled: bool = Field(
        default=True,
        description="是否启用",
    )
    description: str | None = Field(
        default=None,
        max_length=200,
        sa_column=Column(String(200), nullable=True),
        description="规则描述",
    )

    def __repr__(self) -> str:
        device_str = f"device={self.device_id}" if self.device_id else "all devices"
        return f"<AlertRule: {device_str} {self.metric.value} {self.operator.value} {self.threshold}>"

    def check_condition(self, value: float) -> bool:
        """检查值是否满足规则条件

        Args:
            value: 传感器读数

        Returns:
            bool: 是否触发规则
        """
        match self.operator:
            case RuleOperator.GT:
                return value > self.threshold
            case RuleOperator.LT:
                return value < self.threshold
            case RuleOperator.EQ:
                return value == self.threshold
            case _:
                return False

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": 1,
                "metric": "temperature",
                "operator": "gt",
                "threshold": 80.0,
                "duration": 60,
                "description": "温度超过80℃持续1分钟触发告警",
            }
        }
