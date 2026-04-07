"""MQTT服务

接收设备传感器数据，写入数据库，并发布到Redis
"""

import asyncio
import json
import logging
from datetime import datetime, timezone

import aiomqtt
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Device, DeviceStatus, SensorData
from app.redis import get_redis

logger = logging.getLogger(__name__)

# MQTT配置
MQTT_BROKER = "emqx"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/+/data"


class MQTTService:
    """MQTT客户端服务"""

    def __init__(self):
        self.client: aiomqtt.Client | None = None
        self.running = False
        self._task: asyncio.Task | None = None
        self.data_callback = None  # 数据回调函数

    async def start(self):
        """启动MQTT服务"""
        self.running = True
        self._task = asyncio.create_task(self._run())
        logger.info("MQTT服务已启动")

    async def stop(self):
        """停止MQTT服务"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self.client:
            await self.client.disconnect()
        logger.info("MQTT服务已停止")

    async def _run(self):
        """运行MQTT客户端（带重连）"""
        while self.running:
            try:
                async with aiomqtt.Client(
                    hostname=MQTT_BROKER,
                    port=MQTT_PORT,
                    identifier="backend_service",
                ) as client:
                    self.client = client
                    logger.info(f"已连接到MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")

                    await client.subscribe(MQTT_TOPIC)
                    logger.info(f"已订阅主题: {MQTT_TOPIC}")

                    async for message in client.messages:
                        if not self.running:
                            break
                        await self._handle_message(message)

            except aiomqtt.MqttError as e:
                logger.error(f"MQTT连接错误: {e}, 5秒后重连...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"MQTT服务异常: {e}")
                await asyncio.sleep(5)

    async def _handle_message(self, message):
        """处理MQTT消息"""
        try:
            topic = message.topic.value
            payload = message.payload.decode()

            # 解析主题提取设备ID: sensors/DEV001/data
            parts = topic.split("/")
            if len(parts) != 3:
                logger.warning(f"无效的主题格式: {topic}")
                return

            device_name = parts[1]

            # 解析JSON数据
            data = json.loads(payload)

            # 保存到数据库
            sensor_data = await self._save_sensor_data(device_name, data)

            if sensor_data:
                # 发布到Redis供WebSocket使用
                await self._publish_to_redis(sensor_data)
                logger.debug(f"已处理设备 {device_name} 的数据")

                # 调用数据回调（告警检测）
                if self.data_callback:
                    try:
                        await self.data_callback(sensor_data)
                    except Exception as e:
                        logger.error(f"数据回调失败: {e}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}, payload: {payload}")
        except Exception as e:
            logger.error(f"处理MQTT消息失败: {e}")

    async def _save_sensor_data(
        self, device_name: str, data: dict
    ) -> SensorData | None:
        """保存传感器数据到数据库"""
        async with AsyncSessionLocal() as session:
            try:
                # 查找设备
                result = await session.execute(
                    select(Device).where(
                        Device.name == device_name,
                        Device.status != DeviceStatus.DISABLED,
                    )
                )
                device = result.scalar_one_or_none()

                if not device:
                    # 自动创建设备
                    device = Device(
                        name=device_name,
                        type="compressor",
                        status=DeviceStatus.ONLINE,
                    )
                    session.add(device)
                    await session.flush()
                    logger.info(f"自动创建设备: {device_name}")

                # 解析时间戳
                timestamp_str = data.get("timestamp")
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                else:
                    timestamp = datetime.now(timezone.utc)

                # 创建传感器数据
                sensor_data = SensorData(
                    device_id=device.id,
                    temperature=data.get("temperature"),
                    vibration=data.get("vibration"),
                    current=data.get("current"),
                    timestamp=timestamp,
                )

                session.add(sensor_data)
                await session.commit()
                await session.refresh(sensor_data)

                return sensor_data

            except Exception as e:
                await session.rollback()
                logger.error(f"保存传感器数据失败: {e}")
                return None

    async def _publish_to_redis(self, sensor_data: SensorData):
        """发布数据到Redis"""
        try:
            redis = get_redis()
            if redis:
                message = {
                    "device_id": sensor_data.device_id,
                    "temperature": sensor_data.temperature,
                    "vibration": sensor_data.vibration,
                    "current": sensor_data.current,
                    "timestamp": sensor_data.timestamp.isoformat(),
                }
                channel = f"device:{sensor_data.device_id}:data"
                await redis.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"发布到Redis失败: {e}")


# 全局MQTT服务实例
mqtt_service = MQTTService()
