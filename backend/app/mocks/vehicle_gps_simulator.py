"""
车辆GPS模拟器 / Vehicle GPS Simulator

模拟转运车辆的GPS定位和轨迹：
- 实时位置追踪
- 行驶轨迹记录
- 进站/出站检测
- 速度监测

Simulates vehicle GPS positioning and tracking:
- Real-time location tracking
- Travel trajectory recording
- Entry/exit detection
- Speed monitoring

Author: AI Sprint
Date: 2026-04-07
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class VehicleStatus(str, Enum):
    """车辆状态 / Vehicle Status"""
    IDLE = "idle"               # 闲置 / Idle
    EN_ROUTE = "en_route"       # 行驶中 / En route
    QUEUING = "queuing"         # 排队中 / Queuing
    UNLOADING = "unloading"     # 卸料中 / Unloading
    MAINTENANCE = "maintenance" # 维护中 / Maintenance


class VehicleType(str, Enum):
    """车辆类型 / Vehicle Type"""
    DOMESTIC = "domestic"       # 生活垃圾车 / Domestic waste
    KITCHEN = "kitchen"         # 厨余垃圾车 / Kitchen waste
    RECYCLABLE = "recyclable"   # 可回收物车 / Recyclable
    HAZARDOUS = "hazardous"     # 有害垃圾车 / Hazardous


@dataclass
class GPSReading:
    """
    GPS读数 / GPS Reading
    """
    vehicle_id: str
    license_plate: str
    vehicle_type: VehicleType

    # 位置 / Position (使用站内相对坐标 / Using station-relative coordinates)
    x: float  # X坐标(米) / X coordinate (meters)
    y: float  # Y坐标(米) / Y coordinate (meters)

    # GPS坐标 / GPS coordinates
    latitude: float   # 纬度 / Latitude
    longitude: float  # 经度 / Longitude

    # 运动状态 / Motion state
    speed: float = 0.0          # 速度(km/h) / Speed (km/h)
    heading: float = 0.0        # 方向(度) / Heading (degrees)
    altitude: float = 0.0       # 海拔(m) / Altitude (meters)

    # 精度 / Accuracy
    gps_accuracy: float = 5.0   # GPS精度(m) / GPS accuracy (meters)

    # 车辆状态 / Vehicle status
    status: VehicleStatus = VehicleStatus.IDLE

    # 载重 / Load
    current_load: float = 0.0   # 当前载重(吨) / Current load (tons)
    max_capacity: float = 5.0   # 最大容量(吨) / Max capacity (tons)

    # 时间戳 / Timestamp
    timestamp: datetime = field(default_factory=datetime.now)

    # 里程 / Mileage
    odometer: float = 0.0       # 总里程(km) / Total mileage (km)


class VehicleGPSSimulator:
    """
    车辆GPS模拟器 / Vehicle GPS Simulator

    模拟垃圾转运车辆的GPS定位和运动
    Simulates GPS positioning and movement of waste transfer vehicles
    """

    def __init__(self, vehicle_count: int = 15):
        """
        初始化模拟器 / Initialize simulator

        Args:
            vehicle_count: 车辆数量 / Number of vehicles
        """
        self.vehicle_count = vehicle_count
        self.vehicles: Dict[str, GPSReading] = {}
        self.trajectories: Dict[str, List[Dict]] = {}  # 轨迹记录 / Trajectory records
        self._init_vehicles()

    def _init_vehicles(self):
        """初始化车辆 / Initialize vehicles"""
        # 车牌前缀 / License plate prefixes
        prefixes = ["川A", "川G", "川M"]

        # 车辆类型分布 / Vehicle type distribution
        type_weights = [
            (VehicleType.DOMESTIC, 0.6),
            (VehicleType.KITCHEN, 0.2),
            (VehicleType.RECYCLABLE, 0.15),
            (VehicleType.HAZARDOUS, 0.05)
        ]

        for i in range(self.vehicle_count):
            vehicle_id = f"VEH_{1000 + i:04d}"
            prefix = random.choice(prefixes)
            plate = f"{prefix}{random.randint(10000, 99999)}"

            # 按权重选择类型 / Select type by weight
            r = random.random()
            cumulative = 0
            v_type = VehicleType.DOMESTIC
            for vt, w in type_weights:
                cumulative += w
                if r <= cumulative:
                    v_type = vt
                    break

            # 容量配置 / Capacity config
            capacity_map = {
                VehicleType.DOMESTIC: 8.0,
                VehicleType.KITCHEN: 5.0,
                VehicleType.RECYCLABLE: 3.0,
                VehicleType.HAZARDOUS: 2.0
            }

            # 初始位置：站外随机 / Initial position: random outside station
            x = random.choice([random.uniform(-50, 0), random.uniform(200, 250)])
            y = random.uniform(0, 150)

            self.vehicles[vehicle_id] = GPSReading(
                vehicle_id=vehicle_id,
                license_plate=plate,
                vehicle_type=v_type,
                x=x,
                y=y,
                latitude=30.5728 + random.uniform(-0.01, 0.01),
                longitude=104.0668 + random.uniform(-0.01, 0.01),
                max_capacity=capacity_map[v_type],
                current_load=random.uniform(0, capacity_map[v_type] * 0.8)
            )

            self.trajectories[vehicle_id] = []

    def update_positions(self, time_delta: int = 10) -> List[GPSReading]:
        """
        更新车辆位置 / Update vehicle positions

        Args:
            time_delta: 时间间隔(秒) / Time interval (seconds)

        Returns:
            更新后的车辆列表 / Updated vehicle list
        """
        updated = []

        # 站点入口位置 / Station entry points
        entry_points = [(0, 75), (200, 75)]

        for vid, vehicle in self.vehicles.items():
            # 状态机转换 / State machine transition
            if vehicle.status == VehicleStatus.IDLE:
                # 闲置车辆有概率开始行驶 / Idle vehicles may start moving
                if random.random() < 0.1:
                    vehicle.status = VehicleStatus.EN_ROUTE
                    # 目标：站点入口 / Target: station entry
                    target = random.choice(entry_points)
                    vehicle.heading = self._calculate_heading(
                        (vehicle.x, vehicle.y), target
                    )

            elif vehicle.status == VehicleStatus.EN_ROUTE:
                # 向站点行驶 / Drive to station
                speed_kmh = random.uniform(20, 40)
                vehicle.speed = speed_kmh

                # 更新位置 / Update position
                speed_ms = speed_kmh / 3.6
                dx = speed_ms * time_delta * math.cos(math.radians(vehicle.heading))
                dy = speed_ms * time_delta * math.sin(math.radians(vehicle.heading))

                vehicle.x += dx
                vehicle.y += dy

                # 进站检测 / Entry detection
                if 0 <= vehicle.x <= 200 and 0 <= vehicle.y <= 150:
                    vehicle.status = VehicleStatus.QUEUING
                    vehicle.speed = 0

            elif vehicle.status == VehicleStatus.QUEUING:
                # 排队等待 / Queue waiting
                if random.random() < 0.05:  # 5%概率开始卸料
                    vehicle.status = VehicleStatus.UNLOADING

            elif vehicle.status == VehicleStatus.UNLOADING:
                # 卸料中 / Unloading
                if random.random() < 0.1:  # 10%概率卸料完成
                    vehicle.status = VehicleStatus.EN_ROUTE
                    vehicle.current_load = 0
                    # 驶离站点 / Leave station
                    vehicle.heading = random.choice([90, 270])

            # 更新里程 / Update mileage
            vehicle.odometer += (vehicle.speed / 3.6) * time_delta / 1000

            # 记录轨迹 / Record trajectory
            if len(self.trajectories[vid]) > 1000:
                self.trajectories[vid].pop(0)

            self.trajectories[vid].append({
                "x": round(vehicle.x, 2),
                "y": round(vehicle.y, 2),
                "speed": round(vehicle.speed, 2),
                "timestamp": vehicle.timestamp.isoformat()
            })

            vehicle.timestamp += timedelta(seconds=time_delta)
            updated.append(vehicle)

        return updated

    def _calculate_heading(self, from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> float:
        """计算航向角 / Calculate heading angle"""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        return angle

    def get_all_vehicles(self) -> List[Dict]:
        """获取所有车辆状态 / Get all vehicle statuses"""
        return [
            {
                "vehicle_id": v.vehicle_id,
                "license_plate": v.license_plate,
                "type": v.vehicle_type.value,
                "position": {"x": round(v.x, 2), "y": round(v.y, 2)},
                "gps": {"lat": round(v.latitude, 6), "lng": round(v.longitude, 6)},
                "speed": round(v.speed, 2),
                "heading": round(v.heading, 2),
                "status": v.status.value,
                "load": f"{v.current_load:.1f}/{v.max_capacity:.1f}t",
                "odometer": round(v.odometer, 2),
                "timestamp": v.timestamp.isoformat()
            }
            for v in self.vehicles.values()
        ]

    def get_vehicle_trajectory(self, vehicle_id: str, last_n: int = 100) -> List[Dict]:
        """获取车辆轨迹 / Get vehicle trajectory"""
        if vehicle_id in self.trajectories:
            return self.trajectories[vehicle_id][-last_n:]
        return []

    def get_vehicles_in_station(self) -> List[Dict]:
        """获取站内车辆 / Get vehicles in station"""
        return [
            {
                "vehicle_id": v.vehicle_id,
                "plate": v.license_plate,
                "status": v.status.value,
                "position": (round(v.x, 2), round(v.y, 2))
            }
            for v in self.vehicles.values()
            if 0 <= v.x <= 200 and 0 <= v.y <= 150
        ]
