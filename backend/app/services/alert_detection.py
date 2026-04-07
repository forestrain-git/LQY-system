"""告警检测服务

实时阈值检测 + 趋势分析
"""

import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import (
    Alert, AlertType, AlertMetric, AlertLevel, AlertStatus,
    AlertRule, RuleMetric, SensorData, Device
)
from app.redis import get_redis
from app.services.mqtt_service import mqtt_service

logger = logging.getLogger(__name__)

# 默认阈值规则
DEFAULT_THRESHOLD_RULES = [
    {"metric": "temperature", "threshold": 80.0, "operator": "gt", "level": AlertLevel.CRITICAL, "message": "温度过高: {value}℃ > 80℃"},
    {"metric": "temperature", "threshold": 65.0, "operator": "gt", "level": AlertLevel.WARNING, "message": "温度偏高: {value}℃ > 65℃"},
    {"metric": "vibration", "threshold": 5.0, "operator": "gt", "level": AlertLevel.WARNING, "message": "振动异常: {value}mm/s > 5.0"},
    {"metric": "current", "threshold": 20.0, "operator": "gt", "level": AlertLevel.CRITICAL, "message": "电流过载: {value}A > 20A"},
]

# 重复抑制窗口（秒）
DUPLICATE_SUPPRESSION_WINDOW = 300  # 5分钟

# 趋势检测配置
TREND_CHECK_INTERVAL = 60  # 每60秒检查一次
TREND_DATA_WINDOW = 600    # 分析最近10分钟的数据


class AlertDetectionService:
    """告警检测服务"""

    def __init__(self):
        self.running = False
        self._trend_task: Optional[asyncio.Task] = None
        # 内存缓存：设备最近数据（用于趋势检测）
        self._device_data_cache: Dict[int, List[dict]] = defaultdict(list)
        self._cache_lock = asyncio.Lock()

    async def start(self):
        """启动检测服务"""
        self.running = True

        # 注册MQTT数据回调
        mqtt_service.data_callback = self._on_sensor_data
        logger.info("告警检测服务已启动，已注册MQTT回调")

        # 启动趋势检测定时任务
        self._trend_task = asyncio.create_task(self._trend_check_loop())
        logger.info("趋势检测任务已启动")

    async def stop(self):
        """停止检测服务"""
        self.running = False

        # 取消MQTT回调
        mqtt_service.data_callback = None

        # 停止趋势检测任务
        if self._trend_task:
            self._trend_task.cancel()
            try:
                await self._trend_task
            except asyncio.CancelledError:
                pass

        logger.info("告警检测服务已停止")

    async def _on_sensor_data(self, sensor_data: SensorData):
        """MQTT数据回调"""
        if not self.running:
            return

        try:
            # 缓存数据用于趋势检测
            await self._cache_sensor_data(sensor_data)

            # 实时阈值检测
            await self.check_thresholds(sensor_data)

        except Exception as e:
            logger.error(f"处理传感器数据失败: {e}")

    async def _cache_sensor_data(self, sensor_data: SensorData):
        """缓存传感器数据到内存（用于趋势检测）"""
        async with self._cache_lock:
            device_id = sensor_data.device_id

            data_point = {
                "timestamp": sensor_data.timestamp,
                "temperature": sensor_data.temperature,
                "vibration": sensor_data.vibration,
                "current": sensor_data.current,
            }

            self._device_data_cache[device_id].append(data_point)

            # 只保留最近10分钟的数据
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=TREND_DATA_WINDOW)
            self._device_data_cache[device_id] = [
                d for d in self._device_data_cache[device_id]
                if d["timestamp"] > cutoff_time
            ]

    async def check_thresholds(self, sensor_data: SensorData):
        """阈值检测"""
        device_id = sensor_data.device_id

        # 获取设备信息
        async with AsyncSessionLocal() as session:
            device = await session.get(Device, device_id)
            if not device:
                logger.warning(f"设备不存在: {device_id}")
                return

        # 检查默认规则
        for rule in DEFAULT_THRESHOLD_RULES:
            metric = rule["metric"]
            value = getattr(sensor_data, metric)

            if value is None:
                continue

            # 检查是否触发规则
            if rule["operator"] == "gt" and value > rule["threshold"]:
                # 检查重复抑制
                if await self._is_duplicate_alert(device_id, metric):
                    logger.info(f"Alert suppressed: {device_id} {metric} (recent alert exists)")
                    continue

                # 创建告警
                message = rule["message"].format(value=round(value, 2))
                await self._create_alert(
                    device_id=device_id,
                    alert_type=AlertType.THRESHOLD,
                    metric=AlertMetric(metric),
                    message=message,
                    level=rule["level"],
                    value=value
                )
                logger.info(f"Alert triggered: {device_id} {metric}={value}")

        # 检查动态规则（从数据库加载）
        await self._check_dynamic_rules(sensor_data, device_id)

    async def _check_dynamic_rules(self, sensor_data: SensorData, device_id: int):
        """检查动态规则"""
        async with AsyncSessionLocal() as session:
            # 加载适用的规则（设备特定或全局）
            result = await session.execute(
                select(AlertRule).where(
                    (AlertRule.device_id == device_id) | (AlertRule.device_id == None),
                    AlertRule.enabled == True
                )
            )
            rules = result.scalars().all()

            for rule in rules:
                metric = rule.metric.value
                value = getattr(sensor_data, metric, None)

                if value is None:
                    continue

                # 检查规则条件
                if rule.check_condition(value):
                    if await self._is_duplicate_alert(device_id, metric):
                        continue

                    message = f"{metric} {rule.operator.value} {rule.threshold}: {value}"
                    level = AlertLevel.WARNING if rule.duration > 0 else AlertLevel.CRITICAL

                    await self._create_alert(
                        device_id=device_id,
                        alert_type=AlertType.THRESHOLD,
                        metric=AlertMetric(metric),
                        message=message,
                        level=level,
                        value=value
                    )

    async def _is_duplicate_alert(self, device_id: int, metric: str) -> bool:
        """检查是否是重复告警（5分钟内）"""
        redis = get_redis()
        if not redis:
            # Redis不可用，不抑制
            return False

        try:
            key = f"alert:last:{device_id}:{metric}"
            last_alert = await redis.get(key)

            if last_alert:
                # 更新过期时间
                await redis.expire(key, DUPLICATE_SUPPRESSION_WINDOW)
                return True

            # 设置当前告警时间
            await redis.setex(key, DUPLICATE_SUPPRESSION_WINDOW, datetime.now(timezone.utc).isoformat())
            return False

        except Exception as e:
            logger.error(f"检查重复告警失败: {e}")
            return False

    async def _create_alert(
        self,
        device_id: int,
        alert_type: AlertType,
        metric: AlertMetric,
        message: str,
        level: AlertLevel,
        value: float
    ):
        """创建告警"""
        async with AsyncSessionLocal() as session:
            try:
                alert = Alert(
                    device_id=device_id,
                    alert_type=alert_type,
                    metric=metric,
                    message=message,
                    level=level,
                    status=AlertStatus.ACTIVE
                )
                session.add(alert)
                await session.commit()
                await session.refresh(alert)

                # 发布到Redis（供WebSocket使用）
                await self._publish_alert(alert, device_id)

                logger.info(f"告警已创建: {alert.id} - {message}")

            except Exception as e:
                await session.rollback()
                logger.error(f"创建告警失败: {e}")

    async def _publish_alert(self, alert: Alert, device_id: int):
        """发布告警到Redis"""
        try:
            redis = get_redis()
            if not redis:
                return

            # 获取设备名称
            async with AsyncSessionLocal() as session:
                device = await session.get(Device, device_id)
                device_name = device.name if device else f"设备{device_id}"

            message = {
                "type": "new_alert",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "id": alert.id,
                    "device_id": device_id,
                    "device_name": device_name,
                    "alert_type": alert.alert_type.value,
                    "metric": alert.metric.value,
                    "message": alert.message,
                    "level": alert.level.value,
                    "created_at": alert.created_at.isoformat()
                }
            }

            await redis.publish("alerts:new", json.dumps(message))

        except Exception as e:
            logger.error(f"发布告警到Redis失败: {e}")

    async def _trend_check_loop(self):
        """趋势检测循环"""
        while self.running:
            try:
                await asyncio.sleep(TREND_CHECK_INTERVAL)
                await self.check_trends()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"趋势检测异常: {e}")

    async def check_trends(self):
        """趋势检测"""
        async with self._cache_lock:
            for device_id, data_points in self._device_data_cache.items():
                if len(data_points) < 5:
                    continue

                # 按时间排序
                sorted_data = sorted(data_points, key=lambda x: x["timestamp"])

                # 检测连续上升
                await self._check_rising_trend(device_id, sorted_data)

                # 检测快速升温
                await self._check_rapid_rise(device_id, sorted_data)

    async def _check_rising_trend(self, device_id: int, data_points: List[dict]):
        """检测连续上升趋势"""
        # 取最近5个点
        recent = data_points[-5:]

        # 检查是否连续上升
        rising_count = 0
        total_rise = 0

        for i in range(1, len(recent)):
            prev_temp = recent[i-1].get("temperature")
            curr_temp = recent[i].get("temperature")

            if prev_temp is None or curr_temp is None:
                continue

            if curr_temp > prev_temp:
                rising_count += 1
                total_rise += (curr_temp - prev_temp)

        # 连续上升且总升温>10℃
        if rising_count >= 4 and total_rise > 10:
            if not await self._is_duplicate_alert(device_id, "temperature_rising"):
                message = f"温度连续上升趋势: 5个数据点上升{total_rise:.1f}℃"
                await self._create_alert(
                    device_id=device_id,
                    alert_type=AlertType.TREND,
                    metric=AlertMetric.TEMPERATURE,
                    message=message,
                    level=AlertLevel.WARNING,
                    value=recent[-1].get("temperature", 0)
                )
                logger.info(f"Trend alert triggered: {device_id} rising temperature")

    async def _check_rapid_rise(self, device_id: int, data_points: List[dict]):
        """检测快速升温"""
        if len(data_points) < 2:
            return

        # 查找10分钟内从<50℃升至>70℃的情况
        now = datetime.now(timezone.utc)
        ten_min_ago = now - timedelta(minutes=10)

        # 找10分钟前的数据点
        early_points = [d for d in data_points if d["timestamp"] <= ten_min_ago]
        recent_points = [d for d in data_points if d["timestamp"] > ten_min_ago]

        if not early_points or not recent_points:
            return

        # 早期温度<50℃，最近温度>70℃
        early_temp = early_points[-1].get("temperature")
        recent_temp = recent_points[-1].get("temperature")

        if early_temp and recent_temp and early_temp < 50 and recent_temp > 70:
            if not await self._is_duplicate_alert(device_id, "temperature_rapid_rise"):
                message = f"温度快速升高: 从{early_temp:.1f}℃升至{recent_temp:.1f}℃"
                await self._create_alert(
                    device_id=device_id,
                    alert_type=AlertType.TREND,
                    metric=AlertMetric.TEMPERATURE,
                    message=message,
                    level=AlertLevel.CRITICAL,
                    value=recent_temp
                )
                logger.info(f"Rapid rise alert triggered: {device_id} temperature")


# 全局告警检测服务实例
alert_detection_service = AlertDetectionService()
