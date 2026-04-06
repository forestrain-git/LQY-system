#!/usr/bin/env python3
"""设备数据模拟器

模拟多台环卫设备发送传感器数据到MQTT Broker
"""

import argparse
import asyncio
import json
import logging
import random
import signal
import sys
from dataclasses import dataclass
from datetime import datetime, timezone

import aiomqtt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class DeviceConfig:
    """设备配置"""

    device_id: str
    base_temp: float = 50.0
    base_vibration: float = 1.0
    base_current: float = 10.0
    anomaly_prob: float = 0.05  # 异常概率


class VirtualDevice:
    """虚拟设备"""

    def __init__(self, config: DeviceConfig, broker: str, port: int):
        self.config = config
        self.broker = broker
        self.port = port
        self.client: aiomqtt.Client | None = None
        self.running = False
        self.anomaly_mode = False
        self.anomaly_counter = 0

    async def start(self):
        """启动设备"""
        self.running = True
        self.client = aiomqtt.Client(
            hostname=self.broker,
            port=self.port,
            identifier=f"simulator_{self.config.device_id}",
        )
        logger.info(f"设备 {self.config.device_id} 已启动")

        try:
            async with self.client:
                while self.running:
                    await self._send_data()
                    await asyncio.sleep(10)  # 10秒发送一次
        except aiomqtt.MqttError as e:
            logger.error(f"设备 {self.config.device_id} MQTT错误: {e}")
        except Exception as e:
            logger.error(f"设备 {self.config.device_id} 异常: {e}")

    def stop(self):
        """停止设备"""
        self.running = False

    def _generate_data(self) -> dict:
        """生成传感器数据"""
        # 决定是否进入异常模式（5%概率）
        if not self.anomaly_mode and random.random() < self.config.anomaly_prob:
            self.anomaly_mode = True
            self.anomaly_counter = random.randint(3, 6)  # 持续3-6个周期
            logger.warning(f"设备 {self.config.device_id} 进入异常模式")

        # 生成数据
        if self.anomaly_mode:
            # 异常数据（温度高、振动大）
            temp = self.config.base_temp + random.uniform(20, 30)
            vibration = self.config.base_vibration + random.uniform(3, 8)
            current = self.config.base_current + random.uniform(5, 10)
            self.anomaly_counter -= 1
            if self.anomaly_counter <= 0:
                self.anomaly_mode = False
                logger.info(f"设备 {self.config.device_id} 恢复正常")
        else:
            # 正常数据 + 随机波动
            temp = self.config.base_temp + random.uniform(-5, 5)
            vibration = self.config.base_vibration + random.uniform(-0.5, 0.5)
            current = self.config.base_current + random.uniform(-2, 2)

        return {
            "device_id": self.config.device_id,
            "temperature": round(temp, 2),
            "vibration": round(vibration, 2),
            "current": round(current, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "anomaly": self.anomaly_mode,
        }

    async def _send_data(self):
        """发送数据到MQTT"""
        if not self.client:
            return

        data = self._generate_data()
        topic = f"sensors/{self.config.device_id}/data"

        try:
            await self.client.publish(topic, json.dumps(data))
            logger.debug(f"设备 {self.config.device_id} 发送数据: {data}")
        except Exception as e:
            logger.error(f"设备 {self.config.device_id} 发送失败: {e}")


class Simulator:
    """模拟器管理器"""

    def __init__(self, broker: str, port: int, device_count: int):
        self.broker = broker
        self.port = port
        self.device_count = device_count
        self.devices: list[VirtualDevice] = []
        self.tasks: list[asyncio.Task] = []

    def create_devices(self):
        """创建设备"""
        for i in range(1, self.device_count + 1):
            device_id = f"DEV{i:03d}"

            # DEV001和DEV002更容易异常
            anomaly_prob = 0.15 if i <= 2 else 0.05

            config = DeviceConfig(
                device_id=device_id,
                base_temp=random.uniform(45, 55),
                base_vibration=random.uniform(0.8, 1.5),
                base_current=random.uniform(8, 12),
                anomaly_prob=anomaly_prob,
            )

            device = VirtualDevice(config, self.broker, self.port)
            self.devices.append(device)

        logger.info(f"已创建 {self.device_count} 台虚拟设备")

    async def start(self):
        """启动所有设备"""
        self.create_devices()

        # 启动所有设备
        for device in self.devices:
            task = asyncio.create_task(device.start())
            self.tasks.append(task)

        logger.info(f"模拟器已启动，{self.device_count} 台设备运行中...")

        # 等待所有任务
        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("模拟器任务被取消")

    def stop(self):
        """停止所有设备"""
        logger.info("正在停止模拟器...")
        for device in self.devices:
            device.stop()

        # 取消所有任务
        for task in self.tasks:
            task.cancel()


def main():
    parser = argparse.ArgumentParser(description="设备数据模拟器")
    parser.add_argument(
        "--broker",
        default="localhost",
        help="MQTT Broker地址 (默认: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=1883,
        help="MQTT端口 (默认: 1883)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="设备数量 (默认: 10)",
    )

    args = parser.parse_args()

    simulator = Simulator(args.broker, args.port, args.count)

    # 信号处理
    def signal_handler(sig, frame):
        logger.info("收到停止信号...")
        simulator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动
    try:
        asyncio.run(simulator.start())
    except KeyboardInterrupt:
        logger.info("用户中断")
        simulator.stop()


if __name__ == "__main__":
    main()
