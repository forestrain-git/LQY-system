"""告警规则API测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AlertRule, RuleMetric, RuleOperator


class TestAlertRuleCRUD:
    """测试告警规则CRUD"""

    async def test_create_alert_rule(self, client: AsyncClient):
        """创建规则"""
        rule_data = {
            "metric": "temperature",
            "operator": "gt",
            "threshold": 80.0,
            "duration": 60,
            "enabled": True,
            "description": "测试规则"
        }

        response = await client.post("/api/v1/alert-rules", json=rule_data)
        assert response.status_code == 201
        data = response.json()
        assert data["metric"] == "temperature"
        assert data["threshold"] == 80.0

    async def test_list_alert_rules(self, client: AsyncClient, db_session: AsyncSession):
        """查询规则列表"""
        # 创建规则
        rule = AlertRule(
            metric=RuleMetric.VIBRATION,
            operator=RuleOperator.GT,
            threshold=5.0,
            enabled=True
        )
        db_session.add(rule)
        await db_session.commit()

        response = await client.get("/api/v1/alert-rules")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1

    async def test_update_alert_rule(self, client: AsyncClient, db_session: AsyncSession):
        """更新规则"""
        # 创建规则
        rule = AlertRule(
            metric=RuleMetric.CURRENT,
            operator=RuleOperator.GT,
            threshold=15.0,
            enabled=True
        )
        db_session.add(rule)
        await db_session.commit()

        # 更新
        update_data = {"enabled": False, "threshold": 20.0}
        response = await client.put(f"/api/v1/alert-rules/{rule.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] == False
        assert data["threshold"] == 20.0

    async def test_delete_alert_rule(self, client: AsyncClient, db_session: AsyncSession):
        """删除规则"""
        # 创建规则
        rule = AlertRule(
            metric=RuleMetric.TEMPERATURE,
            operator=RuleOperator.LT,
            threshold=10.0,
            enabled=True
        )
        db_session.add(rule)
        await db_session.commit()

        # 删除
        response = await client.delete(f"/api/v1/alert-rules/{rule.id}")
        assert response.status_code == 204
