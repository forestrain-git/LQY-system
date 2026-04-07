"""
安全管控数据模型 / Safety Control Data Models

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, Text, Float
from sqlmodel import Field, Relationship, SQLModel


# ============== 枚举类型 / Enums ==============

class SafetyAlertType(str, Enum):
    """安全告警类型 / Safety Alert Type"""
    FENCE_VIOLATION = "fence_violation"      # 电子围栏越界
    UNAUTHORIZED_ACCESS = "unauthorized_access"  # 未授权进入
    EQUIPMENT_FAILURE = "equipment_failure"   # 设备故障
    HAZARDOUS_MATERIAL = "hazardous_material" # 危险品泄漏
    FIRE_RISK = "fire_risk"                   # 火灾风险
    PPE_VIOLATION = "ppe_violation"          # 未佩戴防护装备
    VEHICLE_INCIDENT = "vehicle_incident"     # 车辆事故
    EMERGENCY = "emergency"                   # 紧急情况


class SafetyAlertLevel(str, Enum):
    """安全告警级别 / Safety Alert Level"""
    INFO = "info"         # 提示
    WARNING = "warning"   # 警告
    CRITICAL = "critical" # 严重
    EMERGENCY = "emergency" # 紧急


class SafetyAlertStatus(str, Enum):
    """安全告警状态 / Safety Alert Status"""
    ACTIVE = "active"         # 活跃
    ACKNOWLEDGED = "acknowledged"  # 已确认
    RESOLVED = "resolved"     # 已解决
    DISMISSED = "dismissed"   # 已忽略


class RiskLevel(str, Enum):
    """风险等级 / Risk Level"""
    LOW = "low"       # 低
    MEDIUM = "medium" # 中
    HIGH = "high"     # 高
    EXTREME = "extreme" # 极高


# ============== 安全告警模型 / Safety Alert Model ==============

class SafetyAlert(SQLModel, table=True):
    """
    安全告警模型 / Safety Alert Model

    记录安全相关的告警事件
    Records safety-related alert events
    """

    __tablename__ = "safety_alerts"

    id: int | None = Field(default=None, primary_key=True)

    # 告警信息 / Alert Info
    alert_code: str = Field(
        ...,
        max_length=30,
        sa_column=Column(String(30), unique=True, nullable=False),
        description="告警编号 / Alert code",
    )
    alert_type: SafetyAlertType = Field(
        ...,
        sa_column=Column(String(30), nullable=False),
        description="告警类型 / Alert type",
    )
    level: SafetyAlertLevel = Field(
        ...,
        sa_column=Column(String(20), nullable=False),
        description="告警级别 / Alert level",
    )
    title: str = Field(
        ...,
        max_length=200,
        sa_column=Column(String(200), nullable=False),
        description="告警标题 / Alert title",
    )
    description: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="告警描述 / Alert description",
    )

    # 位置信息 / Location
    location: str | None = Field(
        default=None,
        max_length=200,
        sa_column=Column(String(200)),
        description="发生位置 / Location",
    )
    gps_latitude: float | None = Field(
        default=None,
        description="GPS纬度 / GPS latitude",
    )
    gps_longitude: float | None = Field(
        default=None,
        description="GPS经度 / GPS longitude",
    )

    # 关联对象 / Related Objects
    equipment_id: int | None = Field(
        default=None,
        foreign_key="devices.id",
        description="关联设备ID / Related equipment ID",
    )
    vehicle_id: int | None = Field(
        default=None,
        foreign_key="vehicles.id",
        description="关联车辆ID / Related vehicle ID",
    )
    staff_id: int | None = Field(
        default=None,
        foreign_key="staff.id",
        description="关联人员ID / Related staff ID",
    )

    # 处理信息 / Handling Info
    status: SafetyAlertStatus = Field(
        default=SafetyAlertStatus.ACTIVE,
        sa_column=Column(String(20), nullable=False, index=True),
        description="告警状态 / Alert status",
    )
    acknowledged_by: int | None = Field(
        default=None,
        foreign_key="staff.id",
        description="确认人ID / Acknowledged by",
    )
    acknowledged_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="确认时间 / Acknowledged time",
    )
    resolved_by: int | None = Field(
        default=None,
        foreign_key="staff.id",
        description="解决人ID / Resolved by",
    )
    resolved_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="解决时间 / Resolved time",
    )
    resolution_notes: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="解决方案 / Resolution notes",
    )

    # 时间戳 / Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="创建时间 / Creation time",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="更新时间 / Update time",
    )

    def __repr__(self) -> str:
        return f"<SafetyAlert: {self.alert_code} ({self.level.value})>"


# ============== 风险评估模型 / Risk Assessment Model ==============

class RiskAssessment(SQLModel, table=True):
    """
    风险评估模型 / Risk Assessment Model

    记录定期的风险评估结果
    Records periodic risk assessment results
    """

    __tablename__ = "risk_assessments"

    id: int | None = Field(default=None, primary_key=True)

    # 评估信息 / Assessment Info
    assessment_code: str = Field(
        ...,
        max_length=30,
        sa_column=Column(String(30), unique=True, nullable=False),
        description="评估编号 / Assessment code",
    )
    area: str = Field(
        ...,
        max_length=100,
        sa_column=Column(String(100), nullable=False),
        description="评估区域 / Assessment area",
    )
    overall_risk: RiskLevel = Field(
        ...,
        sa_column=Column(String(20), nullable=False),
        description="整体风险等级 / Overall risk level",
    )

    # 风险项 / Risk Items
    identified_hazards: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="识别的危险源(JSON) / Identified hazards (JSON)",
    )
    mitigation_measures: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="缓解措施(JSON) / Mitigation measures (JSON)",
    )

    # 评估人员 / Assessor
    assessed_by: int = Field(
        ...,
        foreign_key="staff.id",
        description="评估人ID / Assessor ID",
    )
    assessed_at: datetime = Field(
        ...,
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="评估时间 / Assessment time",
    )

    # 时间戳 / Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    def __repr__(self) -> str:
        return f"<RiskAssessment: {self.assessment_code}>"


# ============== Pydantic Schemas ==============

class SafetyAlertCreate(SQLModel):
    """安全告警创建Schema"""
    alert_type: SafetyAlertType
    level: SafetyAlertLevel
    title: str
    description: str | None = None
    location: str | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    equipment_id: int | None = None
    vehicle_id: int | None = None
    staff_id: int | None = None


class SafetyAlertRead(SQLModel):
    """安全告警读取Schema"""
    id: int
    alert_code: str
    alert_type: SafetyAlertType
    level: SafetyAlertLevel
    title: str
    description: str | None
    location: str | None
    status: SafetyAlertStatus
    acknowledged_by: int | None
    acknowledged_at: datetime | None
    resolved_by: int | None
    resolved_at: datetime | None
    resolution_notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class SafetyAlertUpdate(SQLModel):
    """安全告警更新Schema"""
    status: SafetyAlertStatus | None = None
    resolution_notes: str | None = None


class RiskAssessmentCreate(SQLModel):
    """风险评估创建Schema"""
    area: str
    overall_risk: RiskLevel
    identified_hazards: str | None = None
    mitigation_measures: str | None = None
    assessed_by: int


class RiskAssessmentRead(SQLModel):
    """风险评估读取Schema"""
    id: int
    assessment_code: str
    area: str
    overall_risk: RiskLevel
    assessed_by: int
    assessed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
