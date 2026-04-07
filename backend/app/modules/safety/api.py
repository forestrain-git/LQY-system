"""
安全管控API路由 / Safety Control API Routes

Author: AI Sprint
Date: 2026-04-07
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlmodel import select

from app.database import get_session
from app.modules.safety.models import (
    SafetyAlert, SafetyAlertCreate, SafetyAlertRead, SafetyAlertUpdate,
    SafetyAlertType, SafetyAlertLevel, SafetyAlertStatus,
    RiskAssessment, RiskAssessmentCreate, RiskAssessmentRead,
    RiskLevel
)

router = APIRouter(prefix="/safety", tags=["safety"])


# ============== 安全告警 / Safety Alerts ==============

@router.get("/alerts", response_model=List[SafetyAlertRead])
async def list_alerts(
    status: Optional[str] = None,
    level: Optional[str] = None,
    alert_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """获取安全告警列表 / Get safety alerts list"""
    query = select(SafetyAlert)
    if status:
        query = query.where(SafetyAlert.status == status)
    if level:
        query = query.where(SafetyAlert.level == level)
    if alert_type:
        query = query.where(SafetyAlert.alert_type == alert_type)

    query = query.order_by(SafetyAlert.created_at.desc())
    result = await session.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/alerts", response_model=SafetyAlertRead)
async def create_alert(
    alert: SafetyAlertCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建安全告警 / Create safety alert"""
    alert_code = f"SA{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

    db_alert = SafetyAlert(
        alert_code=alert_code,
        alert_type=alert.alert_type,
        level=alert.level,
        title=alert.title,
        description=alert.description,
        location=alert.location,
        gps_latitude=alert.gps_latitude,
        gps_longitude=alert.gps_longitude,
        equipment_id=alert.equipment_id,
        vehicle_id=alert.vehicle_id,
        staff_id=alert.staff_id,
        status=SafetyAlertStatus.ACTIVE
    )

    session.add(db_alert)
    await session.commit()
    await session.refresh(db_alert)
    return db_alert


@router.get("/alerts/{alert_id}", response_model=SafetyAlertRead)
async def get_alert(alert_id: int, session: AsyncSession = Depends(get_session)):
    """获取告警详情 / Get alert details"""
    alert = await session.get(SafetyAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    staff_id: int,
    session: AsyncSession = Depends(get_session)
):
    """确认告警 / Acknowledge alert"""
    alert = await session.get(SafetyAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if alert.status != SafetyAlertStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Alert is not active")

    alert.status = SafetyAlertStatus.ACKNOWLEDGED
    alert.acknowledged_by = staff_id
    alert.acknowledged_at = datetime.now()
    alert.updated_at = datetime.now()

    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return {"message": "Alert acknowledged", "alert": alert}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    staff_id: int,
    resolution_notes: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """解决告警 / Resolve alert"""
    alert = await session.get(SafetyAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if alert.status == SafetyAlertStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Alert already resolved")

    alert.status = SafetyAlertStatus.RESOLVED
    alert.resolved_by = staff_id
    alert.resolved_at = datetime.now()
    alert.resolution_notes = resolution_notes
    alert.updated_at = datetime.now()

    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return {"message": "Alert resolved", "alert": alert}


# ============== 安全统计 / Safety Statistics ==============

@router.get("/stats/overview")
async def get_safety_stats(session: AsyncSession = Depends(get_session)):
    """获取安全统计概览 / Get safety statistics overview"""
    # 状态统计
    status_result = await session.execute(
        select(SafetyAlert.status, func.count(SafetyAlert.id)).group_by(SafetyAlert.status)
    )
    by_status = {row[0].value: row[1] for row in status_result.all()}

    # 级别统计
    level_result = await session.execute(
        select(SafetyAlert.level, func.count(SafetyAlert.id)).group_by(SafetyAlert.level)
    )
    by_level = {row[0].value: row[1] for row in level_result.all()}

    # 类型统计
    type_result = await session.execute(
        select(SafetyAlert.alert_type, func.count(SafetyAlert.id)).group_by(SafetyAlert.alert_type)
    )
    by_type = {row[0].value: row[1] for row in type_result.all()}

    # 今日告警
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await session.execute(
        select(func.count(SafetyAlert.id)).where(SafetyAlert.created_at >= today_start)
    )
    today_count = today_result.scalar()

    # 活跃告警
    active_count = by_status.get('active', 0) + by_status.get('acknowledged', 0)

    return {
        "by_status": by_status,
        "by_level": by_level,
        "by_type": by_type,
        "today_count": today_count,
        "active_count": active_count,
        "total": sum(by_status.values())
    }


# ============== 风险评估 / Risk Assessment ==============

@router.get("/risk-assessments", response_model=List[RiskAssessmentRead])
async def list_risk_assessments(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """获取风险评估列表 / Get risk assessment list"""
    result = await session.execute(
        select(RiskAssessment)
        .order_by(RiskAssessment.assessed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/risk-assessments", response_model=RiskAssessmentRead)
async def create_risk_assessment(
    assessment: RiskAssessmentCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建风险评估 / Create risk assessment"""
    assessment_code = f"RA{datetime.now().strftime('%Y%m%d%H%M%S')}"

    db_assessment = RiskAssessment(
        assessment_code=assessment_code,
        area=assessment.area,
        overall_risk=assessment.overall_risk,
        identified_hazards=assessment.identified_hazards,
        mitigation_measures=assessment.mitigation_measures,
        assessed_by=assessment.assessed_by,
        assessed_at=datetime.now()
    )

    session.add(db_assessment)
    await session.commit()
    await session.refresh(db_assessment)
    return db_assessment


# ============== 实时监控 / Real-time Monitoring ==============

@router.get("/monitoring/status")
async def get_monitoring_status(session: AsyncSession = Depends(get_session)):
    """获取安全监控状态 / Get safety monitoring status"""
    # 获取最近24小时的告警
    yesterday = datetime.now() - timedelta(hours=24)

    result = await session.execute(
        select(SafetyAlert).where(SafetyAlert.created_at >= yesterday)
    )
    recent_alerts = result.scalars().all()

    # 按小时统计
    hourly_stats = {}
    for i in range(24):
        hour = (datetime.now() - timedelta(hours=i)).strftime('%H:00')
        hourly_stats[hour] = 0

    for alert in recent_alerts:
        hour = alert.created_at.strftime('%H:00')
        if hour in hourly_stats:
            hourly_stats[hour] += 1

    return {
        "recent_alerts_count": len(recent_alerts),
        "hourly_distribution": hourly_stats,
        "monitoring_active": True,
        "last_check": datetime.now().isoformat()
    }


# ============== AI 安全分析 / AI Safety Analysis ==============

@router.post("/ai-analyze")
async def ai_safety_analysis(
    area: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """
    AI安全分析 / AI Safety Analysis

    使用AI分析安全数据并提供建议
    Uses AI to analyze safety data and provide recommendations
    """
    # 获取最近的安全数据
    week_ago = datetime.now() - timedelta(days=7)

    result = await session.execute(
        select(SafetyAlert).where(SafetyAlert.created_at >= week_ago)
    )
    recent_alerts = result.scalars().all()

    # 构建分析提示
    alert_summary = f"最近7天共有{len(recent_alerts)}条安全告警。"

    if area:
        alert_summary += f"关注区域: {area}。"

    # 这里可以调用AI服务进行深度分析
    # 简化版本返回基础统计
    level_counts = {}
    for alert in recent_alerts:
        level = alert.level.value
        level_counts[level] = level_counts.get(level, 0) + 1

    recommendations = []
    if level_counts.get('emergency', 0) > 0:
        recommendations.append("发现紧急级别告警，建议立即检查相关区域安全状况。")
    if level_counts.get('critical', 0) > 3:
        recommendations.append("严重告警数量较多，建议进行全面的安全风险评估。")
    if len(recent_alerts) > 10:
        recommendations.append("告警频率较高，建议审查现有安全措施和培训程序。")

    return {
        "summary": alert_summary,
        "level_distribution": level_counts,
        "recommendations": recommendations or ["当前安全状况良好，继续保持现有安全措施。"],
        "analyzed_at": datetime.now().isoformat()
    }
