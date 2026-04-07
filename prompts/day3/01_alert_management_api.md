# Day 3 - Prompt 1: 告警管理API

**时机**：告警检测服务完成后执行
**预期耗时**：Claude生成15分钟，你Review 10分钟
**人工决策**：确认API设计满足前端需求

---

## 输入Prompt

```text
请实现完整的告警管理API，支持查询、确认、解决操作。

【告警API】（app/api/v1/alerts.py）

1. GET /api/v1/alerts
   - Query参数：
     - page: int=1
     - size: int=20
     - device_id: int=None, 指定设备
     - level: str=None, 支持多选（critical,warning,info）
     - status: str=None, 支持多选（active,acknowledged,resolved）
     - metric: str=None, 支持多选（temperature,vibration,current）
     - start: datetime=None, 告警开始时间（ISO8601）
     - end: datetime=None, 告警结束时间
   - 默认排序：created_at desc（最新的在前）
   - 返回ListResponse[AlertResponse]

2. GET /api/v1/alerts/stats
   - 返回告警统计：
     - total_active: 当前活跃告警数
     - total_today: 今日产生告警数
     - by_level: {critical: 3, warning: 5, info: 2}
     - by_metric: {temperature: 4, vibration: 3, current: 1}

3. POST /api/v1/alerts/{id}/acknowledge
   - 确认告警（用户已知晓）
   - 更新status=acknowledged, acknowledged_at=now()
   - 返回AlertResponse
   - 已经是acknowledged/resolverd的返回200（幂等）

4. POST /api/v1/alerts/{id}/resolve
   - 解决告警（问题已处理）
   - 更新status=resolved, resolved_at=now()
   - 返回AlertResponse
   - 允许从未确认直接到已解决

5. POST /api/v1/alerts/acknowledge-batch
   - 批量确认
   - Body: {ids: [1,2,3]}
   - 批量更新，返回{updated: 3}

【告警规则API】（app/api/v1/alert_rules.py）

1. GET /api/v1/alert-rules
   - 获取所有告警规则
   - 返回ListResponse[AlertRuleResponse]

2. POST /api/v1/alert-rules
   - 创建新规则
   - Body: AlertRuleCreate
   - 验证：metric+operator+threshold组合不能重复

3. PUT /api/v1/alert-rules/{id}
   - 更新规则（全部字段可选）
   - 可以启用/禁用规则（enabled字段）

4. DELETE /api/v1/alert-rules/{id}
   - 物理删除规则
   - 返回204

【Schema更新】（app/schemas/alert.py, alert_rule.py）

AlertResponse：
- 包含device_name（关联查询）
- 包含duration_seconds（从created_at到现在或resolved_at的秒数）

AlertRuleCreate/Update：
- device_id: Optional[int]
- metric: RuleMetric
- operator: RuleOperator
- threshold: float
- duration: int=0
- enabled: bool=True
- description: Optional[str]

【路由注册】
在main.py注册：
- /api/v1/alerts
- /api/v1/alert-rules

【测试】（app/tests/test_alerts.py）

至少8个测试：
1. test_list_alerts_pagination - 分页查询
2. test_list_alerts_filter_by_level - 级别过滤
3. test_list_alerts_filter_by_status - 状态过滤
4. test_acknowledge_alert_success - 确认告警
5. test_resolve_alert_success - 解决告警
6. test_get_alert_stats - 统计接口
7. test_create_alert_rule - 创建规则
8. test_disable_alert_rule - 禁用规则

【验证步骤】
生成后执行：
1. cd backend
2. docker-compose up -d
3. pytest app/tests/test_alerts.py -v
4. 预期：8个测试全部通过
```

---

## 预期输出

```
生成文件：
- app/api/v1/alerts.py [完成]
- app/api/v1/alert_rules.py [完成]
- app/schemas/alert.py 更新 [完成]
- app/schemas/alert_rule.py 更新 [完成]
- app/tests/test_alerts.py [完成]
- main.py 路由注册 [完成]

API列表：
GET    /api/v1/alerts
GET    /api/v1/alerts/stats
POST   /api/v1/alerts/{id}/acknowledge
POST   /api/v1/alerts/{id}/resolve
POST   /api/v1/alerts/acknowledge-batch
GET    /api/v1/alert-rules
POST   /api/v1/alert-rules
PUT    /api/v1/alert-rules/{id}
DELETE /api/v1/alert-rules/{id}
```

---

## 你的决策

- [ ] API设计满足需求 → 继续Prompt 2
- [ ] 需要添加字段 → 告诉Claude修改
- [ ] 想调整接口路径 → 修改路由

---

## 手工验证

```bash
# 查询活跃告警
curl "http://localhost:8000/api/v1/alerts?status=active"

# 确认告警
curl -X POST http://localhost:8000/api/v1/alerts/1/acknowledge

# 查看统计
curl http://localhost:8000/api/v1/alerts/stats
```
