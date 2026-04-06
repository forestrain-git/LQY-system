# Day 1 - Prompt 4: Docker完善与工具脚本

**时机**：API和测试通过后执行
**预期耗时**：Claude生成10分钟，你测试10分钟
**人工决策**：确认一键启动OK

---

## 输入Prompt

```text
请完善Docker配置和工具脚本。

【Dockerfile】（backend/Dockerfile）
- 基础镜像：python:3.11-slim
- 工作目录：/app
- 安装系统依赖：gcc libpq-dev（为了编译psycopg2/asyncpg）
- 复制requirements.txt先安装（利用缓存层）
- 复制代码
- 创建非root用户appuser运行
- 健康检查：HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
- 启动命令：uvicorn app.main:app --host 0.0.0.0 --port 8000

【docker-compose.yml更新】

添加启动顺序控制：
1. postgres
   - 健康检查：pg_isready -U postgres
   - 卷：postgres_data

2. redis
   - 健康检查：redis-cli ping

3. backend
   - build: .
   - depends_on:
       postgres: condition: service_healthy
       redis: condition: service_healthy
   - 环境变量：
     - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/lqy_db
     - REDIS_URL=redis://redis:6379/0
     - LOG_LEVEL=info
     - PYTHONUNBUFFERED=1
   - 端口：8000:8000
   - 卷：./app:/app/app（开发模式，代码变更自动reload）
   - 重启策略：unless-stopped

【启动脚本】（backend/start.sh）

#!/bin/bash
set -e

echo "等待数据库就绪..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U postgres -c '\q' 2>/dev/null; do
  echo "PostgreSQL未就绪，等待1秒..."
  sleep 1
done
echo "数据库已就绪"

echo "运行Alembic迁移..."
alembic upgrade head

echo "启动应用..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

要求：
- 添加执行权限（chmod +x）
- Dockerfile中CMD调用此脚本

【Makefile】（backend/Makefile）

.PHONY: up down logs test shell migrate lint

up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f backend

test:
	docker-compose exec backend pytest -v --cov=app

shell:
	docker-compose exec backend bash

migrate:
	docker-compose exec backend alembic upgrade head

lint:
	docker-compose exec backend ruff check .

db-shell:
	docker-compose exec postgres psql -U postgres -d lqy_db

【故障诊断脚本】（backend/diagnose.py）

#!/usr/bin/env python3
"""
故障诊断脚本 - 检查系统状态
"""

import asyncio
import sys
import subprocess
import socket

async def check_postgres():
    """检查PostgreSQL"""
    try:
        import asyncpg
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/lqy_db')
        await conn.fetch('SELECT 1')
        await conn.close()
        return True, "PostgreSQL连接正常"
    except Exception as e:
        return False, f"PostgreSQL连接失败: {e}"

async def check_redis():
    """检查Redis"""
    try:
        import redis.asyncio as redis
        r = redis.from_url('redis://localhost:6379')
        await r.ping()
        await r.close()
        return True, "Redis连接正常"
    except Exception as e:
        return False, f"Redis连接失败: {e}"

def check_port(port, name):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    if result == 0:
        return False, f"端口{port}被占用（{name}）"
    return True, f"端口{port}空闲（{name}）"

def check_docker():
    """检查Docker"""
    try:
        subprocess.run(['docker', 'ps'], check=True, capture_output=True)
        return True, "Docker运行正常"
    except:
        return False, "Docker未运行或无权访问"

def main():
    print("=" * 50)
    print("龙泉驿环卫智能体 - 故障诊断")
    print("=" * 50)

    checks = [
        ("Docker", check_docker()),
        ("端口5432", check_port(5432, "PostgreSQL")),
        ("端口6379", check_port(6379, "Redis")),
        ("端口8000", check_port(8000, "Backend")),
    ]

    asyncio.run(async_checks())

    all_ok = all(ok for _, (ok, _) in checks)

    print("\n诊断结果:")
    for name, (ok, msg) in checks:
        status = "✓" if ok else "✗"
        print(f"  {status} {name}: {msg}")

    if all_ok:
        print("\n✓ 所有检查通过，系统正常")
        return 0
    else:
        print("\n✗ 发现异常，请根据提示修复")
        return 1

if __name__ == '__main__':
    sys.exit(main())

【README】（backend/README.md）

# 龙泉驿环卫智能体 - 后端API

## 快速开始（3步启动）

```bash
cd backend
make up          # 启动所有服务
make migrate     # 运行数据库迁移（首次）
# 访问 http://localhost:8000/docs
```

## 常用命令

- `make up` - 启动服务
- `make down` - 停止服务
- `make logs` - 查看日志
- `make test` - 运行测试
- `make shell` - 进入后端容器
- `python diagnose.py` - 故障诊断

## API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 环境变量

- DATABASE_URL - PostgreSQL连接字符串
- REDIS_URL - Redis连接字符串
- LOG_LEVEL - 日志级别（debug/info/warning/error）

## 常见错误

### 端口被占用
```bash
# 检查占用
lsof -i :5432
# 杀掉进程或修改docker-compose.yml端口映射
```

### 数据库连接失败
```bash
# 检查PostgreSQL日志
make logs
# 运行诊断
python diagnose.py
```

## 测试

```bash
make test
# 或
pytest -v --cov=app --cov-report=html
```

【验证步骤】

生成后执行：
1. cd backend
2. make up（一键启动）
3. 等待30秒
4. python diagnose.py（诊断）
5. make test（运行测试）
6. curl http://localhost:8000/health（健康检查）

如果全部通过，Day 1完成。
如果失败，根据错误修复。
