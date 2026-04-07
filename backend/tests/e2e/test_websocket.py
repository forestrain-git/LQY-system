"""
WebSocket E2E 测试
测试实时数据推送功能
"""

import asyncio
import json
import sys
import time
from datetime import datetime

import websockets
import aiohttp


class WebSocketTester:
    """WebSocket 测试器"""

    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.ws_url = f"{base_url}/ws"
        self.received_messages = []
        self.latencies = []

    async def test_connection(self):
        """测试基础连接"""
        print("测试1: WebSocket 基础连接...")

        try:
            async with websockets.connect(self.ws_url) as ws:
                print("  ✓ WebSocket 连接成功")

                # 发送ping
                await ws.send(json.dumps({"type": "ping"}))
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)

                if data.get("type") == "pong":
                    print("  ✓ Ping/Pong 测试通过")
                    return True
                else:
                    print(f"  ✗ 意外响应: {data}")
                    return False

        except Exception as e:
            print(f"  ✗ 连接失败: {e}")
            return False

    async def test_realtime_data(self, duration: float = 10.0):
        """测试实时数据接收"""
        print(f"\n测试2: 实时数据接收 ({duration}秒)...")

        start_time = time.time()
        message_count = 0

        try:
            async with websockets.connect(self.ws_url) as ws:
                print("  等待实时数据...")

                while time.time() - start_time < duration:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(message)

                        if data.get("type") == "sensor_data":
                            message_count += 1
                            self.received_messages.append(data)

                            if message_count % 10 == 0:
                                print(f"  已接收 {message_count} 条消息")

                    except asyncio.TimeoutError:
                        continue

            print(f"  ✓ 共接收 {message_count} 条实时消息")
            return message_count > 0

        except Exception as e:
            print(f"  ✗ 测试失败: {e}")
            return False

    async def test_latency(self, count: int = 10):
        """测试消息延迟"""
        print(f"\n测试3: 消息延迟测试 ({count}次)...")

        try:
            async with websockets.connect(self.ws_url) as ws:
                latencies = []

                for i in range(count):
                    # 发送ping并计时
                    start = time.time()
                    await ws.send(json.dumps({"type": "ping"}))

                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    end = time.time()

                    latency = (end - start) * 1000  # 转换为毫秒
                    latencies.append(latency)

                    await asyncio.sleep(0.5)

                avg_latency = sum(latencies) / len(latencies)
                max_latency = max(latencies)
                min_latency = min(latencies)

                print(f"  ✓ 平均延迟: {avg_latency:.2f}ms")
                print(f"  ✓ 最小延迟: {min_latency:.2f}ms")
                print(f"  ✓ 最大延迟: {max_latency:.2f}ms")

                return avg_latency < 100  # 平均延迟应小于100ms

        except Exception as e:
            print(f"  ✗ 延迟测试失败: {e}")
            return False

    async def test_reconnection(self):
        """测试断线重连"""
        print("\n测试4: 断线重连测试...")

        try:
            # 第一次连接
            async with websockets.connect(self.ws_url) as ws:
                await ws.send(json.dumps({"type": "ping"}))
                response = await ws.recv()
                print("  ✓ 第一次连接成功")

            # 等待后重新连接
            await asyncio.sleep(1)

            async with websockets.connect(self.ws_url) as ws:
                await ws.send(json.dumps({"type": "ping"}))
                response = await ws.recv()
                print("  ✓ 重连成功")

            return True

        except Exception as e:
            print(f"  ✗ 重连测试失败: {e}")
            return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("WebSocket E2E 测试开始")
        print("=" * 60)

        results = []

        # 测试1: 基础连接
        results.append(("连接测试", await self.test_connection()))

        # 测试2: 实时数据
        results.append(("实时数据", await self.test_realtime_data(duration=5.0)))

        # 测试3: 延迟测试
        results.append(("延迟测试", await self.test_latency(count=5)))

        # 测试4: 重连测试
        results.append(("重连测试", await self.test_reconnection()))

        # 总结
        print("\n" + "=" * 60)
        print("测试结果总结")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{name:20s} {status}")

        print(f"\n总计: {passed}/{total} 通过")

        return passed == total


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='WebSocket E2E 测试')
    parser.add_argument('--url', type=str, default='ws://localhost:8000',
                        help='WebSocket URL')
    parser.add_argument('--test', type=str, default='all',
                        choices=['all', 'connection', 'realtime', 'latency', 'reconnect'],
                        help='测试类型')

    args = parser.parse_args()

    tester = WebSocketTester(args.url)

    if args.test == 'all':
        success = await tester.run_all_tests()
    elif args.test == 'connection':
        success = await tester.test_connection()
    elif args.test == 'realtime':
        success = await tester.test_realtime_data()
    elif args.test == 'latency':
        success = await tester.test_latency()
    elif args.test == 'reconnect':
        success = await tester.test_reconnection()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
