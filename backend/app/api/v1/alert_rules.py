"""告警规则管理API

告警规则的CRUD操作
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import AlertRule, Device
from app.schemas import (
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
    ListResponse,
    Pagination,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alert-rules", tags=["告警规则"])


@router.get("", response_model=ListResponse[AlertRuleResponse])
async def list_alert_rules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    enabled: Optional[bool] = Query(None, description="是否启用"),
    db: AsyncSession = Depends(get_session),
):
    """查询告警规则列表"""
    try:
        # 构建查询
        query = select(AlertRule, Device.name.label("device_name")).outerjoin(
            Device, AlertRule.device_id == Device.id
        )

        if enabled is not None:
            query = query.where(AlertRule.enabled == enabled)

        # 统计总数
        count_query = select(AlertRule)
        if enabled is not None:
            count_query = count_query.where(AlertRule.enabled == enabled)
        
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        # 分页
        query = query.order_by(AlertRule.id.desc()).offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        rows = result.all()

        # 构建响应
        rules = []
        for rule, device_name in rows:
            rule_data = AlertRuleResponse(
                id=rule.id,
                device_id=rule.device_id,
                device_name=device_name,
                metric=rule.metric,
                operator=rule.operator,
                threshold=rule.threshold,
                duration=rule.duration,
                enabled=rule.enabled,
                description=rule.description
            )
            rules.append(rule_data)

        pages = (total + size - 1) // size
        pagination = Pagination(page=page, size=size, total=total, pages=pages)

        return ListResponse(data=rules, pagination=pagination)

    except Exception as e:
        logger.error(f"查询告警规则失败: {e}")
        raise HTTPException(status_code=500, detail="查询告警规则失败")


@router.post("", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: AsyncSession = Depends(get_session),
):
    """创建告警规则"""
    try:
        # 验证：metric+operator+threshold组合不能重复
        existing = await db.execute(
            select(AlertRule).where(
                and_(
                    AlertRule.metric == rule_data.metric,
                    AlertRule.operator == rule_data.operator,
                    AlertRule.threshold == rule_data.threshold,
                    AlertRule.device_id == rule_data.device_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="相同的告警规则已存在"
            )

        # 创建设备
        rule = AlertRule(
            device_id=rule_data.device_id,
            metric=rule_data.metric,
            operator=rule_data.operator,
            threshold=rule_data.threshold,
            duration=rule_data.duration,
            enabled=rule_data.enabled,
            description=rule_data.description
        )

        db.add(rule)
        await db.commit()
        await db.refresh(rule)

        # 获取设备名称
        device_name = None
        if rule.device_id:
            device = await db.get(Device, rule.device_id)
            if device:
                device_name = device.name

        logger.info(f"告警规则已创建: {rule.id}")

        return AlertRuleResponse(
            id=rule.id,
            device_id=rule.device_id,
            device_name=device_name,
            metric=rule.metric,
            operator=rule.operator,
            threshold=rule.threshold,
            duration=rule.duration,
            enabled=rule.enabled,
            description=rule.description
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建告警规则失败: {e}")
        raise HTTPException(status_code=500, detail="创建告警规则失败")


@router.put("/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: int,
    rule_data: AlertRuleUpdate,
    db: AsyncSession = Depends(get_session),
):
    """更新告警规则"""
    try:
        # 查询规则
        result = await db.execute(
            select(AlertRule, Device.name.label("device_name"))
            .outerjoin(Device, AlertRule.device_id == Device.id)
            .where(AlertRule.id == rule_id)
        )
        row = result.one_or_none()

        if not row:
            raise HTTPException(status_code=404, detail="告警规则不存在")

        rule, device_name = row

        # 更新字段
        if rule_data.device_id is not None:
            rule.device_id = rule_data.device_id
        if rule_data.metric is not None:
            rule.metric = rule_data.metric
        if rule_data.operator is not None:
            rule.operator = rule_data.operator
        if rule_data.threshold is not None:
            rule.threshold = rule_data.threshold
        if rule_data.duration is not None:
            rule.duration = rule_data.duration
        if rule_data.enabled is not None:
            rule.enabled = rule_data.enabled
        if rule_data.description is not None:
            rule.description = rule_data.description

        await db.commit()
        await db.refresh(rule)

        # 重新获取设备名称
        if rule.device_id:
            device = await db.get(Device, rule.device_id)
            device_name = device.name if device else None

        logger.info(f"告警规则已更新: {rule_id}")

        return AlertRuleResponse(
            id=rule.id,
            device_id=rule.device_id,
            device_name=device_name,
            metric=rule.metric,
            operator=rule.operator,
            threshold=rule.threshold,
            duration=rule.duration,
            enabled=rule.enabled,
            description=rule.description
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新告警规则失败: {e}")
        raise HTTPException(status_code=500, detail="更新告警规则失败")


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_session),
):
    """删除告警规则"""
    try:
        # 查询规则
        rule = await db.get(AlertRule, rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="告警规则不存在")

        # 删除
        await db.delete(rule)
        await db.commit()

        logger.info(f"告警规则已删除: {rule_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除告警规则失败: {e}")
        raise HTTPException(status_code=500, detail="删除告警规则失败")
