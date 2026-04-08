"""
集成测试 / Integration Tests

测试各模块API集成
Tests integration of all module APIs

Author: AI Sprint
Date: 2026-04-07
"""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_session
from app.modules.workflow.models import Staff, Department
from app.modules.dispatch.models import Vehicle, Berth


# 测试客户端 / Test client
@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealth:
    """健康检查测试 / Health check tests"""

    async def test_health_endpoint(self, client: AsyncClient):
        """测试健康检查端点"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestWorkflowAPI:
    """工单模块API测试 / Workflow module API tests"""

    async def test_create_department(self, client: AsyncClient):
        """测试创建部门"""
        response = await client.post("/api/v1/workflow/departments", json={
            "code": "TEST001",
            "name": "测试部门",
            "description": "用于测试的部门"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "TEST001"
        assert data["name"] == "测试部门"

    async def test_list_departments(self, client: AsyncClient):
        """测试获取部门列表"""
        response = await client.get("/api/v1/workflow/departments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_create_staff(self, client: AsyncClient):
        """测试创建人员"""
        response = await client.post("/api/v1/workflow/staff", json={
            "employee_no": "EMP9999",
            "name": "测试人员",
            "role": "operator",
            "phone": "13800138000"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["employee_no"] == "EMP9999"
        assert data["name"] == "测试人员"

    async def test_create_work_order(self, client: AsyncClient):
        """测试创建工单"""
        response = await client.post("/api/v1/workflow/work-orders", json={
            "title": "测试工单",
            "description": "这是一个测试工单",
            "order_type": "inspection",
            "priority": "medium",
            "creator_id": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "测试工单"
        assert data["status"] == "pending"
        assert data["order_no"].startswith("WO")


class TestDispatchAPI:
    """调度模块API测试 / Dispatch module API tests"""

    async def test_list_vehicles(self, client: AsyncClient):
        """测试获取车辆列表"""
        response = await client.get("/api/v1/dispatch/vehicles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_create_vehicle(self, client: AsyncClient):
        """测试创建车辆"""
        response = await client.post("/api/v1/dispatch/vehicles", json={
            "license_plate": "川AT9999",
            "vehicle_type": "domestic",
            "max_capacity": 8.0
        })
        assert response.status_code == 200
        data = response.json()
        assert data["license_plate"] == "川AT9999"

    async def test_list_berths(self, client: AsyncClient):
        """测试获取泊位列表"""
        response = await client.get("/api/v1/dispatch/berths")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_queue_status(self, client: AsyncClient):
        """测试队列状态"""
        response = await client.get("/api/v1/dispatch/queue/status")
        assert response.status_code == 200
        data = response.json()
        assert "queued" in data
        assert "checked_in" in data
        assert "unloading" in data


class TestEquipmentAPI:
    """设备模块API测试 / Equipment module API tests"""

    async def test_list_equipment(self, client: AsyncClient):
        """测试获取设备列表"""
        response = await client.get("/api/v1/equipment")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_create_equipment(self, client: AsyncClient):
        """测试创建设备"""
        response = await client.post("/api/v1/equipment", json={
            "code": "EQ-TEST-001",
            "name": "测试设备",
            "equipment_type": "compressor",
            "location": "测试区域"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "EQ-TEST-001"

    async def test_equipment_stats(self, client: AsyncClient):
        """测试设备统计"""
        response = await client.get("/api/v1/equipment/stats/overview")
        assert response.status_code == 200
        data = response.json()
        assert "by_status" in data
        assert "by_type" in data
        assert "total" in data


class TestSafetyAPI:
    """安全模块API测试 / Safety module API tests"""

    async def test_list_alerts(self, client: AsyncClient):
        """测试获取告警列表"""
        response = await client.get("/api/v1/safety/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_create_alert(self, client: AsyncClient):
        """测试创建告警"""
        response = await client.post("/api/v1/safety/alerts", json={
            "alert_type": "fence_violation",
            "level": "warning",
            "title": "测试告警",
            "description": "这是一个测试告警",
            "location": "测试区域"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "测试告警"
        assert data["alert_code"].startswith("SA")

    async def test_safety_stats(self, client: AsyncClient):
        """测试安全统计"""
        response = await client.get("/api/v1/safety/stats/overview")
        assert response.status_code == 200
        data = response.json()
        assert "by_status" in data
        assert "by_level" in data
        assert "today_count" in data


class TestAIAPI:
    """AI模块API测试 / AI module API tests"""

    async def test_list_conversations(self, client: AsyncClient):
        """测试获取会话列表"""
        response = await client.get("/api/v1/ai/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_create_conversation(self, client: AsyncClient):
        """测试创建会话"""
        response = await client.post("/api/v1/ai/conversations", json={
            "title": "测试会话"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "测试会话"


class TestPredictionsAPI:
    """预测模块API测试 / Predictions module API tests"""

    async def test_waste_volume_prediction(self, client: AsyncClient):
        """测试垃圾量预测"""
        response = await client.get("/api/v1/predictions/waste-volume", params={
            "days": 7
        })
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "method" in data

    async def test_equipment_failure_prediction(self, client: AsyncClient):
        """测试设备故障预测"""
        response = await client.get("/api/v1/predictions/equipment-failure", params={
            "equipment_id": 1
        })
        # 可能返回404如果没有该设备，但API应该正常工作
        assert response.status_code in [200, 404]


# 端到端场景测试 / End-to-end scenario tests
class TestEndToEndScenarios:
    """端到端场景测试 / End-to-end scenario tests"""

    async def test_full_dispatch_flow(self, client: AsyncClient):
        """
        测试完整调度流程:
        1. 创建车辆
        2. 创建调度
        3. 签到
        4. 开始卸货
        5. 完成调度
        """
        # 1. 创建车辆
        vehicle_response = await client.post("/api/v1/dispatch/vehicles", json={
            "license_plate": "川ASCENARIO1",
            "vehicle_type": "domestic",
            "max_capacity": 8.0
        })
        assert vehicle_response.status_code == 200
        vehicle_id = vehicle_response.json()["id"]

        # 2. 创建调度
        schedule_response = await client.post("/api/v1/dispatch/schedules", json={
            "vehicle_id": vehicle_id,
            "appointment_time": datetime.now().isoformat(),
            "expected_waste_type": "domestic"
        })
        assert schedule_response.status_code == 200
        schedule_id = schedule_response.json()["id"]

        # 3. 签到
        checkin_response = await client.post(f"/api/v1/dispatch/schedules/{schedule_id}/checkin")
        assert checkin_response.status_code == 200

        # 4. 开始卸货
        start_response = await client.post(f"/api/v1/dispatch/schedules/{schedule_id}/start-unloading")
        assert start_response.status_code == 200

        # 5. 完成调度
        complete_response = await client.post(
            f"/api/v1/dispatch/schedules/{schedule_id}/complete",
            params={"gross_weight": 5000.0, "tare_weight": 2000.0}
        )
        assert complete_response.status_code == 200
        data = complete_response.json()
        assert data["net_weight"] == 3000.0

    async def test_work_order_lifecycle(self, client: AsyncClient):
        """
        测试工单生命周期:
        1. 创建工单
        2. 分配工单
        3. 开始工单
        4. 完成工单
        """
        # 创建执行人
        staff_response = await client.post("/api/v1/workflow/staff", json={
            "employee_no": "EMP_SCEN",
            "name": "场景测试人员"
        })
        staff_id = staff_response.json()["id"]

        # 1. 创建工单
        order_response = await client.post("/api/v1/workflow/work-orders", json={
            "title": "场景测试工单",
            "order_type": "maintenance",
            "priority": "high",
            "creator_id": staff_id
        })
        assert order_response.status_code == 200
        order_id = order_response.json()["id"]

        # 2. 分配工单
        assign_response = await client.post(
            f"/api/v1/workflow/work-orders/{order_id}/assign",
            params={"assignee_id": staff_id}
        )
        assert assign_response.status_code == 200

        # 3. 开始工单
        start_response = await client.post(f"/api/v1/workflow/work-orders/{order_id}/start")
        assert start_response.status_code == 200

        # 4. 完成工单
        complete_response = await client.post(
            f"/api/v1/workflow/work-orders/{order_id}/complete",
            params={"result_summary": "测试完成", "satisfaction": 5}
        )
        assert complete_response.status_code == 200
