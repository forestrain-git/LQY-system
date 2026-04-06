"""Redis连接管理

提供Redis异步连接池
"""

import logging

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)

# Redis连接池
redis_pool: redis.Redis | None = None


async def init_redis() -> redis.Redis | None:
    """初始化Redis连接"""
    global redis_pool
    try:
        redis_pool = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        # 测试连接
        await redis_pool.ping()
        logger.info("Redis连接成功")
        return redis_pool
    except Exception as e:
        logger.warning(f"Redis连接失败: {e}")
        redis_pool = None
        return None


async def close_redis() -> None:
    """关闭Redis连接"""
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        redis_pool = None
        logger.info("Redis连接已关闭")


def get_redis() -> redis.Redis | None:
    """获取Redis实例"""
    return redis_pool
