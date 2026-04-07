"""
电子围栏模拟器 / Electronic Fence Simulator

模拟转运站内的电子围栏系统，包括：
- 危险区域定义（高空区、沼气区、高压区等）
- 人员进出区域检测
- 越界告警生成

Simulates electronic fence system in transfer station, including:
- Danger zone definitions (high altitude, biogas, high voltage, etc.)
- Personnel entry/exit detection
- Boundary crossing alerts

Author: AI Sprint
Date: 2026-04-07
"""

import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ZoneType(str, Enum):
    """
    危险区域类型 / Danger Zone Types
    """
    HIGH_ALTITUDE = "high_altitude"      # 高空作业区 / High altitude work area
    BIOGAS = "biogas"                    # 沼气区 / Biogas area
    HIGH_VOLTAGE = "high_voltage"        # 高压设备区 / High voltage equipment
    UNLOADING = "unloading"              # 卸料区 / Unloading area
    CHEMICAL = "chemical"                # 化学品存储区 / Chemical storage
    RESTRICTED = "restricted"            # 限制区 / Restricted area


class AlertLevel(str, Enum):
    """
    告警级别 / Alert Levels
    """
    LOW = "low"           # 提示 / Notice
    MEDIUM = "medium"     # 警告 / Warning
    HIGH = "high"         # 严重 / Critical
    EMERGENCY = "emergency"  # 紧急 / Emergency


@dataclass
class Zone:
    """
    电子围栏区域 / Electronic Fence Zone
    """
    id: str
    name: str
    name_en: str
    zone_type: ZoneType
    level: AlertLevel
    # 区域边界点 (x, y) 单位：米 / Zone boundary points in meters
    boundary: List[Tuple[float, float]]
    description: str


@dataclass
class PersonnelPosition:
    """
    人员位置 / Personnel Position
    """
    badge_id: str
    person_name: str
    x: float  # X坐标(米) / X coordinate in meters
    y: float  # Y坐标(米) / Y coordinate in meters
    timestamp: datetime
    is_sos: bool = False  # SOS报警状态 / SOS alarm status


@dataclass
class FenceAlert:
    """
    围栏告警 / Fence Alert
    """
    id: str
    zone_id: str
    zone_name: str
    badge_id: str
    person_name: str
    alert_type: str  # "entry" or "exit" or "sos"
    level: AlertLevel
    timestamp: datetime
    position: Tuple[float, float]
    message: str


class FenceSimulator:
    """
    电子围栏模拟器 / Electronic Fence Simulator

    模拟转运站内的电子围栏系统，生成人员位置数据和越界告警
    Simulates electronic fence system, generates personnel position data and alerts
    """

    def __init__(self):
        """初始化模拟器 / Initialize simulator"""
        self.zones: List[Zone] = self._init_zones()
        self.personnel: Dict[str, PersonnelPosition] = {}
        self.alerts: List[FenceAlert] = []
        self.alert_counter = 0

    def _init_zones(self) -> List[Zone]:
        """
        初始化默认危险区域 / Initialize default danger zones

        基于典型垃圾转运站布局 / Based on typical waste transfer station layout
        坐标系：左下角为原点(0,0)，单位米 / Coordinate: origin at bottom-left, unit meters
        """
        return [
            Zone(
                id="zone_001",
                name="高空作业区A",
                name_en="High Altitude Zone A",
                zone_type=ZoneType.HIGH_ALTITUDE,
                level=AlertLevel.HIGH,
                boundary=[(50, 80), (80, 80), (80, 100), (50, 100)],
                description="压缩机顶部维护区域 / Compressor top maintenance area"
            ),
            Zone(
                id="zone_002",
                name="沼气监测区",
                name_en="Biogas Monitoring Zone",
                zone_type=ZoneType.BIOGAS,
                level=AlertLevel.HIGH,
                boundary=[(120, 40), (150, 40), (150, 70), (120, 70)],
                description="垃圾堆放区沼气监测 / Biogas monitoring for waste storage"
            ),
            Zone(
                id="zone_003",
                name="高压设备区",
                name_en="High Voltage Equipment Zone",
                zone_type=ZoneType.HIGH_VOLTAGE,
                level=AlertLevel.EMERGENCY,
                boundary=[(10, 10), (40, 10), (40, 40), (10, 40)],
                description="配电室和变压器区域 / Distribution room and transformer area"
            ),
            Zone(
                id="zone_004",
                name="卸料作业区",
                name_en="Unloading Operation Zone",
                zone_type=ZoneType.UNLOADING,
                level=AlertLevel.MEDIUM,
                boundary=[(80, 20), (110, 20), (110, 50), (80, 50)],
                description="车辆卸料区域 / Vehicle unloading area"
            ),
            Zone(
                id="zone_005",
                name="渗滤液处理区",
                name_en="Leachate Treatment Zone",
                zone_type=ZoneType.CHEMICAL,
                level=AlertLevel.HIGH,
                boundary=[(150, 80), (180, 80), (180, 100), (150, 100)],
                description="渗滤液处理设备区 / Leachate treatment equipment area"
            ),
        ]

    def _is_point_in_zone(self, x: float, y: float, zone: Zone) -> bool:
        """
        判断点是否在区域内（射线法）/ Check if point is in zone (ray casting)

        Args:
            x: X坐标 / X coordinate
            y: Y坐标 / Y coordinate
            zone: 区域对象 / Zone object

        Returns:
            是否在区域内 / Whether point is inside zone
        """
        # 简化判断：使用边界框 / Simplified: use bounding box
        xs = [p[0] for p in zone.boundary]
        ys = [p[1] for p in zone.boundary]
        return min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys)

    def generate_personnel_positions(
        self,
        count: int = 10,
        center_x: float = 100,
        center_y: float = 60,
        spread: float = 80
    ) -> List[PersonnelPosition]:
        """
        生成人员位置数据 / Generate personnel position data

        模拟人员在站内随机移动 / Simulates personnel moving randomly in station

        Args:
            count: 人数 / Number of personnel
            center_x: 中心X坐标 / Center X coordinate
            center_y: 中心Y坐标 / Center Y coordinate
            spread: 分布范围 / Distribution spread

        Returns:
            人员位置列表 / List of personnel positions
        """
        positions = []
        names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
                "郑一", "冯二", "陈三", "褚四", "卫五", "蒋六", "沈七"]

        now = datetime.now()

        for i in range(min(count, len(names))):
            badge_id = f"BADGE_{1000 + i:04d}"

            # 随机位置（正态分布）/ Random position (normal distribution)
            x = random.gauss(center_x, spread / 3)
            y = random.gauss(center_y, spread / 3)

            # 确保在合理范围内 / Ensure within reasonable bounds
            x = max(0, min(200, x))
            y = max(0, min(150, y))

            # 随机SOS状态（1%概率）/ Random SOS status (1% chance)
            is_sos = random.random() < 0.01

            pos = PersonnelPosition(
                badge_id=badge_id,
                person_name=names[i],
                x=round(x, 2),
                y=round(y, 2),
                timestamp=now,
                is_sos=is_sos
            )

            positions.append(pos)
            self.personnel[badge_id] = pos

        return positions

    def check_zone_violations(
        self,
        positions: Optional[List[PersonnelPosition]] = None
    ) -> List[FenceAlert]:
        """
        检查区域越界 / Check zone violations

        Args:
            positions: 要检查的位置列表 / Positions to check

        Returns:
            告警列表 / List of alerts
        """
        if positions is None:
            positions = list(self.personnel.values())

        new_alerts = []

        for pos in positions:
            # 检查SOS报警 / Check SOS
            if pos.is_sos:
                self.alert_counter += 1
                alert = FenceAlert(
                    id=f"ALERT_{self.alert_counter:06d}",
                    zone_id="SOS",
                    zone_name="紧急求救 / Emergency SOS",
                    badge_id=pos.badge_id,
                    person_name=pos.person_name,
                    alert_type="sos",
                    level=AlertLevel.EMERGENCY,
                    timestamp=pos.timestamp,
                    position=(pos.x, pos.y),
                    message=f"人员 {pos.person_name} 触发SOS紧急求救！"
                )
                new_alerts.append(alert)

            # 检查每个危险区域 / Check each danger zone
            for zone in self.zones:
                is_in_zone = self._is_point_in_zone(pos.x, pos.y, zone)

                # 简化的进入检测（实际应该跟踪状态变化）
                # Simplified entry detection (actual should track state changes)
                if is_in_zone and random.random() < 0.3:  # 30%概率触发告警
                    self.alert_counter += 1
                    alert = FenceAlert(
                        id=f"ALERT_{self.alert_counter:06d}",
                        zone_id=zone.id,
                        zone_name=zone.name,
                        badge_id=pos.badge_id,
                        person_name=pos.person_name,
                        alert_type="entry",
                        level=zone.level,
                        timestamp=pos.timestamp,
                        position=(pos.x, pos.y),
                        message=f"人员 {pos.person_name} 进入{zone.name}！"
                    )
                    new_alerts.append(alert)

        self.alerts.extend(new_alerts)
        return new_alerts

    def get_zone_status(self) -> Dict:
        """
        获取所有区域状态 / Get all zone status

        Returns:
            区域状态字典 / Zone status dictionary
        """
        return {
            "zones": [
                {
                    "id": zone.id,
                    "name": zone.name,
                    "name_en": zone.name_en,
                    "type": zone.zone_type.value,
                    "level": zone.level.value,
                    "boundary": zone.boundary,
                    "description": zone.description
                }
                for zone in self.zones
            ],
            "total_zones": len(self.zones),
            "danger_levels": {
                "emergency": len([z for z in self.zones if z.level == AlertLevel.EMERGENCY]),
                "high": len([z for z in self.zones if z.level == AlertLevel.HIGH]),
                "medium": len([z for z in self.zones if z.level == AlertLevel.MEDIUM]),
            }
        }

    def get_personnel_in_zones(self) -> Dict[str, List[Dict]]:
        """
        获取各区域内的人员 / Get personnel in each zone

        Returns:
            区域-人员映射 / Zone-personnel mapping
        """
        result = {zone.id: [] for zone in self.zones}

        for badge_id, pos in self.personnel.items():
            for zone in self.zones:
                if self._is_point_in_zone(pos.x, pos.y, zone):
                    result[zone.id].append({
                        "badge_id": pos.badge_id,
                        "name": pos.person_name,
                        "position": (pos.x, pos.y),
                        "timestamp": pos.timestamp.isoformat()
                    })

        return result

    def simulate_movement(
        self,
        duration_minutes: int = 60,
        update_interval: int = 10
    ) -> List[Dict]:
        """
        模拟人员移动场景 / Simulate personnel movement scenario

        Args:
            duration_minutes: 模拟时长(分钟) / Simulation duration
            update_interval: 更新间隔(秒) / Update interval

        Returns:
            模拟事件列表 / List of simulation events
        """
        events = []
        steps = (duration_minutes * 60) // update_interval

        for step in range(steps):
            # 更新人员位置 / Update positions
            for badge_id, pos in self.personnel.items():
                # 随机移动 / Random movement
                pos.x += random.gauss(0, 2)  # 随机走动
                pos.y += random.gauss(0, 2)
                pos.x = max(0, min(200, pos.x))
                pos.y = max(0, min(150, pos.y))
                pos.timestamp += timedelta(seconds=update_interval)

            # 检查越界 / Check violations
            new_alerts = self.check_zone_violations()

            if new_alerts:
                events.append({
                    "timestamp": pos.timestamp.isoformat(),
                    "step": step,
                    "alerts": [
                        {
                            "id": alert.id,
                            "type": alert.alert_type,
                            "zone": alert.zone_name,
                            "person": alert.person_name,
                            "level": alert.level.value
                        }
                        for alert in new_alerts
                    ]
                })

        return events
