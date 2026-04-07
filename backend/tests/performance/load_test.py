"""
性能测试 - 负载测试
模拟高并发设备，测试系统性能
"""

import asyncio
import json
import logging
import statistics
import sys
import time
from datetime import datetime
from typing import Dict, List

import aiomqtt
import aiohttp

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """性能指标收集器"""

    def __init__(self):
        self.message_latencies: List[float] = []
        self.api_latencies: List[float] = []
        self.errors: List[str] = []
        self.start_time: float = 0
        self.message_count = 0

    def start(self):
        """开始计时"""
        self.start_time = time.time()

    def record_message_latency(self, latency_ms: float):
        """记录消息延迟"""
        self.message_latencies.append(latency_ms)
        self.message_count += 1

    def record_api_latency(self, latency_ms: float):
        """记录API延迟"""
        self.api_latencies.append(latency_ms)

    def record_error(self, error: str):
        """记录错误"""
        self.errors.append(error)

    def get_summary(self) -> Dict:
        """获取性能摘要"""
        duration = time.time() - self.start_time

        summary = {
            "duration_seconds": duration,
            "total_messages": self.message_count,
            "messages_per_second": self.message_count / duration if duration > 0 else 0,
            "error_count": len(self.errors),
        }

        # 消息延迟统计
        if self.message_latencies:
            summary["message_latency"] = {
                "avg_ms": statistics.mean(self.message_latencies),
                "min_ms": min(self.message_latencies),
                "max_ms": max(self.message_latencies),
                "p50_ms": statistics.median(self.message_latencies),
                "p95_ms": sorted(self.message_latencies)[int(len(self.message_latencies) * 0.95)],
                "p99_ms": sorted(self.message_latencies)[int(len(self.message_latencies) * 0.99)],
            }

        # API延迟统计
        if self.api_latencies:
            summary["api_latency"] = {
                "avg_ms": statistics.mean(self.api_latencies),
                "min_ms": min(self.api_latencies),
                "max_ms": max(self.api_latencies),
                "p95_ms": sorted(self.api_latencies)[int(len(self.api_latencies) * 0.95)],
            }

        return summary


class LoadTester:
    """负载测试器"""

    def __init__(self,
                 device_count: int = 50,
                 duration: float = 60.0,
                 message_interval: float = 5.0,
                 mqtt_broker: str = "localhost",
                 mqtt_port: int = 1883,
                 api_url: str = "http://localhost:8000"):
        self.device_count = device_count
        self.duration = duration
        self.message_interval = message_interval
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.api_url = api_url
        self.metrics = PerformanceMetrics()
        self.running = False

    async def simulate_device(self, device_id: str):
        """模拟单个设备"""
        try:
            async with aiomqtt.Client(
                hostname=self.mqtt_broker,
                port=self.mqtt_port,
                identifier=f"load_test_{device_id}",
            ) as client:

                start_time = time.time()
                message_count = 0

                while self.running and (time.time() - start_time) < self.duration:
                    # 生成数据
                    data = {
                        "device_id": device_id,
                        "temperature": 60 + message_count % 20,
                        "vibration": 3.0 + (message_count % 10) / 10,
                        "current": 15 + message_count % 5,
                        "timestamp": datetime.now().isoformat(),
                    }

                    # 发送数据
                    msg_start = time.time()
                    await client.publish(
                        f"sensors/{device_id}/data",
                        json.dumps(data)
                    )
                    msg_latency = (time.time() - msg_start) * 1000
                    self.metrics.record_message_latency(msg_latency)

                    message_count += 1
                    await asyncio.sleep(self.message_interval)

        except Exception as e:
            self.metrics.record_error(f"Device {device_id}: {e}")

    async def test_api_performance(self):
        """测试API性能"""
        async with aiohttp.ClientSession() as session:
            endpoints = [
                "/health",
                "/api/v1/devices",
                "/api/v1/alerts",
            ]

            for endpoint in endpoints:
                try:
                    start = time.time()
                    async with session.get(f"{self.api_url}{endpoint}") as resp:
                        await resp.text()
                        latency = (time.time() - start) * 1000
                        self.metrics.record_api_latency(latency)
                except Exception as e:
                    self.metrics.record_error(f"API {endpoint}: {e}")

    async def run(self):
        """运行负载测试"""
        print("=" * 60)
        print("负载测试配置")
        print("=" * 60)
        print(f"设备数量: {self.device_count}")
        print(f"测试时长: {self.duration} 秒")
        print(f"消息间隔: {self.message_interval} 秒")
        print(f"MQTT Broker: {self.mqtt_broker}:{self.mqtt_port}")
        print(f"API地址: {self.api_url}")
        print("=" * 60)

        self.running = True
        self.metrics.start()

        # 创建设备任务
        tasks = []
        for i in range(self.device_count):
            device_id = f"LOAD{i+1:03d}"
            task = asyncio.create_task(self.simulate_device(device_id))
            tasks.append(task)

        # 定期测试API
        api_task = asyncio.create_task(self._periodic_api_test())

        print(f"\n启动 {self.device_count} 个设备模拟器...")
        print("测试中，请等待...\n")

        # 等待所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)
        self.running = False

        try:
            await asyncio.wait_for(api_task, timeout=5.0)
        except asyncio.TimeoutError:
            pass

        # 输出结果
        self._print_results()

    async def _periodic_api_test(self):
        """定期测试API"""
        while self.running:
            await self.test_api_performance()
            await asyncio.sleep(5.0)

    def _print_results(self):
        """打印测试结果"""
        summary = self.metrics.get_summary()

        print("\n" + "=" * 60)
        print("测试结果")
        print("=" * 60)

        print(f"\n基础指标:")
        print(f"  测试时长: {summary['duration_seconds']:.2f} 秒")
        print(f"  总消息数: {summary['total_messages']}")
        print(f"  消息速率: {summary['messages_per_second']:.2f}  msg/s")
        print(f"  错误数量: {summary['error_count']}")

        if 'message_latency' in summary:
            lat = summary['message_latency']
            print(f"\n消息延迟 (MQTT -> 后端):")
            print(f"  平均: {lat['avg_ms']:.2f} ms")
            print(f"  最小: {lat['min_ms']:.2f} ms")
            print(f"  最大: {lat['max_ms']:.2f} ms")
            print(f"  P50:  {lat['p50_ms']:.2f} ms")
            print(f"  P95:  {lat['p95_ms']:.2f} ms")
            print(f"  P99:  {lat['p99_ms']:.2f} ms")

        if 'api_latency' in summary:
            lat = summary['api_latency']
            print(f"\nAPI延迟:")
            print(f"  平均: {lat['avg_ms']:.2f} ms")
            print(f"  P95:  {lat['p95_ms']:.2f} ms")

        # 性能评估
        print("\n" + "=" * 60)
        print("性能评估")
        print("=" * 60)

        success = True

        if summary['messages_per_second'] < 10:
            print("✗ 消息速率过低 (< 10 msg/s)")
            success = False
        else:
            print("✓ 消息速率正常")

        if 'message_latency' in summary:
            if summary['message_latency']['p95_ms'] > 200:
                print("✗ 消息延迟过高 (P95 > 200ms)")
                success = False
            else:
                print("✓ 消息延迟正常")

        if summary['error_count'] > 0:
            print(f"✗ 存在 {summary['error_count']} 个错误")
            success = False
        else:
            print("✓ 无错误")

        print("=" * 60)

        return success


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='负载测试')
    parser.add_argument('--devices', type=int, default=50, help='设备数量')
    parser.add_argument('--duration', type=float, default=60.0, help='测试时长(秒)')
    parser.add_argument('--interval', type=float, default=5.0, help='消息间隔(秒)')
    parser.add_argument('--broker', type=str, default='localhost', help='MQTT broker')
    parser.add_argument('--port', type=int, default=1883, help='MQTT端口')
    parser.add_argument('--api', type=str, default='http://localhost:8000', help='API地址')

    args = parser.parse_args()

    tester = LoadTester(
        device_count=args.devices,
        duration=args.duration,
        message_interval=args.interval,
        mqtt_broker=args.broker,
        mqtt_port=args.port,
        api_url=args.api,
    )

    await tester.run()


if __name__ == "__main__":
    asyncio.run(main())
