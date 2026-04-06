"""设备API测试

测试设备的CRUD操作和查询功能
"""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Device, DeviceStatus, SensorData


class TestCreateDevice:
    """测试创建设备"""

    async def test_create_device_success(self, client: AsyncClient, sample_device_data):
        """正常创建设备，返回201"""
        response = await client.post("/api/v1/devices", json=sample_device_data)

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == sample_device_data["name"]
        assert data["data"]["type"] == sample_device_data["type"]
        assert "id" in data["data"]

    async def test_create_device_duplicate_name(self, client: AsyncClient, sample_device_data):
        """重复名称，返回409"""
        # 先创建第一个设备
        response1 = await client.post("/api/v1/devices", json=sample_device_data)
        assert response1.status_code == 201

        # 再创建同名设备
        response2 = await client.post("/api/v1/devices", json=sample_device_data)
        assert response2.status_code == 409
        data = response2.json()
        assert data["code"] == 409


class TestListDevices:
    """测试设备列表查询"""

    async def test_list_devices_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """分页正常"""
        # 先创建多个设备
        for i in range(5):
            device = Device(
                name=f"设备-{i:03d}",
                type="compressor",
                status=DeviceStatus.ONLINE,
            )
            db_session.add(device)
        await db_session.commit()

        # 测试分页
        response = await client.get("/api/v1/devices?page=1&size=3")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 3
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["size"] == 3
        assert data["pagination"]["total"] == 5

    async def test_list_devices_filter_by_status(self, client: AsyncClient, db_session: AsyncSession):
        """状态过滤"""
        # 创建不同状态的设备
        device1 = Device(name="在线设备", type="compressor", status=DeviceStatus.ONLINE)
        device2 = Device(name="离线设备", type="compressor", status=DeviceStatus.OFFLINE)
        db_session.add_all([device1, device2])
        await db_session.commit()

        # 过滤在线设备
        response = await client.get("/api/v1/devices?status=online")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["status"] == "online"

    async def test_list_devices_search_by_name(self, client: AsyncClient, db_session: AsyncSession):
        """名称模糊搜索"""
        # 创建设备
        device1 = Device(name="压缩机-A01", type="compressor", status=DeviceStatus.ONLINE)
        device2 = Device(name="泵-B02", type="pump", status=DeviceStatus.ONLINE)
        db_session.add_all([device1, device2])
        await db_session.commit()

        # 搜索包含"压缩机"的设备
        response = await client.get("/api/v1/devices?name=压缩机")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert "压缩机" in data["data"][0]["name"]


class TestGetDevice:
    """测试获取单个设备"""

    async def test_get_device_success(self, client: AsyncClient, db_session: AsyncSession):
        """获取成功，包含latest_data"""
        # 创建设备和传感器数据
        device = Device(name="测试设备", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.flush()

        sensor_data = SensorData(
            device_id=device.id,
            temperature=70.0,
            vibration=1.5,
            current=10.0,
        )
        db_session.add(sensor_data)
        await db_session.commit()

        # 获取设备详情
        response = await client.get(f"/api/v1/devices/{device.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "测试设备"
        assert data["data"]["latest_sensor_data"] is not None
        assert data["data"]["latest_sensor_data"]["temperature"] == 70.0

    async def test_get_device_not_found(self, client: AsyncClient):
        """不存在，返回404"""
        response = await client.get("/api/v1/devices/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == 404


class TestUpdateDevice:
    """测试更新设备"""

    async def test_update_device_success(self, client: AsyncClient, db_session: AsyncSession):
        """更新成功"""
        # 创建设备
        device = Device(name="原名称", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.commit()

        # 更新设备
        update_data = {"name": "新名称", "location": "新位置"}
        response = await client.put(f"/api/v1/devices/{device.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "新名称"
        assert data["data"]["location"] == "新位置"


class TestDeleteDevice:
    """测试删除设备（软删除）"""

    async def test_delete_device_actually_disables(self, client: AsyncClient, db_session: AsyncSession):
        """删除后status=disabled"""
        # 创建设备
        device = Device(name="待删除", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.commit()

        # 删除设备
        response = await client.delete(f"/api/v1/devices/{device.id}")
        assert response.status_code == 204

        # 验证状态变为disabled
        await db_session.refresh(device)
        assert device.status == DeviceStatus.DISABLED

        # 再次删除（幂等）
        response2 = await client.delete(f"/api/v1/devices/{device.id}")
        assert response2.status_code == 204


class TestDeviceStats:
    """测试设备统计"""

    async def test_get_device_stats(self, client: AsyncClient, db_session: AsyncSession):
        """统计正确"""
        # 创建设备和传感器数据
        device = Device(name="统计设备", type="compressor", status=DeviceStatus.ONLINE)
        db_session.add(device)
        await db_session.flush()

        # 添加今日数据
        from datetime import datetime, timezone
        sensor_data1 = SensorData(
            device_id=device.id,
            temperature=60.0,
            vibration=1.0,
            current=10.0,
            timestamp=datetime.now(timezone.utc),
        )
        sensor_data2 = SensorData(
            device_id=device.id,
            temperature=70.0,
            vibration=2.0,
            current=15.0,
            timestamp=datetime.now(timezone.utc),
        )
        db_session.add_all([sensor_data1, sensor_data2])
        await db_session.commit()

        # 获取统计
        response = await client.get(f"/api/v1/devices/{device.id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total_records"] == 2
        assert data["data"]["avg_temperature"] == 65.0
        assert data["data"]["avg_vibration"] == 1.5
        assert data["data"]["avg_current"] == 12.5
