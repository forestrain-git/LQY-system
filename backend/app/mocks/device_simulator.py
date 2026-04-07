"""
设备传感器模拟器 / Device Sensor Simulator

模拟各类设备的传感器数据：
- 振动传感器 / Vibration sensors
- 温度传感器 / Temperature sensors
- 电流传感器 / Current sensors
- 压力传感器 / Pressure sensors

Author: AI Sprint
Date: 2026-04-07
"""

import random
import math
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class SensorType(str, Enum):
    """传感器类型 / Sensor Type"""
    VIBRATION = "vibration"     # 振动 / Vibration (mm/s)
    TEMPERATURE = "temperature" # 温度 / Temperature (°C)
    CURRENT = "current"         # 电流 / Current (A)
    PRESSURE = "pressure"       # 压力 / Pressure (kPa)
    HUMIDITY = "humidity"       # 湿度 / Humidity (%)


@dataclass
class SensorReading:
    """传感器读数 / Sensor Reading"""
    device_id: str
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime
    is_anomaly: bool = False


class DeviceSimulator:
    """
    设备传感器模拟器 / Device Sensor Simulator

    模拟各类环卫设备的传感器数据生成
    Simulates sensor data generation for various sanitation equipment
    """

    # 设备类型配置 / Device type configurations
    DEVICE_CONFIGS = {
        "compressor": {  # 压缩机
            "sensors": {
                SensorType.VIBRATION: {"min": 2, "max": 10, "unit": "mm/s", "threshold": 8},
                SensorType.TEMPERATURE: {"min": 40, "max": 80, "unit": "°C", "threshold": 75},
                SensorType.CURRENT: {"min": 10, "max": 50, "unit": "A", "threshold": 45},
            }
        },
        "pump": {  # 泵
            "sensors": {
                SensorType.VIBRATION: {"min": 1, "max": 8, "unit": "mm/s", "threshold": 6},
                SensorType.TEMPERATURE: {"min": 30, "max": 60, "unit": "°C", "threshold": 55},
                SensorType.CURRENT: {"min": 5, "max": 30, "unit": "A", "threshold": 28},
                SensorType.PRESSURE: {"min": 100, "max": 500, "unit": "kPa", "threshold": 450},
            }
        },
        "fan": {  # 风机
            "sensors": {
                SensorType.VIBRATION: {"min": 1, "max": 6, "unit": "mm/s", "threshold": 5},
                SensorType.TEMPERATURE: {"min": 25, "max": 50, "unit": "°C", "threshold": 45},
                SensorType.CURRENT: {"min": 3, "max": 20, "unit": "A", "threshold": 18},
            }
        },
        "conveyor": {  # 传送带
            "sensors": {
                SensorType.VIBRATION: {"min": 0.5, "max": 5, "unit": "mm/s", "threshold": 4},
                SensorType.TEMPERATURE: {"min": 20, "max": 45, "unit": "°C", "threshold": 40},
                SensorType.CURRENT: {"min": 2, "max": 15, "unit": "A", "threshold": 13},
            }
        }
    }

    def __init__(self):
        """初始化模拟器 / Initialize simulator"""
        self.devices: Dict[str, Dict] = {}
        self.readings: Dict[str, List[SensorReading]] = {}
        self._init_devices()

    def _init_devices(self):
        """初始化设备 / Initialize devices"""
        device_types = list(self.DEVICE_CONFIGS.keys())

        for i in range(10):  # 10个设备
            device_type = device_types[i % len(device_types)]
            device_id = f"DEV_{device_type.upper()}_{100 + i:03d}"

            self.devices[device_id] = {
                "type": device_type,
                "name": f"{device_type.capitalize()}-{i+1}",
                "status": "running",
                "config": self.DEVICE_CONFIGS[device_type]
            }

            self.readings[device_id] = []

    def generate_readings(self, device_id: Optional[str] = None) -> List[SensorReading]:
        """
        生成传感器读数 / Generate sensor readings

        Args:
            device_id: 指定设备ID / Specific device ID (None for all)

        Returns:
            读数列表 / List of readings
        """
        new_readings = []
        timestamp = datetime.now()

        devices_to_update = [device_id] if device_id else list(self.devices.keys())

        for did in devices_to_update:
            if did not in self.devices:
                continue

            device = self.devices[did]
            config = device["config"]

            for sensor_type, sensor_config in config["sensors"].items():
                # 正常范围内的随机值 / Random value within normal range
                base_value = random.uniform(sensor_config["min"], sensor_config["max"])

                # 偶尔产生异常值 / Occasionally generate anomaly
                is_anomaly = random.random() < 0.02  # 2%概率异常
                if is_anomaly:
                    base_value *= random.uniform(1.2, 1.5)  # 超出正常范围

                reading = SensorReading(
                    device_id=did,
                    sensor_id=f"{did}_{sensor_type.value}",
                    sensor_type=sensor_type,
                    value=round(base_value, 2),
                    unit=sensor_config["unit"],
                    timestamp=timestamp,
                    is_anomaly=is_anomaly
                )

                new_readings.append(reading)
                self.readings[did].append(reading)

                # 限制历史记录数 / Limit history
                if len(self.readings[did]) > 1000:
                    self.readings[did].pop(0)

        return new_readings

    def get_device_status(self, device_id: str) -> Dict:
        """获取设备状态 / Get device status"""
        if device_id not in self.devices:
            return {}

        device = self.devices[device_id]
        recent_readings = self.readings[device_id][-10:] if self.readings[device_id] else []

        # 检查是否有异常 / Check for anomalies
        has_anomaly = any(r.is_anomaly for r in recent_readings)

        return {
            "device_id": device_id,
            "type": device["type"],
            "name": device["name"],
            "status": "warning" if has_anomaly else device["status"],
            "last_readings": [
                {
                    "sensor": r.sensor_type.value,
                    "value": r.value,
                    "unit": r.unit,
                    "anomaly": r.is_anomaly,
                    "time": r.timestamp.isoformat()
                }
                for r in recent_readings[-5:]
            ]
        }

    def get_all_devices_status(self) -> List[Dict]:
        """获取所有设备状态 / Get all device statuses"""
        return [self.get_device_status(did) for did in self.devices.keys()]
