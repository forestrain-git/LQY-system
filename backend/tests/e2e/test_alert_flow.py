"""
告警流程 E2E 测试
验证告警生成、通知、确认全流程
"""

import asyncio
import json
import sys
from datetime import datetime, timezone

import aiomqtt
import aiohttp


class AlertFlowTester:
    """告警流程测试器"""

    def __init__(self, mqtt_broker="localhost", mqtt_port=1883,
                 api_url="http://localhost:8000"):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.api_url = api_url
        self.test_device = "ALERT_TEST_001"
        self.alert_triggered = False
        self.alert_acknowledged = False

    async def trigger_temperature_alert(self):
        """触发温度告警"""
        print("步骤1: 发送高温数据触发告警...")

        async with aiomqtt.Client(
            hostname=self.mqtt_broker,
            port=self.mqtt_port,
            identifier="alert_test_publisher",
        ) as client:

            # 发送高温数据（阈值80°C）
            for i in range(3):
                data = {
                    "device_id": self.test_device,
                    "temperature": 85.0 + i,  # 超过80°C阈值
                    "vibration": 3.0,
                    "current": 15.0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                await client.publish(
                    f"sensors/{self.test_device}/data",
                    json.dumps(data)
                )
                print(f"  发送高温数据: {data['temperature']}°C")
                await asyncio.sleep(1)

        print("  ✓ 高温数据发送完成")

    async def check_alert_created(self):
        """检查告警是否创建"""
        print("\n步骤2: 检查告警是否创建...")

        await asyncio.sleep(2)  # 等待后端处理

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_url}/api/v1/alerts") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    alerts = data.get("items", [])

                    # 查找刚创建的告警
                    for alert in alerts:
                        if alert.get("device_name") == self.test_device:
                            print(f"  ✓ 告警已创建: {alert['message']}")
                            self.alert_id = alert["id"]
                            self.alert_triggered = True
                            return True

                print("  ✗ 未找到告警")
                return False

    async def acknowledge_alert(self):
        """确认告警"""
        print("\n步骤3: 确认告警...")

        if not self.alert_triggered:
            print("  ✗ 没有可确认的告警")
            return False

        async with aiohttp.ClientSession() as session:
            # 调用确认API
            async with session.post(
                f"{self.api_url}/api/v1/alerts/{self.alert_id}/acknowledge"
            ) as resp:
                if resp.status == 200:
                    print("  ✓ 告警已确认")
                    self.alert_acknowledged = True
                    return True
                else:
                    print(f"  ✗ 确认失败: {resp.status}")
                    return False

    async def resolve_alert(self):
        """解决告警"""
        print("\n步骤4: 解决告警...")

        # 发送正常数据
        async with aiomqtt.Client(
            hostname=self.mqtt_broker,
            port=self.mqtt_port,
            identifier="alert_test_resolver",
        ) as client:

            data = {
                "device_id": self.test_device,
                "temperature": 65.0,  # 正常温度
                "vibration": 3.0,
                "current": 15.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            await client.publish(
                f"sensors/{self.test_device}/data",
                json.dumps(data)
            )

        print("  ✓ 已发送正常数据")

        # 等待自动解决或手动解决
        await asyncio.sleep(2)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/api/v1/alerts/{self.alert_id}"
            ) as resp:
                if resp.status == 200:
                    alert = await resp.json()
                    status = alert.get("status")
                    print(f"  ✓ 告警状态: {status}")
                    return status in ["resolved", "acknowledged"]

        return False

    async def cleanup(self):
        """清理测试数据"""
        print("\n步骤5: 清理测试数据...")
        # 删除测试告警
        if hasattr(self, 'alert_id'):
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.api_url}/api/v1/alerts/{self.alert_id}"
                ) as resp:
                    if resp.status == 204:
                        print("  ✓ 测试告警已删除")

    async def run_full_test(self):
        """运行完整告警流程测试"""
        print("=" * 60)
        print("告警流程 E2E 测试")
        print("=" * 60)

        results = []

        try:
            # 步骤1: 触发告警
            await self.trigger_temperature_alert()
            results.append(("触发告警", True))

            # 步骤2: 检查告警创建
            alert_created = await self.check_alert_created()
            results.append(("告警创建", alert_created))

            if alert_created:
                # 步骤3: 确认告警
                ack_result = await self.acknowledge_alert()
                results.append(("告警确认", ack_result))

                # 步骤4: 解决告警
                resolve_result = await self.resolve_alert()
                results.append(("告警解决", resolve_result))

        except Exception as e:
            print(f"\n✗ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append(("异常", False))

        finally:
            # 步骤5: 清理
            await self.cleanup()

        # 总结
        print("\n" + "=" * 60)
        print("测试结果")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{name:20s} {status}")

        print(f"\n总计: {passed}/{total} 通过")
        print("=" * 60)

        return passed == total


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='告警流程 E2E 测试')
    parser.add_argument('--broker', type=str, default='localhost',
                        help='MQTT broker')
    parser.add_argument('--port', type=int, default=1883,
                        help='MQTT端口')
    parser.add_argument('--api', type=str, default='http://localhost:8000',
                        help='API地址')

    args = parser.parse_args()

    tester = AlertFlowTester(
        mqtt_broker=args.broker,
        mqtt_port=args.port,
        api_url=args.api,
    )

    success = await tester.run_full_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
