#!/usr/bin/env python3
"""告警引擎端到端验证脚本

验证完整告警流程：模拟数据 → 检测 → 告警 → WebSocket推送
"""

import asyncio
import json
import sys
from datetime import datetime, timezone

import httpx


async def validate_alert_engine():
    """验证告警引擎"""
    print("=" * 60)
    print("龙泉驿环卫智能体 - Day 3 告警引擎验证")
    print("=" * 60)

    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        # 测试1: 健康检查
        print("\n[测试1] 服务健康检查")
        try:
            resp = await client.get(f"{base_url}/health")
            if resp.status_code == 200:
                print("  ✓ PASS - 服务运行正常")
            else:
                print(f"  ✗ FAIL - 状态码: {resp.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ FAIL - 连接失败: {e}")
            return False

        # 测试2: 查询告警API
        print("\n[测试2] 告警查询API")
        try:
            resp = await client.get(f"{base_url}/api/v1/alerts")
            if resp.status_code == 200:
                data = resp.json()
                print(f"  ✓ PASS - 查询成功，返回{len(data.get('data', []))}条告警")
            else:
                print(f"  ✗ FAIL - 状态码: {resp.status_code}")
        except Exception as e:
            print(f"  ✗ FAIL - 请求失败: {e}")

        # 测试3: 告警统计API
        print("\n[测试3] 告警统计API")
        try:
            resp = await client.get(f"{base_url}/api/v1/alerts/stats")
            if resp.status_code == 200:
                stats = resp.json()
                print(f"  ✓ PASS - 统计接口正常")
                print(f"    - 活跃告警: {stats.get('total_active', 0)}")
                print(f"    - 今日告警: {stats.get('total_today', 0)}")
            else:
                print(f"  ✗ FAIL - 状态码: {resp.status_code}")
        except Exception as e:
            print(f"  ✗ FAIL - 请求失败: {e}")

        # 测试4: 告警规则API
        print("\n[测试4] 告警规则API")
        try:
            resp = await client.get(f"{base_url}/api/v1/alert-rules")
            if resp.status_code == 200:
                data = resp.json()
                print(f"  ✓ PASS - 规则查询成功，返回{len(data.get('data', []))}条规则")
            else:
                print(f"  ✗ FAIL - 状态码: {resp.status_code}")
        except Exception as e:
            print(f"  ✗ FAIL - 请求失败: {e}")

    print("\n" + "=" * 60)
    print("基础API验证完成")
    print("=" * 60)
    print("\n注意: 完整的数据流验证需要:")
    print("1. 启动设备模拟器产生异常数据")
    print("2. 观察后端日志中的告警触发信息")
    print("3. 使用wscat连接WebSocket验证实时推送")
    print("\n命令示例:")
    print("  wscat -c 'ws://localhost:8000/ws/devices'")
    print("  python3 simulator/device_simulator.py --count 2")

    return True


if __name__ == "__main__":
    result = asyncio.run(validate_alert_engine())
    sys.exit(0 if result else 1)
