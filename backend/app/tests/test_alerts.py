"""告警API测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Alert, AlertLevel, AlertMetric, AlertStatus, AlertType, Device, DeviceStatus


class TestListAlerts:
    """测试告警列表查询"""

    async def test_list_alerts_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """分页查询"""
        # 创建设备和告警
        device = Device(name="测试设备", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.flush()

        for i in range(5):
            alert = Alert(
                device_id=device.id,
                alert_type=AlertType.THRESHOLD,
                metric=AlertMetric.TEMPERATURE,
                message=f"告警{i}",
                level=AlertLevel.WARNING
            )
            db_session.add(alert)
        await db_session.commit()

        # 测试分页
        response = await client.get("/api/v1/alerts?page=1&size=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3
        assert data["pagination"]["total"] == 5

    async def test_list_alerts_filter_by_level(self, client: AsyncClient, db_session: AsyncSession):
        """级别过滤"""
        device = Device(name="测试设备2", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.flush()

        # 创建不同级别的告警
        alert1 = Alert(device_id=device.id, metric=AlertMetric.TEMPERATURE, message="Critical", level=AlertLevel.CRITICAL)
        alert2 = Alert(device_id=device.id, metric=AlertMetric.TEMPERATURE, message="Warning", level=AlertLevel.WARNING)
        db_session.add_all([alert1, alert2])
        await db_session.commit()

        # 过滤Critical
        response = await client.get("/api/v1/alerts?level=critical")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["level"] == "critical"


class TestAlertLifecycle:
    """测试告警生命周期"""

    async def test_acknowledge_alert_success(self, client: AsyncClient, db_session: AsyncSession):
        """确认告警"""
        # 创建设备和告警
        device = Device(name="测试设备3", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.flush()

        alert = Alert(
            device_id=device.id,
            metric=AlertMetric.TEMPERATURE,
            message="测试告警",
            level=AlertLevel.WARNING,
            status=AlertStatus.ACTIVE
        )
        db_session.add(alert)
        await db_session.commit()

        # 确认告警
        response = await client.post(f"/api/v1/alerts/{alert.id}/acknowledge")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "acknowledged"
        assert data["acknowledged_at"] is not None

    async def test_resolve_alert_success(self, client: AsyncClient, db_session: AsyncSession):
        """解决告警"""
        # 创建设备和告警
        device = Device(name="测试设备4", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.flush()

        alert = Alert(
            device_id=device.id,
            metric=AlertMetric.VIBRATION,
            message="振动异常",
            level=AlertLevel.CRITICAL,
            status=AlertStatus.ACTIVE
        )
        db_session.add(alert)
        await db_session.commit()

        # 解决告警
        response = await client.post(f"/api/v1/alerts/{alert.id}/resolve")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"
        assert data["resolved_at"] is not None


class TestAlertStats:
    """测试告警统计"""

    async def test_get_alert_stats(self, client: AsyncClient, db_session: AsyncSession):
        """统计接口"""
        device = Device(name="测试设备5", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.flush()

        # 创建测试数据
        alert1 = Alert(device_id=device.id, metric=AlertMetric.TEMPERATURE, message="T1", level=AlertLevel.CRITICAL)
        alert2 = Alert(device_id=device.id, metric=AlertMetric.VIBRATION, message="V1", level=AlertLevel.WARNING)
        db_session.add_all([alert1, alert2])
        await db_session.commit()

        response = await client.get("/api/v1/alerts/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_active" in data
        assert "by_level" in data
        assert "by_metric" in data
