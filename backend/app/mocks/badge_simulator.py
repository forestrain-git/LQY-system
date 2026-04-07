"""
人员工牌模拟器 / Staff Badge Simulator

模拟人员定位工牌系统，包括：
- 实时位置追踪（10-30cm精度）
- 静置监测（长时间不动检测）
- SOS一键报警
- 电量监测

Simulates staff badge positioning system, including:
- Real-time location tracking (10-30cm accuracy)
- Static detection (long time motionless detection)
- SOS emergency button
- Battery monitoring

Author: AI Sprint
Date: 2026-04-07
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class BadgeStatus(str, Enum):
    """工牌状态 / Badge Status"""
    NORMAL = "normal"           # 正常 / Normal
    STATIC = "static"           # 静置 / Static (not moving)
    SOS = "sos"                 # 紧急求救 / Emergency
    LOW_BATTERY = "low_battery" # 低电量 / Low battery
    OFFLINE = "offline"         # 离线 / Offline


@dataclass
class BadgeReading:
    """
    工牌读数 / Badge Reading
    """
    badge_id: str
    person_name: str
    person_role: str  # 工种 / Job role

    # 位置 / Position
    x: float  # X坐标(米) / X coordinate (meters)
    y: float  # Y坐标(米) / Y coordinate (meters)
    z: float = 0.0  # 高度(米) / Height (meters)

    # 精度 / Accuracy
    accuracy: float = 0.15  # 定位精度(米) / Positioning accuracy (meters, 10-30cm)

    # 状态 / Status
    status: BadgeStatus = BadgeStatus.NORMAL
    is_moving: bool = True
    static_duration: int = 0  # 静置时长(秒) / Static duration (seconds)

    # SOS / SOS
    sos_triggered: bool = False
    sos_time: Optional[datetime] = None

    # 电量 / Battery
    battery_level: int = 100  # 电量百分比 / Battery percentage

    # 时间戳 / Timestamp
    timestamp: datetime = field(default_factory=datetime.now)

    # 异常检测 / Anomaly detection
    anomaly_type: Optional[str] = None  # "fall", "linger", "panic"


class BadgeSimulator:
    """
    人员工牌模拟器 / Staff Badge Simulator

    模拟高精度人员定位工牌的实时数据生成
    Simulates real-time data generation for high-precision staff positioning badges
    """

    # 工种列表 / Job roles
    ROLES = [
        ("司机", "Driver"),
        ("操作工", "Operator"),
        ("维修工", "Maintenance"),
        ("保洁员", "Cleaner"),
        ("安全员", "Safety Officer"),
        ("管理员", "Manager"),
        ("巡检员", "Inspector")
    ]

    def __init__(self, personnel_count: int = 20):
        """
        初始化模拟器 / Initialize simulator

        Args:
            personnel_count: 模拟人数 / Number of personnel to simulate
        """
        self.personnel_count = personnel_count
        self.badges: Dict[str, BadgeReading] = {}
        self._init_personnel()

    def _init_personnel(self):
        """初始化人员数据 / Initialize personnel data"""
        surnames = ["张", "李", "王", "赵", "刘", "陈", "杨", "黄", "周", "吴",
                   "徐", "孙", "马", "朱", "胡", "郭", "何", "林", "罗", "高"]
        names = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
                "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "华", "鹏"]

        for i in range(self.personnel_count):
            badge_id = f"BADGE_{1000 + i:04d}"
            name = f"{random.choice(surnames)}{random.choice(names)}"
            role_cn, role_en = random.choice(self.ROLES)

            # 随机初始位置 / Random initial position
            x = random.uniform(20, 180)
            y = random.uniform(20, 130)

            self.badges[badge_id] = BadgeReading(
                badge_id=badge_id,
                person_name=name,
                person_role=role_cn,
                x=x,
                y=y,
                accuracy=random.uniform(0.10, 0.30),  # 10-30cm精度
                battery_level=random.randint(30, 100),
                timestamp=datetime.now()
            )

    def update_positions(self, time_delta: int = 10) -> List[BadgeReading]:
        """
        更新所有工牌位置 / Update all badge positions

        Args:
            time_delta: 时间间隔(秒) / Time interval (seconds)

        Returns:
            更新后的读数列表 / Updated readings list
        """
        updated = []

        for badge_id, badge in self.badges.items():
            # 模拟移动 / Simulate movement
            if random.random() < 0.7:  # 70%概率在移动
                # 随机走动 / Random walk
                speed = random.uniform(0.5, 1.5)  # 速度 0.5-1.5 m/s
                angle = random.uniform(0, 2 * math.pi)

                dx = speed * time_delta * math.cos(angle)
                dy = speed * time_delta * math.sin(angle)

                badge.x += dx
                badge.y += dy

                # 边界检查 / Boundary check
                badge.x = max(0, min(200, badge.x))
                badge.y = max(0, min(150, badge.y))

                badge.is_moving = True
                badge.static_duration = 0
                badge.status = BadgeStatus.NORMAL

            else:  # 30%概率静止
                badge.is_moving = False
                badge.static_duration += time_delta

                # 长时间静止检测 / Long static detection
                if badge.static_duration > 300:  # 5分钟
                    badge.status = BadgeStatus.STATIC

            # 电量消耗 / Battery drain
            if random.random() < 0.1:  # 10%概率耗电
                badge.battery_level = max(0, badge.battery_level - 1)

            if badge.battery_level < 20:
                badge.status = BadgeStatus.LOW_BATTERY

            # 随机SOS触发（极低概率）/ Random SOS trigger (very low probability)
            if random.random() < 0.001 and not badge.sos_triggered:  # 0.1%
                badge.sos_triggered = True
                badge.sos_time = datetime.now()
                badge.status = BadgeStatus.SOS

            # 随机异常行为检测 / Random anomaly detection
            if random.random() < 0.005:  # 0.5%概率异常
                anomaly = random.choice(["fall", "linger"])
                badge.anomaly_type = anomaly

            # 更新时间戳 / Update timestamp
            badge.timestamp += timedelta(seconds=time_delta)
            updated.append(badge)

        return updated

    def get_all_positions(self) -> List[Dict]:
        """获取所有工牌位置 / Get all badge positions"""
        return [
            {
                "badge_id": b.badge_id,
                "person_name": b.person_name,
                "role": b.person_role,
                "position": {"x": round(b.x, 2), "y": round(b.y, 2)},
                "accuracy": round(b.accuracy, 2),
                "status": b.status.value,
                "is_moving": b.is_moving,
                "static_duration": b.static_duration,
                "battery_level": b.battery_level,
                "sos_triggered": b.sos_triggered,
                "anomaly_type": b.anomaly_type,
                "timestamp": b.timestamp.isoformat()
            }
            for b in self.badges.values()
        ]

    def get_persons_by_zone(self, zone_boundary: List[tuple]) -> List[Dict]:
        """
        获取指定区域内的人员 / Get personnel in specific zone

        Args:
            zone_boundary: 区域边界 [(x1,y1), (x2,y2), ...]

        Returns:
            区域内人员列表 / Personnel in zone
        """
        # 简化判断：使用边界框
        xs = [p[0] for p in zone_boundary]
        ys = [p[1] for p in zone_boundary]

        persons = []
        for badge in self.badges.values():
            if min(xs) <= badge.x <= max(xs) and min(ys) <= badge.y <= max(ys):
                persons.append({
                    "badge_id": badge.badge_id,
                    "name": badge.person_name,
                    "role": badge.person_role,
                    "position": (round(badge.x, 2), round(badge.y, 2))
                })

        return persons

    def clear_sos(self, badge_id: str) -> bool:
        """清除SOS状态 / Clear SOS status"""
        if badge_id in self.badges:
            self.badges[badge_id].sos_triggered = False
            self.badges[badge_id].sos_time = None
            self.badges[badge_id].status = BadgeStatus.NORMAL
            return True
        return False
