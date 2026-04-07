"""
设备模拟器 - 用于系统集成测试
模拟多个设备发送MQTT数据到后端
"""

import asyncio
import json
import logging
import random
import sys
import time
from datetime import datetime, timezone
from typing import List, Optional

import aiomqtt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeviceSimulator:
    """模拟单个设备的行为"""

    def __init__(self, device_id: str, mqtt_broker: str = "localhost", mqtt_port: int = 1883):
        self.device_id = device_id
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.client: Optional[aiomqtt.Client] = None
        self.running = False

        # 设备特性（模拟不同类型的设备）
        self.base_temp = random.uniform(50, 60)  # 基础温度
        self.base_vibration = random.uniform(2.0, 3.0)  # 基础振动
        self.base_current = random.uniform(10, 15)  # 基础电流

    async def connect(self):
        """连接到MQTT Broker"""
        try:
            self.client = aiomqtt.Client(
                hostname=self.mqtt_broker,
                port=self.mqtt_port,
                identifier=f"simulator_{self.device_id}",
            )
            await self.client.__aenter__()
            logger.info(f"设备 {self.device_id} 已连接到MQTT")
        except Exception as e:
            logger.error(f"设备 {self.device_id} 连接失败: {e}")
            raise

    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.__aexit__(None, None, None)
            logger.info(f"设备 {self.device_id} 已断开")

    def generate_sensor_data(self, anomaly: bool = False) -> dict:
        """生成传感器数据"""
        # 正常数据范围
        temp = self.base_temp + random.uniform(-5, 5)
        vibration = self.base_vibration + random.uniform(-0.5, 0.5)
        current = self.base_current + random.uniform(-2, 2)

        # 如果要求异常数据，生成超出阈值的值
        if anomaly:
            anomaly_type = random.choice(['temp', 'vibration', 'current'])
            if anomaly_type == 'temp':
                temp = random.uniform(85, 95)  # 过高温度
            elif anomaly_type == 'vibration':
                vibration = random.uniform(6.5, 8.0)  # 过高振动
            else:
                current = random.uniform(22, 25)  # 过高电流

        return {
            "device_id": self.device_id,
            "temperature": round(temp, 2),
            "vibration": round(vibration, 2),
            "current": round(current, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def send_data(self, data: dict):
        """发送数据到MQTT"""
        if not self.client:
            return

        topic = f"sensors/{self.device_id}/data"
        payload = json.dumps(data)

        try:
            await self.client.publish(topic, payload)
            logger.debug(f"设备 {self.device_id} 发送数据: {data}")
        except Exception as e:
            logger.error(f"设备 {self.device_id} 发送失败: {e}")

    async def run(self, interval: float = 5.0, anomaly_prob: float = 0.1):
        """运行设备模拟器"""
        self.running = True
        await self.connect()

        try:
            while self.running:
                # 随机生成异常数据（10%概率）
                is_anomaly = random.random() < anomaly_prob
                data = self.generate_sensor_data(anomaly=is_anomaly)

                await self.send_data(data)

                if is_anomaly:
                    logger.info(f"设备 {self.device_id} 生成异常数据: {data}")

                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info(f"设备 {self.device_id} 模拟器被取消")
        finally:
            await self.disconnect()

    def stop(self):
        """停止模拟器"""
        self.running = False


class SimulatorCluster:
    """设备模拟器集群"""

    def __init__(self, device_count: int, mqtt_broker: str = "localhost", mqtt_port: int = 1883):
        self.device_count = device_count
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.simulators: List[DeviceSimulator] = []
        self.tasks: List[asyncio.Task] = []

    def create_simulators(self):
        """创建设备模拟器"""
        for i in range(self.device_count):
            device_id = f"DEV{i+1:03d}"
            simulator = DeviceSimulator(device_id, self.mqtt_broker, self.mqtt_port)
            self.simulators.append(simulator)

        logger.info(f"创建了 {self.device_count} 个设备模拟器")

    async def start(self, interval: float = 5.0, anomaly_prob: float = 0.1):
        """启动所有模拟器"""
        self.create_simulators()

        # 创建任务
        for sim in self.simulators:
            task = asyncio.create_task(sim.run(interval, anomaly_prob))
            self.tasks.append(task)

        logger.info(f"启动了 {len(self.tasks)} 个模拟任务")

    async def stop(self):
        """停止所有模拟器"""
        # 停止所有模拟器
        for sim in self.simulators:
            sim.stop()

        # 取消所有任务
        for task in self.tasks:
            task.cancel()

        # 等待任务完成
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        logger.info("所有模拟器已停止")

    async def run_for_duration(self, duration: float, interval: float = 5.0, anomaly_prob: float = 0.1):
        """运行指定时间"""
        await self.start(interval, anomaly_prob)

        try:
            await asyncio.sleep(duration)
        except asyncio.CancelledError:
            logger.info("模拟被中断")
        finally:
            await self.stop()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='设备模拟器')
    parser.add_argument('--count', type=int, default=5, help='设备数量')
    parser.add_argument('--interval', type=float, default=5.0, help='数据发送间隔（秒）')
    parser.add_argument('--duration', type=float, default=0, help='运行时长（秒），0表示永久运行')
    parser.add_argument('--anomaly', type=float, default=0.1, help='异常数据概率（0-1）')
    parser.add_argument('--broker', type=str, default='localhost', help='MQTT Broker地址')
    parser.add_argument('--port', type=int, default=1883, help='MQTT端口')

    args = parser.parse_args()

    cluster = SimulatorCluster(
        device_count=args.count,
        mqtt_broker=args.broker,
        mqtt_port=args.port
    )

    try:
        if args.duration > 0:
            logger.info(f"启动模拟: {args.count} 个设备, 运行 {args.duration} 秒")
            await cluster.run_for_duration(args.duration, args.interval, args.anomaly)
        else:
            logger.info(f"启动模拟: {args.count} 个设备, 永久运行 (按Ctrl+C停止)")
            await cluster.start(args.interval, args.anomaly)

            # 永久运行
            while True:
                await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止...")
        await cluster.stop()
        logger.info("模拟器已停止")


if __name__ == "__main__":
    asyncio.run(main())
