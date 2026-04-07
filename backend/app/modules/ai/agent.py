"""
AI Agent模块 / AI Agent Module

提供自主决策和自动化任务执行
Provides autonomous decision making and automated task execution

Author: AI Sprint
Date: 2026-04-07
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.ai.service import get_ai_service
from app.modules.safety.models import SafetyAlert, SafetyAlertLevel, SafetyAlertStatus
from app.modules.workflow.models import WorkOrder, WorkOrderStatus, WorkOrderPriority
from app.modules.dispatch.models import Schedule, ScheduleStatus


class AgentActionType(str, Enum):
    """Agent动作类型 / Agent Action Type"""
    CREATE_WORK_ORDER = "create_work_order"
    ALERT_ACKNOWLEDGE = "alert_acknowledge"
    DISPATCH_OPTIMIZE = "dispatch_optimize"
    EQUIPMENT_MAINTENANCE = "equipment_maintenance"
    NOTIFY_STAFF = "notify_staff"
    ANALYZE_DATA = "analyze_data"


@dataclass
class AgentAction:
    """Agent动作 / Agent Action"""
    action_type: AgentActionType
    target_id: int
    target_type: str
    parameters: Dict[str, Any]
    reason: str
    confidence: float


class AIAgent:
    """
    AI代理 / AI Agent

    自主监控和决策代理，能够：
    - 自动响应安全告警
    - 优化调度决策
    - 创建设备维护工单
    - 生成数据报告
    """

    def __init__(self):
        self.ai_service = get_ai_service()
        self.action_history: List[AgentAction] = []

    async def process_safety_alert(
        self,
        session: AsyncSession,
        alert_id: int
    ) -> Optional[AgentAction]:
        """
        处理安全告警 / Process safety alert

        根据告警级别和类型自动决定处理方式
        Automatically decides handling method based on alert level and type
        """
        alert = await session.get(SafetyAlert, alert_id)
        if not alert:
            return None

        # 根据级别决定动作 / Decide action based on level
        if alert.level == SafetyAlertLevel.EMERGENCY:
            # 紧急告警：创建高优先级工单并通知相关人员
            action = AgentAction(
                action_type=AgentActionType.CREATE_WORK_ORDER,
                target_id=alert_id,
                target_type="safety_alert",
                parameters={
                    "priority": "urgent",
                    "title": f"【紧急】处理安全告警: {alert.title}",
                    "description": alert.description,
                    "equipment_id": alert.equipment_id
                },
                reason="紧急安全告警需要立即处理",
                confidence=0.95
            )
        elif alert.level == SafetyAlertLevel.CRITICAL:
            # 严重告警：创建高优先级工单
            action = AgentAction(
                action_type=AgentActionType.CREATE_WORK_ORDER,
                target_id=alert_id,
                target_type="safety_alert",
                parameters={
                    "priority": "high",
                    "title": f"处理安全告警: {alert.title}",
                    "description": alert.description
                },
                reason="严重安全告警需要尽快处理",
                confidence=0.85
            )
        elif alert.level == SafetyAlertLevel.WARNING:
            # 警告：添加到监控队列
            action = AgentAction(
                action_type=AgentActionType.ALERT_ACKNOWLEDGE,
                target_id=alert_id,
                target_type="safety_alert",
                parameters={"auto_acknowledge": True},
                reason="警告级别，自动确认并监控",
                confidence=0.70
            )
        else:
            # 提示级别：仅记录
            action = AgentAction(
                action_type=AgentActionType.ANALYZE_DATA,
                target_id=alert_id,
                target_type="safety_alert",
                parameters={"log_only": True},
                reason="提示级别，仅记录分析",
                confidence=0.50
            )

        self.action_history.append(action)
        return action

    async def optimize_dispatch(
        self,
        session: AsyncSession
    ) -> List[AgentAction]:
        """
        优化调度 / Optimize dispatch

        分析当前调度状况并提供优化建议
        Analyzes current dispatch status and provides optimization suggestions
        """
        actions = []

        # 获取排队中的调度
        result = await session.execute(
            select(Schedule).where(Schedule.status == ScheduleStatus.QUEUED)
        )
        queued_schedules = result.scalars().all()

        # 获取进行中的调度
        result = await session.execute(
            select(Schedule).where(Schedule.status == ScheduleStatus.UNLOADING)
        )
        unloading_schedules = result.scalars().all()

        # 如果队列过长，建议优化
        if len(queued_schedules) > 5:
            actions.append(AgentAction(
                action_type=AgentActionType.DISPATCH_OPTIMIZE,
                target_id=0,
                target_type="dispatch_system",
                parameters={
                    "action": "process_queue",
                    "queued_count": len(queued_schedules)
                },
                reason=f"队列车辆过多({len(queued_schedules)}辆)，建议加快处理",
                confidence=0.80
            ))

        # 如果有长时间未完成的卸货，检查是否有问题
        for schedule in unloading_schedules:
            if schedule.unloading_started_at:
                duration = (datetime.now() - schedule.unloading_started_at).total_seconds() / 60
                if duration > 30:  # 超过30分钟
                    actions.append(AgentAction(
                        action_type=AgentActionType.NOTIFY_STAFF,
                        target_id=schedule.id,
                        target_type="schedule",
                        parameters={
                            "message": f"调度{schedule.id}卸货时间超过30分钟，请检查",
                            "priority": "medium"
                        },
                        reason="卸货时间过长，可能存在异常",
                        confidence=0.75
                    ))

        self.action_history.extend(actions)
        return actions

    async def predict_equipment_maintenance(
        self,
        session: AsyncSession,
        equipment_id: int
    ) -> Optional[AgentAction]:
        """
        预测性维护 / Predictive maintenance

        基于设备数据预测维护需求
        Predicts maintenance needs based on equipment data
        """
        from app.modules.equipment.models import Equipment, EquipmentStatus

        equipment = await session.get(Equipment, equipment_id)
        if not equipment:
            return None

        # 简单的预测逻辑 / Simple prediction logic
        needs_maintenance = False
        reason_parts = []

        # 检查运行时长
        if equipment.total_operating_hours > 1000:
            needs_maintenance = True
            reason_parts.append(f"运行时长超过1000小时({equipment.total_operating_hours:.0f})")

        # 检查上次维护时间
        if equipment.last_maintenance_at:
            days_since = (datetime.now() - equipment.last_maintenance_at).days
            if days_since > 90:
                needs_maintenance = True
                reason_parts.append(f"距上次维护已超过90天({days_since}天)")
        else:
            needs_maintenance = True
            reason_parts.append("从未进行过维护")

        # 检查状态
        if equipment.status == EquipmentStatus.WARNING:
            needs_maintenance = True
            reason_parts.append("设备状态为警告")

        if needs_maintenance:
            action = AgentAction(
                action_type=AgentActionType.EQUIPMENT_MAINTENANCE,
                target_id=equipment_id,
                target_type="equipment",
                parameters={
                    "maintenance_type": "preventive",
                    "priority": "medium",
                    "title": f"{equipment.name} 预防性维护",
                    "description": "基于AI分析，建议对该设备进行预防性维护。原因：" + "；".join(reason_parts)
                },
                reason="；".join(reason_parts),
                confidence=0.80
            )
            self.action_history.append(action)
            return action

        return None

    async def generate_daily_report(
        self,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        生成日报 / Generate daily report

        汇总系统运行状况
        Summarizes system operation status
        """
        # 获取今日数据
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # 安全告警统计
        from app.modules.safety.models import SafetyAlert
        result = await session.execute(
            select(SafetyAlert).where(SafetyAlert.created_at >= today_start)
        )
        today_alerts = result.scalars().all()

        # 工单统计
        result = await session.execute(
            select(WorkOrder).where(WorkOrder.created_at >= today_start)
        )
        today_orders = result.scalars().all()

        # 调度统计
        result = await session.execute(
            select(Schedule).where(Schedule.created_at >= today_start)
        )
        today_schedules = result.scalars().all()

        report = {
            "date": today_start.strftime("%Y-%m-%d"),
            "summary": {
                "total_alerts": len(today_alerts),
                "total_work_orders": len(today_orders),
                "total_schedules": len(today_schedules)
            },
            "alerts_by_level": {},
            "work_orders_by_status": {},
            "recommendations": []
        }

        # 统计告警级别
        for alert in today_alerts:
            level = alert.level.value
            report["alerts_by_level"][level] = report["alerts_by_level"].get(level, 0) + 1

        # 统计工单状态
        for order in today_orders:
            status = order.status.value
            report["work_orders_by_status"][status] = report["work_orders_by_status"].get(status, 0) + 1

        # 生成建议
        if report["alerts_by_level"].get('emergency', 0) > 0:
            report["recommendations"].append("今日发生紧急安全事件，建议召开安全复盘会议。")
        if len(today_orders) > 20:
            report["recommendations"].append("工单量较大，建议评估人员配置是否充足。")
        if report["summary"]["total_schedules"] > 50:
            report["recommendations"].append("调度量高，建议检查设备负荷和人员疲劳度。")

        if not report["recommendations"]:
            report["recommendations"].append("今日运行状况良好，请继续保持。")

        return report

    def get_recent_actions(
        self,
        limit: int = 10
    ) -> List[AgentAction]:
        """获取最近的Agent动作 / Get recent agent actions"""
        return self.action_history[-limit:]

    def get_statistics(self) -> Dict[str, int]:
        """获取Agent统计 / Get agent statistics"""
        stats = {action_type.value: 0 for action_type in AgentActionType}
        for action in self.action_history:
            stats[action.action_type.value] += 1
        return stats


# 全局Agent实例
_agent: Optional[AIAgent] = None


def get_ai_agent() -> AIAgent:
    """获取AI Agent单例 / Get AI Agent singleton"""
    global _agent
    if _agent is None:
        _agent = AIAgent()
    return _agent
