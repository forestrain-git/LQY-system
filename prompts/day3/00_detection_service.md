# Day 3 - Prompt 0: 告警检测服务

**时机**：Day 3开始，确认Day 2数据流正常后执行
**预期耗时**：Claude生成20分钟，你Review 10分钟
**人工决策**：确认检测规则设计，验收检测准确性

---

## 输入Prompt

```text
请实现完整的告警检测引擎，包含实时阈值检测和趋势检测。

【告警检测服务】（app/services/alert_detection.py）

核心类 AlertDetectionService：

1. 阈值检测（实时）
   - 监听MQTT数据流（复用mqtt_service的回调机制）
   - 对每个传感器数据进行规则匹配
   - 默认规则：
     * 温度 > 80℃：Critical告警 "温度过高: {value}℃ > 80℃"
     * 温度 > 65℃：Warning告警 "温度偏高: {value}℃ > 65℃"
     * 振动 > 5.0mm/s：Warning告警 "振动异常: {value}mm/s > 5.0"
     * 电流 > 20A：Critical告警 "电流过载: {value}A > 20A"
   - 支持从AlertRule表动态加载规则

2. 趋势检测（异步任务，每分钟）
   - 扫描最近10分钟的数据
   - 检测连续上升趋势（连续5个点，总上升>10℃）
   - 检测快速升温（10分钟内从<50℃升至>70℃）
   - 生成Trend类型告警

3. 重复抑制
   - 同一设备同一指标，5分钟内不重复生成告警
   - 使用Redis缓存最近告警时间

4. 告警创建
   - 检测到异常时，写入Alert表
   - 同时发布到Redis频道 "alerts:new"

关键方法：
- async def start()：启动检测服务，订阅MQTT
- async def stop()：停止检测
- async def check_thresholds(sensor_data: SensorData)：阈值检查
- async def check_trends()：趋势检查（每分钟）
- def _is_duplicate_alert(device_id, metric)：重复检查

【状态管理】
- 使用内存队列缓存最近10条数据（用于趋势检测）
- 使用Redis记录最近告警时间（key: alert:last:{device_id}:{metric}）

【启动集成】
在main.py的lifespan中：
- 启动时初始化AlertDetectionService
- 传入mqtt_service实例，注册数据回调
- 启动趋势检测定时任务

【日志】
- 检测到异常："Alert triggered: {device_id} {metric}={value}"
- 重复抑制："Alert suppressed: {device_id} {metric} (recent alert exists)"
```

---

## 预期输出

```
生成文件：
- app/services/alert_detection.py [完成]
- app/services/__init__.py 更新 [完成]
- main.py 集成检测服务 [完成]

代码特征：
- AlertDetectionService 类，生命周期管理
- MQTT数据回调机制
- Redis重复抑制
- 趋势检测异步任务
```

---

## 你的决策

- [ ] 规则阈值合理 → 继续Prompt 1
- [ ] 需要调整阈值 → 告诉Claude修改数值
- [ ] 想增加规则 → 添加新检测逻辑

---

## 手工验证

```bash
# 启动服务后，运行模拟器产生异常数据
cd simulator
python3 device_simulator.py --count 2

# 观察后端日志，应该看到：
# "Alert triggered: DEV001 temperature=85.5"
# "Alert suppressed: DEV001 temperature (recent alert exists)"
```
