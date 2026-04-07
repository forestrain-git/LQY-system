"""WebSocket服务

提供实时数据推送功能
"""

import asyncio
import json
import logging
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.redis import get_redis

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 所有设备连接
        self.all_devices_connections: Set[WebSocket] = set()
        # 特定设备连接
        self.device_connections: Dict[int, Set[WebSocket]] = {}
        # Redis订阅任务
        self._redis_task: asyncio.Task | None = None
        self._redis: Redis | None = None

    async def connect_all(self, websocket: WebSocket):
        """连接所有设备数据流"""
        await websocket.accept()
        self.all_devices_connections.add(websocket)
        logger.info(f"WebSocket连接: 所有设备，当前连接数: {len(self.all_devices_connections)}")

    async def connect_device(self, websocket: WebSocket, device_id: int):
        """连接特定设备数据流"""
        await websocket.accept()
        if device_id not in self.device_connections:
            self.device_connections[device_id] = set()
        self.device_connections[device_id].add(websocket)
        logger.info(f"WebSocket连接: 设备{device_id}，当前连接数: {len(self.device_connections[device_id])}")

    async def disconnect(self, websocket: WebSocket, device_id: int | None = None):
        """断开连接"""
        if device_id is None:
            self.all_devices_connections.discard(websocket)
            logger.info(f"WebSocket断开: 所有设备，当前连接数: {len(self.all_devices_connections)}")
        else:
            if device_id in self.device_connections:
                self.device_connections[device_id].discard(websocket)
                logger.info(f"WebSocket断开: 设备{device_id}，当前连接数: {len(self.device_connections.get(device_id, set()))}")

    async def broadcast_all(self, message: dict):
        """广播给所有设备连接"""
        disconnected = set()
        for connection in self.all_devices_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # 清理断开连接
        for conn in disconnected:
            self.all_devices_connections.discard(conn)

    async def broadcast_device(self, device_id: int, message: dict):
        """广播给特定设备连接"""
        if device_id not in self.device_connections:
            return

        disconnected = set()
        for connection in self.device_connections[device_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # 清理断开连接
        for conn in disconnected:
            self.device_connections[device_id].discard(conn)

    async def start_redis_listener(self):
        """启动Redis订阅监听器"""
        self._redis_task = asyncio.create_task(self._redis_listener())

    async def stop_redis_listener(self):
        """停止Redis订阅监听器"""
        if self._redis_task:
            self._redis_task.cancel()
            try:
                await self._redis_task
            except asyncio.CancelledError:
                pass

    async def _redis_listener(self):
        """监听Redis发布"""
        try:
            redis = get_redis()
            if not redis:
                logger.warning("Redis未连接，WebSocket无法接收数据")
                return

            self._redis = redis

            # 创建发布/订阅客户端
            pubsub = redis.pubsub()
            await pubsub.psubscribe("device:*:data")
            await pubsub.subscribe("alerts:new")
            logger.info("WebSocket已订阅Redis频道: device:*:data, alerts:new")

            async for message in pubsub.listen():
                if message["type"] in ["pmessage", "message"]:
                    try:
                        channel = message["channel"]
                        data = json.loads(message["data"])

                        # 处理告警通知
                        if channel == "alerts:new":
                            ws_message = {
                                "type": "new_alert",
                                "timestamp": data.get("timestamp"),
                                "data": data.get("data", {})
                            }
                            # 广播给所有连接
                            await self.broadcast_all(ws_message)
                            continue

                        # 处理传感器数据
                        device_id = data.get("device_id")

                        # 构建WebSocket消息
                        ws_message = {
                            "type": "sensor_data",
                            "data": data,
                        }

                        # 广播给所有连接
                        await self.broadcast_all(ws_message)

                        # 广播给特定设备连接
                        if device_id:
                            await self.broadcast_device(device_id, ws_message)

                    except json.JSONDecodeError:
                        logger.error(f"Redis消息JSON解析失败: {message['data']}")
                    except Exception as e:
                        logger.error(f"处理Redis消息失败: {e}")

        except Exception as e:
            logger.error(f"Redis监听器异常: {e}")


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/devices")
async def websocket_all_devices(websocket: WebSocket):
    """WebSocket: 所有设备数据流"""
    await manager.connect_all(websocket)
    try:
        while True:
            # 接收心跳
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


@router.websocket("/ws/devices/{device_id}")
async def websocket_single_device(websocket: WebSocket, device_id: int):
    """WebSocket: 单个设备数据流"""
    await manager.connect_device(websocket, device_id)
    try:
        while True:
            # 接收心跳
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket, device_id)
