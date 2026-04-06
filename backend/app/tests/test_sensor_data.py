"""传感器数据API测试

测试传感器数据的写入和导出功能
"""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Device, DeviceStatus, SensorData


class TestCreateSensorData:
    """测试创建传感器数据"""

    async def test_create_sensor_data_success(self, client: AsyncClient, db_session: AsyncSession):
        """单条创建"""
        # 创建设备
        device = Device(name="测试设备", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.commit()

        # 创建传感器数据
        data = {
            "device_id": device.id,
            "temperature": 65.5,
            "vibration": 2.3,
            "current": 12.5,
        }
        response = await client.post("/api/v1/sensor-data", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 0
        assert result["data"]["count"] == 1
        assert len(result["data"]["ids"]) == 1

    async def test_create_sensor_data_batch(self, client: AsyncClient, db_session: AsyncSession):
        """批量创建（最多100）"""
        # 创建设备
        device = Device(name="批量设备", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.commit()

        # 批量创建数据
        data_list = [
            {
                "device_id": device.id,
                "temperature": 60.0 + i,
                "vibration": 1.0 + i * 0.1,
                "current": 10.0 + i,
            }
            for i in range(10)
        ]
        response = await client.post("/api/v1/sensor-data", json=data_list)
        assert response.status_code == 200
        result = response.json()
        assert result["data"]["count"] == 10

    async def test_create_sensor_data_too_many(self, client: AsyncClient, db_session: AsyncSession):
        """超过100条返回400"""
        device = Device(name="超限设备", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.commit()

        data_list = [{"device_id": device.id, "temperature": 60.0}] * 101
        response = await client.post("/api/v1/sensor-data", json=data_list)
        assert response.status_code == 400

    async def test_create_sensor_data_device_disabled(self, client: AsyncClient, db_session: AsyncSession):
        """设备disabled返回400"""
        # 创建disabled设备
        device = Device(name="禁用设备", type="compressor", status=DeviceStatus.DISABLED)
        db_session.add(device)
        await db_session.commit()

        data = {
            "device_id": device.id,
            "temperature": 65.5,
        }
        response = await client.post("/api/v1/sensor-data", json=data)
        assert response.status_code == 400
        result = response.json()
        assert "不存在或已禁用" in result["message"]


class TestExportSensorData:
    """测试导出传感器数据"""

    async def test_export_sensor_data(self, client: AsyncClient, db_session: AsyncSession):
        """CSV导出"""
        from datetime import datetime, timezone

        # 创建设备和数据
        device = Device(name="导出设备", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.flush()

        sensor_data = SensorData(
            device_id=device.id,
            temperature=65.5,
            vibration=2.3,
            current=12.5,
            timestamp=datetime.now(timezone.utc),
        )
        db_session.add(sensor_data)
        await db_session.commit()

        # 导出CSV
        response = await client.get(f"/api/v1/sensor-data/export?device_id={device.id}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

        # 验证CSV内容
        content = response.content.decode("utf-8-sig")
        assert "timestamp,device_name,temperature,vibration,current" in content
        assert "导出设备" in content
        assert "65.5" in content
