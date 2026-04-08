"""FastAPI 应用入口

包含 lifespan 管理、健康检查端点
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1 import (
    alert_rules_router,
    alerts_router,
    devices_router,
    predictions_router,
    sensor_data_router,
)
from app.modules.dispatch.api import router as dispatch_router
from app.modules.workflow.api import router as workflow_router
from app.modules.equipment.api import router as equipment_router
from app.modules.safety.api import router as safety_router
from app.modules.ai.api import router as ai_router
from app.modules.auth.api import router as auth_router
from app.api.websocket import manager, router as websocket_router
from app.config import settings
from app.database import close_db
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.redis import close_redis, init_redis
from app.services import alert_detection_service, mqtt_service

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理

    启动时:
        1. 初始化数据库连接
        2. 初始化Redis连接
        3. 启动MQTT服务
        4. 启动WebSocket Redis监听器

    关闭时:
        1. 停止MQTT服务
        2. 停止WebSocket监听器
        3. 关闭Redis连接
        4. 关闭数据库连接
    """
    # 启动
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")

    # 初始化数据库
    try:
        logger.info("数据库连接已就绪")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

    # 初始化Redis（失败不影响启动）
    await init_redis()

    # 启动MQTT服务
    try:
        await mqtt_service.start()
    except Exception as e:
        logger.warning(f"MQTT服务启动失败: {e}")

    # 启动WebSocket Redis监听器
    try:
        await manager.start_redis_listener()
    except Exception as e:
        logger.warning(f"WebSocket监听器启动失败: {e}")

    # 启动告警检测服务
    try:
        await alert_detection_service.start()
    except Exception as e:
        logger.warning(f"告警检测服务启动失败: {e}")

    yield

    # 关闭
    logger.info("正在关闭应用...")

    # 停止MQTT服务
    try:
        await mqtt_service.stop()
    except Exception as e:
        logger.error(f"停止MQTT服务失败: {e}")

    # 停止告警检测服务
    try:
        await alert_detection_service.stop()
    except Exception as e:
        logger.error(f"停止告警检测服务失败: {e}")

    # 停止WebSocket监听器
    try:
        await manager.stop_redis_listener()
    except Exception as e:
        logger.error(f"停止WebSocket监听器失败: {e}")

    await close_redis()
    await close_db()
    logger.info("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="龙泉驿区环境卫生智能管理系统 API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 注册中间件
app.add_middleware(LoggingMiddleware)

# 注册异常处理器
register_exception_handlers(app)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")  # 认证路由 / Auth routes
app.include_router(devices_router, prefix="/api/v1")
app.include_router(sensor_data_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(alert_rules_router, prefix="/api/v1")
app.include_router(predictions_router, prefix="/api/v1")
app.include_router(dispatch_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")
app.include_router(equipment_router, prefix="/api/v1")
app.include_router(safety_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(websocket_router)


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """健康检查端点

    Returns:
        dict: 包含状态和应用版本信息
    """
    return {
        "status": "ok",
        "version": settings.app_version,
    }


@app.get("/")
async def root():
    """根路径重定向到文档"""
    return {
        "message": "龙泉驿环卫智能体 API",
        "docs": "/docs",
        "health": "/health",
    }
