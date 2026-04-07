# Day6 系统集成测试计划

## 测试目标
验证前端、后端、MQTT、数据库全链路集成正常工作

## 测试范围

### 1. 端到端功能测试 (E2E)
- [ ] 设备列表展示与搜索
- [ ] 实时数据推送（WebSocket）
- [ ] 告警生成与通知
- [ ] 数据历史查询

### 2. 性能测试
- [ ] 并发设备连接（50+）
- [ ] WebSocket推送性能（消息延迟<100ms）
- [ ] API响应时间（<200ms）
- [ ] 数据库查询性能

### 3. 告警验证
- [ ] 阈值告警触发
- [ ] 趋势告警检测
- [ ] 告警确认/解决流程
- [ ] 告警历史记录

### 4. 部署验证
- [ ] Docker Compose完整启动
- [ ] 服务健康检查
- [ ] 网络连通性
- [ ] 数据持久化

## 测试工具

### 设备模拟器
```bash
python tests/e2e/device_simulator.py --count 10 --interval 5
```

### 性能测试
```bash
python tests/performance/load_test.py --devices 50 --duration 60
```

### E2E测试
```bash
pytest tests/e2e/ -v
```

## 测试数据

### 模拟设备数据格式
```json
{
  "device_id": "DEV001",
  "temperature": 65.5,
  "vibration": 3.2,
  "current": 15.1,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 告警触发条件
- 温度 > 80°C
- 振动 > 6.0 mm/s  
- 电流 > 20A

## 成功标准

1. **功能完整**: 所有E2E测试通过
2. **性能达标**: 
   - API响应 < 200ms (P95)
   - WebSocket延迟 < 100ms
   - 支持50+并发设备
3. **稳定性**: 连续运行30分钟无错误
4. **数据一致性**: 数据库记录与MQTT消息一致

## 测试环境

```yaml
# docker-compose.test.yml
版本: 测试专用
服务:
  - postgres (测试数据库)
  - redis (测试缓存)
  - emqx (MQTT broker)
  - backend (FastAPI)
  - frontend (Vue3)
```

## 执行步骤

1. **准备环境** (5分钟)
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

2. **运行E2E测试** (10分钟)
   ```bash
   pytest tests/e2e/ -v --tb=short
   ```

3. **运行性能测试** (15分钟)
   ```bash
   python tests/performance/load_test.py
   ```

4. **验证告警系统** (5分钟)
   ```bash
   python tests/e2e/test_alert_flow.py
   ```

5. **生成报告** (2分钟)
   ```bash
   python tests/generate_report.py
   ```

## 故障排查

### 常见问题

1. **MQTT连接失败**
   - 检查EMQX是否启动
   - 检查端口1883是否开放

2. **WebSocket推送延迟**
   - 检查Redis连接
   - 检查后端日志

3. **数据库连接错误**
   - 检查PostgreSQL状态
   - 验证连接字符串

## 测试报告

测试完成后生成：`docs/day6_test_report.md`

包含：
- 测试通过率
- 性能指标
- 故障截图
- 改进建议
