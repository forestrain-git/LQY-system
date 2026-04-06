"""告警规则Schema

告警规则相关的请求/响应数据模型
"""

from pydantic import BaseModel, ConfigDict, Field

from app.models.alert_rule import RuleMetric, RuleOperator


class AlertRuleBase(BaseModel):
    """告警规则基础Schema"""

    device_id: int | None = Field(default=None, description="设备ID，空表示所有设备")
    metric: RuleMetric = Field(..., description="监控指标")
    operator: RuleOperator = Field(..., description="比较操作符")
    threshold: float = Field(..., description="阈值")
    duration: int = Field(default=0, description="持续时间(秒)")
    enabled: bool = Field(default=True, description="是否启用")
    description: str | None = Field(default=None, max_length=200, description="规则描述")


class AlertRuleCreate(AlertRuleBase):
    """创建告警规则请求Schema"""

    pass


class AlertRuleUpdate(BaseModel):
    """更新告警规则请求Schema"""

    device_id: int | None = Field(default=None, description="设备ID")
    metric: RuleMetric | None = Field(default=None, description="监控指标")
    operator: RuleOperator | None = Field(default=None, description="比较操作符")
    threshold: float | None = Field(default=None, description="阈值")
    duration: int | None = Field(default=None, description="持续时间(秒)")
    enabled: bool | None = Field(default=None, description="是否启用")
    description: str | None = Field(default=None, description="规则描述")


class AlertRuleResponse(AlertRuleBase):
    """告警规则响应Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="规则ID")
    device_name: str | None = Field(default=None, description="设备名称（空表示所有设备）")
