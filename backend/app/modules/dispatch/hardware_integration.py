"""
硬件集成服务 / Hardware Integration Service

连接GPS、工牌、地磅等模拟器与业务模型
Connects GPS, badge, weighbridge simulators with business models

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

from app.mocks.vehicle_gps_simulator import VehicleGPSSimulator, VehicleState
from app.mocks.badge_simulator import StaffBadgeSimulator
from app.mocks.weighbridge_simulator import WeighbridgeSimulator, WeighbridgeState
from app.mocks.fence_simulator import FenceSimulator, ZoneType


@dataclass
class VehicleLocationEvent:
    """
    车辆位置事件 / Vehicle Location Event
    """
    vehicle_id: int
    latitude: float
    longitude: float
    speed: float
    heading: float
    state: str
    timestamp: datetime
    in_fence: bool
    fence_zone: Optional[str]


@dataclass
class StaffBadgeEvent:
    """
    员工工牌事件 / Staff Badge Event
    """
    staff_id: int
    badge_id: str
    location: str
    action: str  # 'entry' or 'exit'
    timestamp: datetime


@dataclass
class WeighbridgeEvent:
    """
    地磅称重事件 / Weighbridge Event
    """
    schedule_id: int
    gross_weight: float
    tare_weight: float
    net_weight: float
    vehicle_plate: str
    timestamp: datetime
    photo_url: Optional[str]


class HardwareEventBus:
    """
    硬件事件总线 / Hardware Event Bus

    管理硬件事件的分发和订阅
    Manages hardware event distribution and subscription
    """

    def __init__(self):
        self._subscribers: Dict[str, list] = {
            'gps': [],
            'badge': [],
            'weighbridge': [],
            'fence': [],
        }

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        订阅事件 / Subscribe to event

        Args:
            event_type: 事件类型 / Event type
            callback: 回调函数 / Callback function
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """取消订阅 / Unsubscribe"""
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, event_data: Any) -> None:
        """发布事件 / Publish event"""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    print(f"Event handler error: {e}")


class HardwareIntegrationService:
    """
    硬件集成服务 / Hardware Integration Service

    统一管理所有硬件模拟器，提供业务层接口
    Unified management of all hardware simulators, provides business layer interface
    """

    def __init__(self):
        # 初始化模拟器 / Initialize simulators
        self.gps_simulator = VehicleGPSSimulator()
        self.badge_simulator = StaffBadgeSimulator()
        self.weighbridge = WeighbridgeSimulator()
        self.fence_simulator = FenceSimulator()

        # 事件总线 / Event bus
        self.event_bus = HardwareEventBus()

        # 回调句柄存储 / Callback handle storage
        self._gps_callbacks: Dict[int, int] = {}
        self._badge_callbacks: Dict[str, int] = {}

    # ==================== GPS 集成 / GPS Integration ====================

    def register_vehicle_gps(
        self,
        vehicle_id: int,
        start_lat: float = 30.5728,
        start_lon: float = 104.0668
    ) -> None:
        """
        注册车辆GPS追踪 / Register vehicle GPS tracking

        Args:
            vehicle_id: 车辆ID / Vehicle ID
            start_lat: 初始纬度 / Initial latitude
            start_lon: 初始经度 / Initial longitude
        """
        handle = self.gps_simulator.register_vehicle(
            vehicle_id=vehicle_id,
            start_lat=start_lat,
            start_lon=start_lon,
            update_callback=lambda v_id, data: self._on_gps_update(v_id, data)
        )
        self._gps_callbacks[vehicle_id] = handle

    def _on_gps_update(self, vehicle_id: int, data: Dict) -> None:
        """GPS更新回调 / GPS update callback"""
        # 检查电子围栏 / Check electronic fence
        in_fence, zone_name = self.fence_simulator.check_position(
            data['latitude'],
            data['longitude']
        )

        event = VehicleLocationEvent(
            vehicle_id=vehicle_id,
            latitude=data['latitude'],
            longitude=data['longitude'],
            speed=data['speed'],
            heading=data['heading'],
            state=data['state'],
            timestamp=data['timestamp'],
            in_fence=in_fence,
            fence_zone=zone_name
        )

        self.event_bus.publish('gps', event)

    def set_vehicle_destination(
        self,
        vehicle_id: int,
        dest_lat: float,
        dest_lon: float
    ) -> bool:
        """
        设置车辆目的地 / Set vehicle destination

        Args:
            vehicle_id: 车辆ID / Vehicle ID
            dest_lat: 目标纬度 / Destination latitude
            dest_lon: 目标经度 / Destination longitude

        Returns:
            是否成功 / Success flag
        """
        handle = self._gps_callbacks.get(vehicle_id)
        if handle:
            return self.gps_simulator.set_destination(handle, dest_lat, dest_lon)
        return False

    def unregister_vehicle_gps(self, vehicle_id: int) -> None:
        """注销车辆GPS / Unregister vehicle GPS"""
        handle = self._gps_callbacks.pop(vehicle_id, None)
        if handle:
            self.gps_simulator.unregister_vehicle(handle)

    # ==================== 工牌集成 / Badge Integration ====================

    def register_staff_badge(
        self,
        staff_id: int,
        badge_id: str,
        area_bounds: Dict[str, tuple]
    ) -> None:
        """
        注册员工工牌 / Register staff badge

        Args:
            staff_id: 员工ID / Staff ID
            badge_id: 工牌ID / Badge ID
            area_bounds: 区域边界 / Area boundaries {name: (x1, y1, x2, y2)}
        """
        handle = self.badge_simulator.register_badge(
            badge_id=badge_id,
            area_bounds=area_bounds,
            scan_callback=lambda b_id, area, entering: self._on_badge_scan(
                staff_id, b_id, area, entering
            )
        )
        self._badge_callbacks[badge_id] = handle

    def _on_badge_scan(self, staff_id: int, badge_id: str, area: str, entering: bool) -> None:
        """工牌扫描回调 / Badge scan callback"""
        event = StaffBadgeEvent(
            staff_id=staff_id,
            badge_id=badge_id,
            location=area,
            action='entry' if entering else 'exit',
            timestamp=datetime.now()
        )
        self.event_bus.publish('badge', event)

    def unregister_staff_badge(self, badge_id: str) -> None:
        """注销员工工牌 / Unregister staff badge"""
        handle = self._badge_callbacks.pop(badge_id, None)
        if handle:
            self.badge_simulator.unregister_badge(handle)

    # ==================== 地磅集成 / Weighbridge Integration ====================

    def start_weighing_process(
        self,
        schedule_id: int,
        vehicle_plate: str,
        expected_weight: float
    ) -> Dict[str, Any]:
        """
        开始称重流程 / Start weighing process

        Args:
            schedule_id: 调度ID / Schedule ID
            vehicle_plate: 车牌号 / License plate
            expected_weight: 预期重量 / Expected weight

        Returns:
            称重结果 / Weighing result
        """
        result = self.weighbridge.simulate_complete_process(
            vehicle_plate=vehicle_plate,
            actual_weight=expected_weight
        )

        if result['success']:
            event = WeighbridgeEvent(
                schedule_id=schedule_id,
                gross_weight=result['gross_weight'],
                tare_weight=result['tare_weight'],
                net_weight=result['net_weight'],
                vehicle_plate=vehicle_plate,
                timestamp=result['timestamp'],
                photo_url=None  # 可扩展拍照功能 / Can extend photo feature
            )
            self.event_bus.publish('weighbridge', event)

        return result

    def get_weighbridge_status(self) -> Dict[str, Any]:
        """获取地磅状态 / Get weighbridge status"""
        return self.weighbridge.get_status()

    # ==================== 电子围栏 / Electronic Fence ====================

    def add_fence_zone(
        self,
        name: str,
        zone_type: ZoneType,
        boundary: list,
        action: str = 'alert'
    ) -> None:
        """
        添加围栏区域 / Add fence zone

        Args:
            name: 区域名称 / Zone name
            zone_type: 区域类型 / Zone type
            boundary: 边界坐标列表 / Boundary coordinates
            action: 触发动作 / Trigger action
        """
        self.fence_simulator.add_zone(name, zone_type, boundary, action)

    def remove_fence_zone(self, name: str) -> bool:
        """移除围栏区域 / Remove fence zone"""
        return self.fence_simulator.remove_zone(name)

    def check_fence_position(self, lat: float, lon: float) -> tuple:
        """
        检查位置是否在围栏内 / Check if position is inside fence

        Returns:
            (是否在围栏内, 区域名称) / (In fence, zone name)
        """
        return self.fence_simulator.check_position(lat, lon)

    # ==================== 业务集成方法 / Business Integration Methods ====================

    async def track_vehicle_to_berth(
        self,
        vehicle_id: int,
        berth_location: tuple,
        on_arrival: Optional[Callable] = None
    ) -> None:
        """
        追踪车辆到泊位 / Track vehicle to berth

        Args:
            vehicle_id: 车辆ID / Vehicle ID
            berth_location: 泊位坐标 (lat, lon) / Berth coordinates
            on_arrival: 到达回调 / Arrival callback
        """
        # 设置目的地 / Set destination
        dest_lat, dest_lon = berth_location
        self.set_vehicle_destination(vehicle_id, dest_lat, dest_lon)

        # 订阅到达事件 / Subscribe to arrival
        def arrival_checker(event: VehicleLocationEvent):
            if event.vehicle_id == vehicle_id:
                # 简单距离检查 / Simple distance check
                import math
                dist = math.sqrt(
                    (event.latitude - dest_lat) ** 2 +
                    (event.longitude - dest_lon) ** 2
                )
                if dist < 0.0001:  # 约10米 / About 10 meters
                    if on_arrival:
                        on_arrival(vehicle_id)
                    self.event_bus.unsubscribe('gps', arrival_checker)

        self.event_bus.subscribe('gps', arrival_checker)

    def get_hardware_status(self) -> Dict[str, Any]:
        """
        获取所有硬件状态 / Get all hardware status

        Returns:
            硬件状态汇总 / Hardware status summary
        """
        return {
            'gps': {
                'registered_vehicles': len(self._gps_callbacks),
                'active_tracks': self.gps_simulator.active_tracks
            },
            'badge': {
                'registered_badges': len(self._badge_callbacks),
                'active_scans': self.badge_simulator.active_badges
            },
            'weighbridge': self.weighbridge.get_status(),
            'fence': {
                'zones_defined': len(self.fence_simulator.zones),
                'zone_names': list(self.fence_simulator.zones.keys())
            },
            'event_subscribers': {
                k: len(v) for k, v in self.event_bus._subscribers.items()
            }
        }


# 全局服务实例 / Global service instance
_hardware_service: Optional[HardwareIntegrationService] = None


def get_hardware_service() -> HardwareIntegrationService:
    """获取硬件服务单例 / Get hardware service singleton"""
    global _hardware_service
    if _hardware_service is None:
        _hardware_service = HardwareIntegrationService()
    return _hardware_service
