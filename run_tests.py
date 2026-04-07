#!/usr/bin/env python3
"""
Day6 集成测试运行器
一键运行所有系统测试
"""

import argparse
import asyncio
import subprocess
import sys
import time
from pathlib import Path


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.test_dir = Path(__file__).parent / "backend" / "tests"
        self.results = []

    def print_header(self, text):
        """打印标题"""
        print("\n" + "=" * 70)
        print(f" {text}")
        print("=" * 70)

    def run_command(self, cmd, description, timeout=60):
        """运行命令"""
        print(f"\n▶ {description}")
        print(f"  命令: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(Path(__file__).parent)
            )

            if result.returncode == 0:
                print(f"  ✓ 成功")
                if result.stdout:
                    print(result.stdout[-500:])  # 只显示最后500字符
                return True
            else:
                print(f"  ✗ 失败 (返回码: {result.returncode})")
                print(result.stderr[-500:])
                return False

        except subprocess.TimeoutExpired:
            print(f"  ✗ 超时 ({timeout}秒)")
            return False
        except Exception as e:
            print(f"  ✗ 异常: {e}")
            return False

    def check_services(self):
        """检查服务状态"""
        self.print_header("1. 服务健康检查")

        services = [
            ("http://localhost:8000/health", "后端API"),
            ("http://localhost:5173", "前端"),
        ]

        all_ok = True
        for url, name in services:
            cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                status = result.stdout.strip()
                if status in ["200", "301", "302"]:
                    print(f"  ✓ {name}: OK (HTTP {status})")
                else:
                    print(f"  ✗ {name}: 异常 (HTTP {status})")
                    all_ok = False
            except Exception as e:
                print(f"  ✗ {name}: 无法连接 ({e})")
                all_ok = False

        return all_ok

    def run_e2e_tests(self):
        """运行E2E测试"""
        self.print_header("2. 端到端功能测试")

        tests = [
            (["python3", "tests/e2e/test_websocket.py", "--test", "connection"],
             "WebSocket连接测试", 10),
            (["python3", "tests/e2e/test_websocket.py", "--test", "realtime"],
             "WebSocket实时数据测试", 15),
            (["python3", "tests/e2e/test_alert_flow.py"],
             "告警流程测试", 30),
        ]

        results = []
        for cmd, desc, timeout in tests:
            success = self.run_command(cmd, desc, timeout)
            results.append((desc, success))

        return all(r[1] for r in results)

    def run_performance_tests(self):
        """运行性能测试"""
        self.print_header("3. 性能测试")

        cmd = [
            "python3", "tests/performance/load_test.py",
            "--devices", "10",
            "--duration", "30",
            "--interval", "2"
        ]

        return self.run_command(cmd, "负载测试 (10设备, 30秒)", 60)

    def run_simulation(self):
        """运行设备模拟"""
        self.print_header("4. 设备模拟验证")

        cmd = [
            "python3", "tests/e2e/device_simulator.py",
            "--count", "5",
            "--duration", "10",
            "--interval", "2"
        ]

        return self.run_command(cmd, "设备数据模拟 (5设备, 10秒)", 20)

    def generate_report(self):
        """生成测试报告"""
        self.print_header("5. 生成测试报告")

        report = f"""
# Day6 集成测试报告

生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 测试摘要

- 后端API: {'✓ 正常' if any('后端' in str(r) and r[1] for r in self.results) else '✗ 异常'}
- 前端服务: {'✓ 正常' if any('前端' in str(r) and r[1] for r in self.results) else '✗ 异常'}
- E2E测试: {'✓ 通过' if all(r[1] for r in self.results if 'E2E' in str(r)) else '✗ 失败'}
- 性能测试: {'✓ 通过' if any('性能' in str(r) and r[1] for r in self.results) else '✗ 失败'}

## 详细结果

"""
        for name, result in self.results:
            status = "✓ PASS" if result else "✗ FAIL"
            report += f"- {name}: {status}\n"

        report_path = Path(__file__).parent / "docs" / "day6_test_report.md"
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report, encoding='utf-8')

        print(f"  ✓ 报告已生成: {report_path}")
        return True

    async def run_all_tests(self):
        """运行所有测试"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                    Day6 系统集成测试                             ║
╚══════════════════════════════════════════════════════════════════╝
""")

        start_time = time.time()

        # 1. 服务检查
        services_ok = self.check_services()
        self.results.append(("服务健康检查", services_ok))

        if not services_ok:
            print("\n⚠ 警告: 部分服务未启动，尝试继续测试...")

        # 2. E2E测试
        e2e_ok = self.run_e2e_tests()
        self.results.append(("E2E测试", e2e_ok))

        # 3. 性能测试
        perf_ok = self.run_performance_tests()
        self.results.append(("性能测试", perf_ok))

        # 4. 模拟测试
        sim_ok = self.run_simulation()
        self.results.append(("设备模拟", sim_ok))

        # 5. 生成报告
        report_ok = self.generate_report()
        self.results.append(("报告生成", report_ok))

        # 总结
        duration = time.time() - start_time
        self.print_summary(duration)

    def print_summary(self, duration):
        """打印总结"""
        self.print_header("测试完成总结")

        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)

        for name, result in self.results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {name:30s} {status}")

        print(f"\n总计: {passed}/{total} 通过")
        print(f"耗时: {duration:.1f} 秒")

        if passed == total:
            print("\n🎉 所有测试通过！系统已准备好部署。")
        else:
            print(f"\n⚠ {total - passed} 个测试失败，请检查日志。")

        print("\n测试报告: docs/day6_test_report.md")
        print("=" * 70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Day6 集成测试')
    parser.add_argument('--skip-health', action='store_true',
                        help='跳过健康检查')
    parser.add_argument('--only', type=str,
                        choices=['health', 'e2e', 'perf', 'sim', 'all'],
                        default='all',
                        help='只运行特定测试')

    args = parser.parse_args()

    runner = TestRunner()
    asyncio.run(runner.run_all_tests())


if __name__ == "__main__":
    main()
