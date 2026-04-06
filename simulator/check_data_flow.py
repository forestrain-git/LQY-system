#!/usr/bin/env python3
"""数据流验证脚本

验证完整数据流: Simulator -> MQTT -> Backend -> WebSocket
"""

import asyncio
import json
import logging
import sys
from datetime import datetime

import aiomqtt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DataFlowValidator:
    """数据流验证器"""

    def __init__(self):
        self.mqtt_connected = False
        self.websocket_connected = False
        self.messages_received = []
        self.anomalies_detected = []
        self.test_duration = 60  # 测试60秒

    async def test_mqtt_broker(self) -> bool:
        """测试MQTT Broker连接"""
        try:
            async with aiomqtt.Client("localhost", 1883) as client:
                await client.subscribe("sensors/+/data")
                logger.info("✅ MQTT Broker连接成功 (端口1883)")
                return True
        except Exception as e:
            logger.error(f"❌ MQTT Broker连接失败: {e}")
            return False

    async def test_emqx_dashboard(self) -> bool:
        """测试EMQX Dashboard"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:18083/api/v5/status", auth=aiohttp.BasicAuth("admin", "public")) as resp:
                    if resp.status == 200:
                        logger.info("✅ EMQX Dashboard可访问 (端口18083)")
                        return True
        except Exception as e:
            logger.warning(f"⚠️ EMQX Dashboard检查失败: {e}")
        return False

    async def test_backend_api(self) -> bool:
        """测试后端API"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        logger.info(f"✅ 后端API运行正常: {data}")
                        return True
        except Exception as e:
            logger.error(f"❌ 后端API检查失败: {e}")
        return False

    async def test_websocket(self) -> bool:
        """测试WebSocket连接"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect("http://localhost:8000/ws/devices") as ws:
                    await ws.send_str("ping")
                    msg = await asyncio.wait_for(ws.receive(), timeout=5)
                    if msg.data == "pong":
                        logger.info("✅ WebSocket连接正常")
                        return True
        except Exception as e:
            logger.error(f"❌ WebSocket检查失败: {e}")
        return False

    async def listen_mqtt(self):
        """监听MQTT数据"""
        try:
            async with aiomqtt.Client("localhost", 1883) as client:
                await client.subscribe("sensors/+/data")
                logger.info("开始监听MQTT数据...")

                async for message in client.messages:
                    try:
                        data = json.loads(message.payload.decode())
                        self.messages_received.append(data)

                        if data.get("anomaly"):
                            self.anomalies_detected.append(data)
                            logger.warning(f"🔴 检测到异常数据: {data['device_id']} - 温度:{data.get('temperature')}°C")

                        if len(self.messages_received) % 10 == 0:
                            logger.info(f"已接收 {len(self.messages_received)} 条消息")

                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.error(f"MQTT监听异常: {e}")

    async def listen_websocket(self):
        """监听WebSocket数据"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect("http://localhost:8000/ws/devices") as ws:
                    logger.info("WebSocket已连接，等待数据...")
                    self.websocket_connected = True
                    ws_msg_count = 0

                    while True:
                        try:
                            msg = await asyncio.wait_for(ws.receive(), timeout=1)
                            if msg.type == aiohttp.WSMsgType.TEXT and msg.data != "pong":
                                data = json.loads(msg.data)
                                if data.get("type") == "sensor_data":
                                    ws_msg_count += 1
                                    if ws_msg_count % 10 == 0:
                                        logger.debug(f"WebSocket累计收到: {ws_msg_count} 条")
                        except asyncio.TimeoutError:
                            continue
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            logger.error(f"WebSocket监听异常: {e}")

    async def run_test(self):
        """运行完整测试"""
        logger.info("=" * 50)
        logger.info("开始数据流验证测试")
        logger.info("=" * 50)

        # 基础连接测试
        checks = [
            ("MQTT Broker", self.test_mqtt_broker()),
            ("EMQX Dashboard", self.test_emqx_dashboard()),
            ("后端API", self.test_backend_api()),
            ("WebSocket", self.test_websocket()),
        ]

        results = []
        for name, coro in checks:
            result = await coro
            results.append((name, result))

        # 如果基础连接都失败，提前退出
        if not all(r[1] for r in results):
            logger.error("\n基础连接测试未通过，请检查服务状态")
            return False

        # 启动数据监听
        logger.info("\n" + "=" * 50)
        logger.info("启动数据流监听 (60秒)...")
        logger.info("请确保设备模拟器正在运行: python simulator/device_simulator.py")
        logger.info("=" * 50)

        mqtt_task = asyncio.create_task(self.listen_mqtt())
        ws_task = asyncio.create_task(self.listen_websocket())

        # 运行测试
        await asyncio.sleep(self.test_duration)

        # 取消任务
        mqtt_task.cancel()
        ws_task.cancel()

        try:
            await mqtt_task
        except asyncio.CancelledError:
            pass

        try:
            await ws_task
        except asyncio.CancelledError:
            pass

        # 生成报告
        self._print_report()
        return len(self.messages_received) > 0

    def _print_report(self):
        """打印测试报告"""
        logger.info("\n" + "=" * 50)
        logger.info("数据流验证报告")
        logger.info("=" * 50)

        logger.info(f"\n📊 统计信息:")
        logger.info(f"  - 测试时长: {self.test_duration} 秒")
        logger.info(f"  - MQTT消息接收: {len(self.messages_received)} 条")
        logger.info(f"  - 异常事件检测: {len(self.anomalies_detected)} 次")

        if self.messages_received:
            devices = set(m.get("device_id") for m in self.messages_received)
            logger.info(f"  - 活跃设备数: {len(devices)} 台")
            logger.info(f"  - 设备列表: {', '.join(sorted(devices))}")

            # 计算平均频率
            avg_interval = self.test_duration / (len(self.messages_received) / len(devices))
            logger.info(f"  - 平均发送间隔: {avg_interval:.1f} 秒/设备")

        if self.anomalies_detected:
            logger.info(f"\n🔴 异常事件详情:")
            for anomaly in self.anomalies_detected[:5]:  # 只显示前5个
                logger.info(f"  - {anomaly['device_id']}: 温度={anomaly.get('temperature')}°C, "
                          f"振动={anomaly.get('vibration')}mm/s, 电流={anomaly.get('current')}A")

        logger.info("\n" + "=" * 50)
        if len(self.messages_received) > 0:
            logger.info("✅ 数据流验证通过!")
        else:
            logger.info("❌ 未接收到任何数据，请检查设备模拟器")
        logger.info("=" * 50)


async def main():
    validator = DataFlowValidator()
    success = await validator.run_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
