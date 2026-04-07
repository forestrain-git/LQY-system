"""
地磅称重模拟器 / Weighbridge Simulator

模拟地磅称重系统，包括：
- 车辆进场称重（毛重）
- 车辆出场称重（皮重）
- 净重计算
- 称重数据记录

Simulates weighbridge system, including:
- Vehicle entry weighing (gross weight)
- Vehicle exit weighing (tare weight)
- Net weight calculation
- Weighing data recording

Author: AI Sprint
Date: 2026-04-07
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class WeighbridgeStatus(str, Enum):
    """地磅状态 / Weighbridge Status"""
    IDLE = "idle"           # 空闲 / Idle
    WEIGHING = "weighing"   # 称重中 / Weighing
    PROCESSING = "processing"  # 处理中 / Processing


class WeightType(str, Enum):
    """称重类型 / Weight Type"""
    GROSS = "gross"     # 毛重 / Gross weight
    TARE = "tare"       # 皮重 / Tare weight
    NET = "net"         # 净重 / Net weight


@dataclass
class WeighingRecord:
    """
    称重记录 / Weighing Record
    """
    record_id: str
    vehicle_id: str
    license_plate: str

    # 重量 / Weights (单位：kg)
    gross_weight: float = 0.0   # 毛重 / Gross weight
    tare_weight: float = 0.0    # 皮重 / Tare weight
    net_weight: float = 0.0     # 净重 / Net weight (calculated)

    # 称重类型 / Weight type for this record
    weight_type: WeightType = WeightType.GROSS

    # 垃圾品类 / Waste type
    waste_type: str = "domestic"  # domestic/kitchen/recyclable/hazardous

    # 时间戳 / Timestamps
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    weighing_time: datetime = field(default_factory=datetime.now)

    # 地磅信息 / Weighbridge info
    weighbridge_id: str = "WB001"
    operator: str = "Operator"

    # 状态 / Status
    is_complete: bool = False   # 是否完成两次称重

    def calculate_net(self):
        """计算净重 / Calculate net weight"""
        if self.gross_weight > 0 and self.tare_weight > 0:
            self.net_weight = self.gross_weight - self.tare_weight


class WeighbridgeSimulator:
    """
    地磅称重模拟器 / Weighbridge Simulator

    模拟地磅的称重流程和数据生成
    Simulates weighbridge weighing process and data generation
    """

    # 车辆参考重量 / Vehicle reference weights
    VEHICLE_WEIGHTS = {
        "small": 3000,      # 小型车 3吨
        "medium": 5000,     # 中型车 5吨
        "large": 8000,      # 大型车 8吨
    }

    # 垃圾密度参考 / Waste density reference (kg/m³)
    WASTE_DENSITY = {
        "domestic": 250,
        "kitchen": 900,
        "recyclable": 150,
        "hazardous": 400,
    }

    def __init__(self, weighbridge_id: str = "WB001"):
        """
        初始化模拟器 / Initialize simulator

        Args:
            weighbridge_id: 地磅编号 / Weighbridge ID
        """
        self.weighbridge_id = weighbridge_id
        self.status = WeighbridgeStatus.IDLE
        self.current_record: Optional[WeighingRecord] = None
        self.records: List[WeighingRecord] = []
        self.record_counter = 0

    def simulate_entry_weighing(
        self,
        vehicle_id: str,
        license_plate: str,
        vehicle_type: str = "medium",
        waste_type: str = "domestic"
    ) -> WeighingRecord:
        """
        模拟进场称重 / Simulate entry weighing

        Args:
            vehicle_id: 车辆ID / Vehicle ID
            license_plate: 车牌号 / License plate
            vehicle_type: 车辆类型 / Vehicle type (small/medium/large)
            waste_type: 垃圾类型 / Waste type

        Returns:
            称重记录 / Weighing record
        """
        self.record_counter += 1
        record_id = f"WG_{datetime.now().strftime('%Y%m%d')}_{self.record_counter:04d}"

        # 基础车重 / Base vehicle weight
        base_weight = self.VEHICLE_WEIGHTS.get(vehicle_type, 5000)

        # 垃圾重量（基于类型随机）/ Waste weight based on type
        load_factor = random.uniform(0.6, 0.95)  # 装载率 60-95%
        max_load = 5000 if vehicle_type == "small" else 8000 if vehicle_type == "medium" else 12000
        waste_weight = max_load * load_factor

        # 毛重 = 车重 + 垃圾重 / Gross = vehicle + waste
        gross_weight = base_weight + waste_weight

        # 添加小随机误差 / Add small random error
        gross_weight += random.uniform(-5, 5)

        record = WeighingRecord(
            record_id=record_id,
            vehicle_id=vehicle_id,
            license_plate=license_plate,
            gross_weight=round(gross_weight, 2),
            weight_type=WeightType.GROSS,
            waste_type=waste_type,
            entry_time=datetime.now(),
            weighbridge_id=self.weighbridge_id,
            is_complete=False
        )

        self.current_record = record
        self.records.append(record)

        return record

    def simulate_exit_weighing(
        self,
        record_id: str,
        vehicle_type: str = "medium"
    ) -> Optional[WeighingRecord]:
        """
        模拟出场称重 / Simulate exit weighing

        Args:
            record_id: 记录ID / Record ID
            vehicle_type: 车辆类型 / Vehicle type

        Returns:
            完成的称重记录 / Completed weighing record
        """
        # 查找记录 / Find record
        record = None
        for r in self.records:
            if r.record_id == record_id:
                record = r
                break

        if not record:
            return None

        # 基础车重 / Base vehicle weight
        base_weight = self.VEHICLE_WEIGHTS.get(vehicle_type, 5000)

        # 皮重（空车重量）/ Tare weight (empty vehicle)
        tare_weight = base_weight + random.uniform(-3, 3)

        record.tare_weight = round(tare_weight, 2)
        record.weight_type = WeightType.NET
        record.exit_time = datetime.now()
        record.is_complete = True

        # 计算净重 / Calculate net weight
        record.calculate_net()

        return record

    def get_record(self, record_id: str) -> Optional[WeighingRecord]:
        """获取称重记录 / Get weighing record"""
        for r in self.records:
            if r.record_id == record_id:
                return r
        return None

    def get_all_records(self, limit: int = 100) -> List[Dict]:
        """获取所有记录 / Get all records"""
        return [
            {
                "record_id": r.record_id,
                "vehicle_id": r.vehicle_id,
                "license_plate": r.license_plate,
                "gross_weight": r.gross_weight,
                "tare_weight": r.tare_weight,
                "net_weight": r.net_weight,
                "waste_type": r.waste_type,
                "is_complete": r.is_complete,
                "entry_time": r.entry_time.isoformat() if r.entry_time else None,
                "exit_time": r.exit_time.isoformat() if r.exit_time else None,
            }
            for r in self.records[-limit:]
        ]

    def get_daily_statistics(self, date: Optional[datetime] = None) -> Dict:
        """
        获取日统计 / Get daily statistics

        Args:
            date: 日期 / Date (default: today)

        Returns:
            统计数据 / Statistics
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")

        day_records = [
            r for r in self.records
            if r.weighing_time.strftime("%Y-%m-%d") == date_str and r.is_complete
        ]

        if not day_records:
            return {
                "date": date_str,
                "total_vehicles": 0,
                "total_weight": 0,
                "waste_by_type": {}
            }

        total_weight = sum(r.net_weight for r in day_records)

        # 按类型统计 / Statistics by type
        waste_by_type = {}
        for r in day_records:
            wt = r.waste_type
            if wt not in waste_by_type:
                waste_by_type[wt] = {"count": 0, "weight": 0}
            waste_by_type[wt]["count"] += 1
            waste_by_type[wt]["weight"] += r.net_weight

        return {
            "date": date_str,
            "total_vehicles": len(day_records),
            "total_weight": round(total_weight, 2),
            "avg_weight": round(total_weight / len(day_records), 2),
            "waste_by_type": waste_by_type
        }
