# Day 3: 告警引擎 - 任务概览

**目标**：构建完整的告警检测、管理和推送系统
**核心交付**：模拟器异常数据能实时触发告警，并通过WebSocket推送

---

## 任务结构

| 序号 | 文件 | 内容 | 预计耗时 |
|------|------|------|----------|
| 00 | [告警检测服务](00_detection_service.md) | 阈值检测、趋势分析、重复抑制 | 30分钟 |
| 01 | [告警管理API](01_alert_management_api.md) | 告警CRUD、确认/解决、规则管理 | 25分钟 |
| 02 | [WebSocket推送](02_websocket_integration.md) | 实时告警推送、状态更新广播 | 25分钟 |
| 03 | [验证测试](03_validation.md) | 端到端验证、性能测试、Git提交 | 30分钟 |

**总计**：约2小时（含Review时间）

---

## 关键架构

```
传感器数据流：
模拟器 → MQTT → 后端订阅 → 检测服务 → 数据库
                              ↓
                         WebSocket广播
                              ↓
                           前端接收

告警检测逻辑：
- 阈值检测：实时（每条数据）
- 趋势检测：定时（每10分钟）
- 重复抑制：Redis缓存（5分钟窗口）
```

---

## 核心功能点

### 1. 检测规则
- **温度**：
  - > 80℃ → Critical
  - > 65℃ → Warning
- **振动**：
  - > 5.0mm/s → Warning
- **电流**：
  - > 20A → Critical

### 2. 趋势检测
- 连续5点上升（总升温>10℃）→ Warning
- 10分钟内从<50℃升至>70℃ → Critical

### 3. API端点
```
GET    /api/v1/alerts              # 查询告警列表
GET    /api/v1/alerts/stats        # 告警统计
POST   /api/v1/alerts/{id}/acknowledge  # 确认告警
POST   /api/v1/alerts/{id}/resolve      # 解决告警
GET    /api/v1/alert-rules        # 查询规则
POST   /api/v1/alert-rules        # 创建规则
PUT    /api/v1/alert-rules/{id}   # 更新规则
```

### 4. WebSocket消息
```json
{
  "type": "new_alert",
  "timestamp": "2026-04-07T10:30:00Z",
  "data": { "id": 1, "level": "critical", ... }
}
```

---

## 验证清单

- [ ] 模拟器产生异常 → 3秒内生成告警
- [ ] 同一异常5分钟内不重复告警
- [ ] WebSocket客户端实时收到推送
- [ ] 告警可正常确认和解决
- [ ] 趋势检测准确识别升温
- [ ] 性能：检测延迟 < 1秒

---

## 风险提示

1. **Redis依赖**：重复抑制依赖Redis，如果Redis不可用会降级为不抑制
2. **性能瓶颈**：趋势检测扫描历史数据，设备多时可能慢
3. **WebSocket广播**：大量连接时广播可能有延迟

---

## 启动指令

在Claude中输入：
```
请读取 prompts/day3/00_detection_service.md 并开始执行
```

每完成一个Prompt，Claude会询问是否继续。

---

**昨日成果**：Day 2已完成MQTT + WebSocket + 设备模拟器
**明日预告**：Day 4将构建Vue3前端看板，展示实时数据流和告警
