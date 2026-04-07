# Day 3 - Prompt 2: WebSocket告警推送

**时机**：告警API完成后执行
**预期耗时**：Claude生成15分钟，你Review 10分钟
**人工决策**：确认实时推送机制，测试端到端数据流

---

## 输入Prompt

```text
请实现告警的WebSocket实时推送，让前端能立即看到新告警。

【Redis订阅集成】（app/api/websocket.py 更新）

在现有的WebSocket管理器（ConnectionManager）中：

1. 添加Redis订阅监听器（复用已有的start_redis_listener）
   - 订阅频道 "alerts:new"
   - 当收到新告警消息时，广播给所有连接的客户端

2. 告警消息格式：
   {
     "type": "new_alert",
     "data": {
       "id": 1,
       "device_id": 1,
       "device_name": "压缩机-01",
       "alert_type": "threshold",
       "metric": "temperature",
       "message": "温度过高: 85℃ > 80℃",
       "level": "critical",
       "created_at": "2026-04-07T10:30:00Z"
     }
   }

3. WebSocket端点扩展
   - 连接时支持订阅特定主题：?topics=alerts,sensors
   - alerts主题：接收新告警推送
   - sensors主题：接收传感器数据（已有）
   - 默认订阅全部

【告警服务集成】（app/services/alert_detection.py 更新）

当生成新告警时：
1. 写入数据库（已有）
2. 同时发布到Redis：
   - 频道："alerts:new"
   - 消息：JSON序列化的告警数据（包含device_name）

【WebSocket消息类型】

所有WebSocket消息统一格式：
{
  "type": "message_type",
  "timestamp": "2026-04-07T10:30:00Z",
  "data": { ... }
}

消息类型：
- sensor_data：传感器实时数据（已有）
- new_alert：新告警通知
- alert_updated：告警状态更新（确认/解决时）
- connection_ack：连接确认

【告警状态更新推送】

当通过API确认或解决告警时：
- 广播alert_updated消息
- 格式：
  {
    "type": "alert_updated",
    "data": {
      "id": 1,
      "status": "acknowledged",
      "acknowledged_at": "2026-04-07T10:35:00Z"
    }
  }

【前端测试页面】（可选，static/alerts_demo.html）

创建一个简单的HTML页面：
- 连接WebSocket
- 显示实时告警列表（新告警自动追加到顶部）
- 支持一键确认告警
- 显示当前连接状态

【性能考虑】
- WebSocket广播使用asyncio.gather并行发送
- Redis订阅使用单独的Task运行
- 连接断开时自动清理资源

【验证步骤】

1. 启动后端服务
2. 打开前端测试页面（或直接用wscat）
3. 运行模拟器产生异常数据
4. 观察WebSocket是否收到new_alert消息
5. 通过API确认告警，观察是否收到alert_updated消息
```

---

## 预期输出

```
更新文件：
- app/api/websocket.py [更新]
- app/services/alert_detection.py [更新]
- app/services/alert_service.py [更新，如果需要]
- static/alerts_demo.html [创建，可选]

数据流验证：
模拟器异常数据 → MQTT → 检测服务 → 数据库+Redis → WebSocket广播 → 前端接收
      ↓              ↓           ↓              ↓               ↓
   生成异常      订阅topic   触发阈值      发布频道        推送客户端
```

---

## 你的决策

- [ ] WebSocket推送正常 → 继续Prompt 3（验证）
- [ ] 消息格式需调整 → 告诉Claude修改
- [ ] 想增加广播范围 → 添加更多频道

---

## 手工验证

```bash
# 使用wscat测试WebSocket
npm install -g wscat
wscat -c "ws://localhost:8000/ws?topics=alerts"

# 在另一个终端运行模拟器
cd simulator
python3 device_simulator.py --count 2

# 观察wscat输出，应该收到new_alert消息
```

## 调试命令

```bash
# 查看Redis发布情况
docker exec lqy_redis redis-cli subscribe alerts:new

# 检查WebSocket连接日志
docker logs lqy_backend | grep WebSocket
```
