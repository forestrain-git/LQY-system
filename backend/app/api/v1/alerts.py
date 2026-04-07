"""告警管理API

告警的查询、确认、解决等操作
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Alert, AlertLevel, AlertMetric, AlertStatus, Device
from app.redis import get_redis
import json
from app.schemas import AlertResponse, ListResponse, Pagination

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["告警管理"])


@router.get("", response_model=ListResponse[AlertResponse])
async def list_alerts(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    device_id: Optional[int] = Query(None, description="设备ID过滤"),
    level: Optional[str] = Query(None, description="告警级别过滤，支持多选（critical,warning,info）"),
    status: Optional[str] = Query(None, description="状态过滤，支持多选（active,acknowledged,resolved）"),
    metric: Optional[str] = Query(None, description="指标过滤，支持多选（temperature,vibration,current）"),
    start: Optional[datetime] = Query(None, description="开始时间（ISO8601）"),
    end: Optional[datetime] = Query(None, description="结束时间"),
    db: AsyncSession = Depends(get_session),
):
    """查询告警列表

    支持分页、过滤、时间范围查询
    """
    try:
        # 构建查询条件
        conditions = []

        if device_id:
            conditions.append(Alert.device_id == device_id)

        if level:
            levels = level.split(",")
            conditions.append(Alert.level.in_(levels))

        if status:
            statuses = status.split(",")
            conditions.append(Alert.status.in_(statuses))

        if metric:
            metrics = metric.split(",")
            conditions.append(Alert.metric.in_(metrics))

        if start:
            conditions.append(Alert.created_at >= start)

        if end:
            conditions.append(Alert.created_at <= end)

        # 主查询
        query = select(Alert, Device.name.label("device_name")).join(
            Device, Alert.device_id == Device.id
        )

        if conditions:
            query = query.where(and_(*conditions))

        # 统计总数
        count_query = select(func.count(Alert.id)).join(
            Device, Alert.device_id == Device.id
        )
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页和排序
        query = query.order_by(Alert.created_at.desc()).offset((page - 1) * size).limit(size)

        result = await db.execute(query)
        rows = result.all()

        # 构建响应数据
        alerts = []
        for alert, device_name in rows:
            # 计算持续时间
            duration = None
            if alert.resolved_at:
                duration = int((alert.resolved_at - alert.created_at).total_seconds())
            else:
                duration = int((datetime.now(timezone.utc) - alert.created_at).total_seconds())

            alert_data = AlertResponse(
                id=alert.id,
                device_id=alert.device_id,
                device_name=device_name,
                alert_type=alert.alert_type,
                metric=alert.metric,
                message=alert.message,
                level=alert.level,
                status=alert.status,
                created_at=alert.created_at,
                acknowledged_at=alert.acknowledged_at,
                resolved_at=alert.resolved_at,
                duration_seconds=duration
            )
            alerts.append(alert_data)

        # 分页信息
        pages = (total + size - 1) // size
        pagination = Pagination(page=page, size=size, total=total, pages=pages)

        return ListResponse(data=alerts, pagination=pagination)

    except Exception as e:
        logger.error(f"查询告警列表失败: {e}")
        raise HTTPException(status_code=500, detail="查询告警列表失败")


@router.get("/stats")
async def get_alert_stats(
    db: AsyncSession = Depends(get_session),
):
    """获取告警统计"""
    try:
        # 当前活跃告警数
        active_result = await db.execute(
            select(func.count(Alert.id)).where(Alert.status == AlertStatus.ACTIVE)
        )
        total_active = active_result.scalar()

        # 今日告警数
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await db.execute(
            select(func.count(Alert.id)).where(Alert.created_at >= today)
        )
        total_today = today_result.scalar()

        # 按级别统计
        level_stats = {}
        for level in AlertLevel:
            result = await db.execute(
                select(func.count(Alert.id)).where(Alert.level == level)
            )
            level_stats[level.value] = result.scalar()

        # 按指标统计
        metric_stats = {}
        for metric in AlertMetric:
            result = await db.execute(
                select(func.count(Alert.id)).where(Alert.metric == metric)
            )
            metric_stats[metric.value] = result.scalar()

        return {
            "total_active": total_active,
            "total_today": total_today,
            "by_level": level_stats,
            "by_metric": metric_stats
        }

    except Exception as e:
        logger.error(f"获取告警统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取告警统计失败")


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_session),
):
    """确认告警"""
    try:
        # 查询告警
        result = await db.execute(
            select(Alert, Device.name.label("device_name"))
            .join(Device, Alert.device_id == Device.id)
            .where(Alert.id == alert_id)
        )
        row = result.one_or_none()

        if not row:
            raise HTTPException(status_code=404, detail="告警不存在")

        alert, device_name = row

        # 幂等：如果已经是acknowledged或resolved，直接返回
        if alert.status in [AlertStatus.ACKNOWLEDGED, AlertStatus.RESOLVED]:
            duration = None
            if alert.resolved_at:
                duration = int((alert.resolved_at - alert.created_at).total_seconds())
            else:
                duration = int((datetime.now(timezone.utc) - alert.created_at).total_seconds())

            return AlertResponse(
                id=alert.id,
                device_id=alert.device_id,
                device_name=device_name,
                alert_type=alert.alert_type,
                metric=alert.metric,
                message=alert.message,
                level=alert.level,
                status=alert.status,
                created_at=alert.created_at,
                acknowledged_at=alert.acknowledged_at,
                resolved_at=alert.resolved_at,
                duration_seconds=duration
            )

        # 更新状态
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(alert)

        # 计算持续时间
        duration = int((datetime.now(timezone.utc) - alert.created_at).total_seconds())

        logger.info(f"告警已确认: {alert_id}")
        
        # 广播状态更新
        await broadcast_alert_update(alert_id, "acknowledged", alert.acknowledged_at.isoformat())

        return AlertResponse(
            id=alert.id,
            device_id=alert.device_id,
            device_name=device_name,
            alert_type=alert.alert_type,
            metric=alert.metric,
            message=alert.message,
            level=alert.level,
            status=alert.status,
            created_at=alert.created_at,
            acknowledged_at=alert.acknowledged_at,
            resolved_at=alert.resolved_at,
            duration_seconds=duration
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"确认告警失败: {e}")
        raise HTTPException(status_code=500, detail="确认告警失败")


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_session),
):
    """解决告警"""
    try:
        # 查询告警
        result = await db.execute(
            select(Alert, Device.name.label("device_name"))
            .join(Device, Alert.device_id == Device.id)
            .where(Alert.id == alert_id)
        )
        row = result.one_or_none()

        if not row:
            raise HTTPException(status_code=404, detail="告警不存在")

        alert, device_name = row

        # 幂等：如果已经是resolved，直接返回
        if alert.status == AlertStatus.RESOLVED:
            duration = int((alert.resolved_at - alert.created_at).total_seconds())
            return AlertResponse(
                id=alert.id,
                device_id=alert.device_id,
                device_name=device_name,
                alert_type=alert.alert_type,
                metric=alert.metric,
                message=alert.message,
                level=alert.level,
                status=alert.status,
                created_at=alert.created_at,
                acknowledged_at=alert.acknowledged_at,
                resolved_at=alert.resolved_at,
                duration_seconds=duration
            )

        # 更新状态
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(alert)

        # 计算持续时间
        duration = int((alert.resolved_at - alert.created_at).total_seconds())

        logger.info(f"告警已解决: {alert_id}")
        
        # 广播状态更新
        await broadcast_alert_update(alert_id, "resolved", alert.resolved_at.isoformat())

        return AlertResponse(
            id=alert.id,
            device_id=alert.device_id,
            device_name=device_name,
            alert_type=alert.alert_type,
            metric=alert.metric,
            message=alert.message,
            level=alert.level,
            status=alert.status,
            created_at=alert.created_at,
            acknowledged_at=alert.acknowledged_at,
            resolved_at=alert.resolved_at,
            duration_seconds=duration
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"解决告警失败: {e}")
        raise HTTPException(status_code=500, detail="解决告警失败")


@router.post("/acknowledge-batch")
async def acknowledge_batch(
    request: dict,
    db: AsyncSession = Depends(get_session),
):
    """批量确认告警

    Request Body:
        {"ids": [1, 2, 3]}
    """
    try:
        ids = request.get("ids", [])
        if not ids:
            return {"updated": 0}

        # 批量更新
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Alert).where(Alert.id.in_(ids))
        )
        alerts = result.scalars().all()

        updated_count = 0
        for alert in alerts:
            if alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = now
                updated_count += 1

        await db.commit()

        logger.info(f"批量确认告警: {updated_count} 条")

        return {"updated": updated_count}

    except Exception as e:
        logger.error(f"批量确认告警失败: {e}")
        raise HTTPException(status_code=500, detail="批量确认告警失败")


# 辅助函数：广播告警更新
async def broadcast_alert_update(alert_id: int, status: str, timestamp: str):
    """广播告警状态更新到WebSocket"""
    try:
        redis = get_redis()
        if redis:
            import json
            message = {
                "type": "alert_updated",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "id": alert_id,
                    "status": status,
                    "updated_at": timestamp
                }
            }
            await redis.publish("alerts:new", json.dumps(message))
    except Exception as e:
        logger.error(f"广播告警更新失败: {e}")
