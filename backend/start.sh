#!/bin/bash
set -e

echo "================================"
echo "龙泉驿环卫智能体 - 启动脚本"
echo "================================"

echo "等待数据库就绪..."
until PGPASSWORD=postgres psql -h postgres -U postgres -c '\q' 2>/dev/null; do
  echo "PostgreSQL未就绪，等待1秒..."
  sleep 1
done
echo "数据库已就绪"

echo "等待Redis就绪..."
until redis-cli -h redis ping 2>/dev/null | grep -q PONG; do
  echo "Redis未就绪，等待1秒..."
  sleep 1
done
echo "Redis已就绪"

echo "运行Alembic迁移..."
alembic upgrade head || echo "迁移失败，继续启动..."

echo "启动应用..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
