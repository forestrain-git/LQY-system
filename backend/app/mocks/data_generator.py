"""
Mock数据生成器 / Mock Data Generator

生成测试用的车辆、泊位、人员、工单等数据
Generates test data for vehicles, berths, staff, work orders, etc.

Author: AI Sprint
Date: 2026-04-07
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict

from app.modules.dispatch.models import (
    Vehicle, VehicleType, VehicleStatus,
    Berth, BerthType, BerthStatus,
    Schedule, ScheduleStatus
)
from app.modules.workflow.models import (
    Staff, StaffRole, StaffStatus,
    Department, WorkOrder, WorkOrderType, WorkOrderStatus, WorkOrderPriority,
    WorkOrderTask, TaskStatus
)


class MockDataGenerator:
    """
    Mock数据生成器 / Mock Data Generator

    生成符合业务场景的模拟数据
    Generates simulated data that matches business scenarios
    """

    # 中文姓名库 / Chinese name library
    SURNAMES = ["张", "李", "王", "赵", "刘", "陈", "杨", "黄", "周", "吴",
                "徐", "孙", "马", "朱", "胡", "郭", "何", "林", "罗", "高",
                "郑", "梁", "谢", "宋", "唐", "许", "韩", "冯", "邓", "曹"]
    MALE_NAMES = ["伟", "强", "磊", "军", "洋", "勇", "杰", "涛", "明", "超",
                  "鹏", "飞", "波", "刚", "辉", "健", "林", "宇", "浩", "鑫"]
    FEMALE_NAMES = ["芳", "娜", "敏", "静", "丽", "艳", "娟", "霞", "秀", "英",
                    "玲", "桂", "兰", "婷", "华", "梅", "雪", "琴", "云", "洁"]

    # 车牌前缀 / License plate prefixes
    PLATE_PREFIXES = ["川A", "川G", "川M"]

    @staticmethod
    def generate_vehicles(count: int = 20) -> List[Vehicle]:
        """
        生成模拟车辆 / Generate mock vehicles

        Args:
            count: 车辆数量 / Number of vehicles

        Returns:
            车辆列表 / List of vehicles
        """
        vehicles = []

        # 车辆类型分布 / Vehicle type distribution
        type_weights = [
            (VehicleType.DOMESTIC, 0.5),
            (VehicleType.KITCHEN, 0.2),
            (VehicleType.RECYCLABLE, 0.15),
            (VehicleType.HAZARDOUS, 0.05),
            (VehicleType.BULKY, 0.05),
            (VehicleType.GREEN, 0.05),
        ]

        # 容量配置 / Capacity configuration
        capacity_map = {
            VehicleType.DOMESTIC: (8.0, 12.0),
            VehicleType.KITCHEN: (5.0, 8.0),
            VehicleType.RECYCLABLE: (3.0, 5.0),
            VehicleType.HAZARDOUS: (2.0, 3.0),
            VehicleType.BULKY: (5.0, 10.0),
            VehicleType.GREEN: (3.0, 5.0),
        }

        for i in range(count):
            # 按权重选择类型 / Select type by weight
            r = random.random()
            cumulative = 0
            v_type = VehicleType.DOMESTIC
            for vt, w in type_weights:
                cumulative += w
                if r <= cumulative:
                    v_type = vt
                    break

            # 生成车牌 / Generate license plate
            prefix = random.choice(MockDataGenerator.PLATE_PREFIXES)
            plate = f"{prefix}{random.randint(10000, 99999)}"

            # 容量 / Capacity
            cap_min, cap_max = capacity_map[v_type]
            capacity = round(random.uniform(cap_min, cap_max), 1)

            vehicle = Vehicle(
                id=i + 1,
                license_plate=plate,
                vehicle_type=v_type,
                brand=random.choice(["东风", "重汽", "陕汽", "福田", "解放"]),
                model=random.choice(["重型", "中型", "轻型"]),
                max_capacity=capacity,
                current_load=round(random.uniform(0, capacity * 0.8), 2),
                status=random.choice(list(VehicleStatus)),
                gps_latitude=30.5728 + random.uniform(-0.02, 0.02),
                gps_longitude=104.0668 + random.uniform(-0.02, 0.02),
                total_mileage=round(random.uniform(10000, 100000), 1),
                engine_hours=round(random.uniform(100, 5000), 1),
            )
            vehicles.append(vehicle)

        return vehicles

    @staticmethod
    def generate_berths(count: int = 8) -> List[Berth]:
        """
        生成模拟泊位 / Generate mock berths

        Args:
            count: 泊位数量 / Number of berths

        Returns:
            泊位列表 / List of berths
        """
        berths = []

        # 泊位类型分布 / Berth type distribution
        berth_configs = [
            ("A", BerthType.DOMESTIC, "生活垃圾"),
            ("B", BerthType.KITCHEN, "厨余垃圾"),
            ("C", BerthType.RECYCLABLE, "可回收物"),
            ("D", BerthType.HAZARDOUS, "有害垃圾"),
            ("E", BerthType.BULKY, "大件垃圾"),
            ("F", BerthType.GREEN, "绿化垃圾"),
            ("G", BerthType.EMERGENCY, "应急"),
            ("H", BerthType.DOMESTIC, "生活垃圾"),
        ]

        for i in range(min(count, len(berth_configs))):
            prefix, b_type, name_cn = berth_configs[i]
            code = f"{prefix}{i+1:02d}"

            berth = Berth(
                id=i + 1,
                code=code,
                name=f"{name_cn}泊位{i+1}号",
                berth_type=b_type,
                location_x=random.uniform(20, 180),
                location_y=random.uniform(20, 130),
                capacity_tons=random.uniform(8.0, 15.0),
                status=random.choice([BerthStatus.AVAILABLE, BerthStatus.OCCUPIED]),
            )
            berths.append(berth)

        return berths

    @staticmethod
    def generate_departments() -> List[Department]:
        """生成部门数据 / Generate department data"""
        departments = [
            Department(id=1, code="OPS", name="运营部", description="日常运营管理"),
            Department(id=2, code="MAINT", name="维修部", description="设备维修保养"),
            Department(id=3, code="SAFE", name="安全部", description="安全生产管理"),
            Department(id=4, code="LOG", name="物流部", description="车辆调度管理"),
            Department(id=5, code="ADMIN", name="行政部", description="行政人事管理"),
        ]
        return departments

    @staticmethod
    def generate_staff(count: int = 50, departments: List[Department] = None) -> List[Staff]:
        """
        生成模拟人员 / Generate mock staff

        Args:
            count: 人员数量 / Number of staff
            departments: 部门列表 / List of departments

        Returns:
            人员列表 / List of staff
        """
        staff_list = []

        if not departments:
            departments = MockDataGenerator.generate_departments()

        # 角色分布 / Role distribution
        role_weights = [
            (StaffRole.DRIVER, 0.25),
            (StaffRole.OPERATOR, 0.30),
            (StaffRole.MAINTENANCE, 0.15),
            (StaffRole.CLEANER, 0.15),
            (StaffRole.SAFETY_OFFICER, 0.05),
            (StaffRole.MANAGER, 0.05),
            (StaffRole.INSPECTOR, 0.05),
        ]

        for i in range(count):
            # 生成姓名 / Generate name
            surname = random.choice(MockDataGenerator.SURNAMES)
            if random.random() < 0.5:
                name = f"{surname}{random.choice(MockDataGenerator.MALE_NAMES)}"
            else:
                name = f"{surname}{random.choice(MockDataGenerator.FEMALE_NAMES)}"

            # 按权重选择角色 / Select role by weight
            r = random.random()
            cumulative = 0
            role = StaffRole.OPERATOR
            for sr, w in role_weights:
                cumulative += w
                if r <= cumulative:
                    role = sr
                    break

            # 分配部门 / Assign department
            dept = random.choice(departments)

            staff = Staff(
                id=i + 1,
                employee_no=f"EMP{1000 + i:04d}",
                name=name,
                role=role,
                phone=f"138{random.randint(10000000, 99999999)}",
                email=f"emp{1000+i}@lqy.com",
                department_id=dept.id,
                badge_id=f"BADGE{2000+i:04d}",
                status=StaffStatus.ACTIVE,
                gps_latitude=30.5728 + random.uniform(-0.01, 0.01),
                gps_longitude=104.0668 + random.uniform(-0.01, 0.01),
            )
            staff_list.append(staff)

        return staff_list

    @staticmethod
    def generate_work_orders(
        count: int = 30,
        staff_list: List[Staff] = None,
        vehicles: List[Vehicle] = None
    ) -> List[WorkOrder]:
        """
        生成模拟工单 / Generate mock work orders

        Args:
            count: 工单数量 / Number of work orders
            staff_list: 人员列表 / List of staff
            vehicles: 车辆列表 / List of vehicles

        Returns:
            工单列表 / List of work orders
        """
        orders = []

        if not staff_list:
            staff_list = MockDataGenerator.generate_staff(count=10)

        # 工单类型和标题模板 / Work order types and title templates
        wo_templates = {
            WorkOrderType.INSPECTION: [
                "压缩机日常巡检", "泵站设备检查", "除臭系统巡检",
                "电气柜安全检查", "消防设备巡检"
            ],
            WorkOrderType.MAINTENANCE: [
                "压缩机定期保养", " conveyor 皮带更换", "润滑油更换",
                "滤网清洗", "轴承润滑保养"
            ],
            WorkOrderType.REPAIR: [
                "液压系统维修", "电机故障修复", "阀门更换",
                "控制面板维修", "管道泄漏修复"
            ],
            WorkOrderType.EMERGENCY: [
                "压缩机紧急停机维修", "电力故障抢修", "除臭设备紧急维修"
            ],
            WorkOrderType.CLEANING: [
                "卸料区清洗", "车间地面清洁", "设备外表清洁"
            ],
            WorkOrderType.SAFETY: [
                "安全隐患排查", "消防设施检查", "应急演练"
            ],
        }

        for i in range(count):
            wo_type = random.choice(list(WorkOrderType))
            title = random.choice(wo_templates[wo_type])

            # 随机创建人和执行人 / Random creator and assignee
            creator = random.choice(staff_list)
            assignee = random.choice(staff_list)

            # 随机车辆（部分工单关联车辆）
            vehicle_id = None
            if vehicles and random.random() < 0.3:
                vehicle_id = random.choice(vehicles).id

            # 计划时间 / Planned time
            planned_start = datetime.now() + timedelta(days=random.randint(-5, 10))
            planned_end = planned_start + timedelta(hours=random.randint(1, 8))

            order = WorkOrder(
                id=i + 1,
                order_no=f"WO{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
                order_type=wo_type,
                title=title,
                description=f"{title}作业工单，请按计划执行",
                priority=random.choice(list(WorkOrderPriority)),
                vehicle_id=vehicle_id,
                creator_id=creator.id,
                assignee_id=assignee.id if random.random() > 0.2 else None,  # 20%未分配
                planned_start=planned_start,
                planned_end=planned_end,
                status=random.choice(list(WorkOrderStatus)),
                created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            )
            orders.append(order)

        return orders

    @staticmethod
    def generate_all() -> Dict:
        """
        生成所有Mock数据 / Generate all mock data

        Returns:
            包含所有Mock数据的字典 / Dictionary containing all mock data
        """
        departments = MockDataGenerator.generate_departments()
        staff = MockDataGenerator.generate_staff(departments=departments)
        vehicles = MockDataGenerator.generate_vehicles()
        berths = MockDataGenerator.generate_berths()
        work_orders = MockDataGenerator.generate_work_orders(
            staff_list=staff,
            vehicles=vehicles
        )

        return {
            "departments": departments,
            "staff": staff,
            "vehicles": vehicles,
            "berths": berths,
            "work_orders": work_orders,
        }
