#!/usr/bin/env python3
"""
故障诊断脚本 - 检查系统状态
"""

import asyncio
import socket
import subprocess
import sys


async def check_postgres():
    """检查PostgreSQL"""
    try:
        import asyncpg

        conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/lqy_db")
        await conn.fetch("SELECT 1")
        await conn.close()
        return True, "PostgreSQL连接正常"
    except Exception as e:
        return False, f"PostgreSQL连接失败: {e}"


async def check_redis():
    """检查Redis"""
    try:
        import redis.asyncio as redis

        r = redis.from_url("redis://localhost:6379")
        await r.ping()
        await r.close()
        return True, "Redis连接正常"
    except Exception as e:
        return False, f"Redis连接失败: {e}"


def check_port(port, name):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", port))
    sock.close()
    if result == 0:
        return True, f"端口{port}正在使用（{name}）"
    return False, f"端口{port}未使用（{name}）"


def check_docker():
    """检查Docker"""
    try:
        subprocess.run(["docker", "ps"], check=True, capture_output=True)
        return True, "Docker运行正常"
    except Exception:
        return False, "Docker未运行或无权访问"


async def async_checks():
    """运行异步检查"""
    results = []

    # 检查端口5432是否被占用（PostgreSQL）
    ok, msg = check_port(5432, "PostgreSQL")
    results.append(("端口5432", ok, msg))

    # 检查端口6379是否被占用（Redis）
    ok, msg = check_port(6379, "Redis")
    results.append(("端口6379", ok, msg))

    # 检查端口8000是否被占用（Backend）
    ok, msg = check_port(8000, "Backend")
    results.append(("端口8000", ok, msg))

    # 如果端口被占用，检查服务连接
    if any(ok for _, ok, _ in results):
        pg_ok, pg_msg = await check_postgres()
        results.append(("PostgreSQL", pg_ok, pg_msg))

        redis_ok, redis_msg = await check_redis()
        results.append(("Redis", redis_ok, redis_msg))

    return results


def main():
    print("=" * 50)
    print("龙泉驿环卫智能体 - 故障诊断")
    print("=" * 50)

    # Docker检查
    docker_ok, docker_msg = check_docker()
    print(f"\n[Docker]")
    print(f"  {'OK' if docker_ok else 'FAIL'}: {docker_msg}")

    # 异步检查
    print("\n[服务检查]")
    results = asyncio.run(async_checks())

    for name, ok, msg in results:
        status = "OK" if ok else "FAIL"
        print(f"  {status}: {msg}")

    # 总结
    all_ok = docker_ok and all(ok for _, ok, _ in results)

    print("\n" + "=" * 50)
    if all_ok:
        print("结果: 所有检查通过")
        print("访问 http://localhost:8000/docs 查看API文档")
        return 0
    else:
        print("结果: 发现异常")
        print("\n修复建议:")
        print("  1. 如果Docker未运行，请先启动Docker Desktop")
        print("  2. 运行 'make up' 启动服务")
        print("  3. 运行 'make logs' 查看详细日志")
        return 1


if __name__ == "__main__":
    sys.exit(main())
