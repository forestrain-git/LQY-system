# Day 3 - Prompt 3: 告警引擎验证

**时机**：所有告警功能完成后执行
**预期耗时**：Claude生成15分钟，你Review 15分钟
**人工决策**：确认告警引擎工作正常，准备Git提交

---

## 输入Prompt

```text
请创建完整的告警引擎验证脚本和测试。

【端到端验证脚本】（validate_alerts.py）

创建 backend/validate_alerts.py：

功能：模拟完整告警流程，验证端到端数据流

步骤：
1. 清空测试告警数据
2. 创建设备（如果不足）
3. 插入模拟传感器数据（触发阈值）
4. 等待检测服务生成告警
5. 查询API验证告警已创建
6. 测试确认/解决API
7. 验证WebSocket推送（模拟连接）
8. 输出验证报告

具体测试场景：
- 场景1：温度超标（Critical）
- 场景2：振动异常（Warning）
- 场景3：重复抑制（5分钟内不重复）
- 场景4：趋势检测（连续升温）

【性能测试】（benchmark_alerts.py）

创建 backend/benchmark_alerts.py：

测试告警检测性能：
- 模拟1000条传感器数据
- 测量检测延迟（从数据到告警创建）
- 测量吞吐量（每秒处理多少条）
- 输出性能报告

【集成测试】（app/tests/test_alert_detection.py）

至少6个测试：
1. test_threshold_detection_critical - 阈值检测Critical
2. test_threshold_detection_warning - 阈值检测Warning
3. test_duplicate_suppression - 重复抑制
4. test_trend_detection_rising - 上升趋势检测
5. test_alert_lifecycle - 告警生命周期（创建→确认→解决）
6. test_websocket_notification - WebSocket通知（模拟）

【数据清理脚本】（cleanup_alerts.py）

创建 backend/cleanup_alerts.py：
- 清理所有测试告警数据
- 保留最近7天的生产数据
- 重置Redis缓存

【验证步骤】

生成后执行：
1. cd backend
2. docker-compose up -d
3. python3 validate_alerts.py
4. pytest app/tests/test_alert_detection.py -v
5. python3 benchmark_alerts.py

预期结果：
- 端到端验证：所有场景通过
- 单元测试：6个测试全部通过
- 性能：检测延迟 < 1秒，吞吐量 > 100条/秒
```

---

## 预期输出

```
生成文件：
- backend/validate_alerts.py [完成]
- backend/benchmark_alerts.py [完成]
- backend/cleanup_alerts.py [完成]
- app/tests/test_alert_detection.py [完成]

验证报告示例：
==================================================
龙泉驿环卫智能体 - Day 3 告警引擎验证
==================================================

[场景1] 温度超标检测
  输入: device_id=1, temperature=85.5
  期望: 生成Critical告警
  结果: ✓ PASS (告警ID: 123)

[场景2] 重复抑制
  输入: 同一设备再次超标
  期望: 5分钟内不生成新告警
  结果: ✓ PASS (被抑制)

[场景3] 趋势检测
  输入: 连续5个点温度上升 [50,55,62,68,75]
  期望: 生成Trend告警
  结果: ✓ PASS

性能测试:
  总数据量: 1000条
  检测延迟: avg=234ms, max=512ms
  吞吐量: 456条/秒

结论: 告警引擎工作正常，性能满足需求
```

---

## 你的决策

- [ ] 所有验证通过 → 执行Git提交
- [ ] 部分测试失败 → 让Claude修复
- [ ] 性能不达标 → 优化检测逻辑
- [ ] 功能完整 → 标记Day 3完成

---

## Git提交

```bash
# 提交Day 3成果
git add .
git commit -m "Day 3: 告警引擎 - 实时检测 + 趋势分析 + WebSocket推送

- 实现AlertDetectionService，支持阈值和趋势检测
- 实现告警管理API（查询、确认、解决）
- 实现告警规则动态管理
- WebSocket实时推送新告警
- Redis重复抑制机制
- 完整测试覆盖，端到端验证通过

验证: python3 validate_alerts.py"

# 标记里程碑
git tag day3-complete
```

---

## Day 3 完成标准

- [ ] 告警检测服务运行中
- [ ] 告警API可正常访问
- [ ] WebSocket推送新告警
- [ ] 端到端验证脚本通过
- [ ] 所有测试通过（覆盖率>75%）
- [ ] Git提交并打标签

## 明日准备

Day 4将构建前端看板，需要：
- 确保WebSocket接口稳定
- 准备API文档（自动生成的/docs）
- 确认告警数据格式前端友好
