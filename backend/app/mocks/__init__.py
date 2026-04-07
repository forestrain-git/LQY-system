"""
硬件模拟系统 / Hardware Simulation System

模拟各类硬件设备的数据生成，用于开发和测试
Simulates data generation for various hardware devices for development and testing

包含模块 / Includes:
- fence_simulator: 电子围栏模拟 / Electronic fence simulation
- badge_simulator: 人员工牌模拟 / Staff badge simulation
- vehicle_gps_simulator: 车辆GPS模拟 / Vehicle GPS simulation
- weighbridge_simulator: 地磅称重模拟 / Weighbridge simulation
- device_simulator: 设备传感器模拟 / Device sensor simulation

Author: AI Sprint
Date: 2026-04-07
"""

from .fence_simulator import FenceSimulator
from .badge_simulator import BadgeSimulator
from .vehicle_gps_simulator import VehicleGPSSimulator
from .weighbridge_simulator import WeighbridgeSimulator
from .device_simulator import DeviceSimulator

__all__ = [
    "FenceSimulator",
    "BadgeSimulator",
    "VehicleGPSSimulator",
    "WeighbridgeSimulator",
    "DeviceSimulator",
]
