# Day 1 - Prompt 2: 模型生成

**时机**：项目结构OK后执行
**预期耗时**：Claude生成10分钟，你Review 5分钟
**人工决策**：确认字段设计后继续

---

## 输入Prompt

```text
请生成SQLModel模型和Schema文件。

【Device模型】（app/models/device.py）
字段：
- id: int, PrimaryKey, auto_increment
- name: str, 索引, 长度50, 不能重复, 不能空
- type: str, 默认'compressor'，枚举：compressor/pump/fan/conveyor/other
- location: str, 长度100, 可空
- status: str, 默认'offline'，枚举：online/offline/maintenance/disabled
  - 注意：没有deleted状态，删除用disabled代替
- created_at: datetime, 默认now
- updated_at: datetime, auto_update

关系：
- sensor_data: List[SensorData]，back_populates="device"，cascade删除
- alerts: List[Alert]，back_populates="device"，cascade删除

方法：
- __repr__: 返回 <Device: {name} ({status})>

【SensorData模型】（app/models/sensor_data.py）
字段：
- id: int, PrimaryKey
- device_id: int, ForeignKey, 索引
- temperature: float, 可空, 单位℃
- vibration: float, 可空, 单位mm/s
- current: float, 可空, 单位A
- timestamp: datetime, 索引, 默认now

关系：
- device: Device, back_populates="sensor_data"

【Alert模型】（app/models/alert.py）
字段：
- id: int, PrimaryKey
- device_id: int, ForeignKey, 索引
- alert_type: str, 默认'threshold'，枚举：threshold/trend/prediction/system
- metric: str, 默认'system'，枚举：temperature/vibration/current/system
- message: str, 长度200
- level: str, 默认'info'，枚举：critical/warning/info
- status: str, 默认'active'，枚举：active/acknowledged/resolved
- created_at: datetime, 默认now
- acknowledged_at: datetime, 可空
- resolved_at: datetime, 可空

【AlertRule模型】（app/models/alert_rule.py）
字段：
- id: int, PrimaryKey
- device_id: int, ForeignKey, 可空（空表示所有设备）
- metric: str, 枚举：temperature/vibration/current
- operator: str, 枚举：gt/lt/eq（gt=大于，lt=小于，eq=等于）
- threshold: float
- duration: int, 默认0，单位秒
- enabled: bool, 默认True
- description: str, 长度200, 可空

【Schema文件】

app/schemas/device.py：
- DeviceBase: name, type, location, status
- DeviceCreate: 继承Base
- DeviceUpdate: 继承Base，所有字段Optional
- DeviceResponse: 完整字段 + latest_sensor_data: Optional[SensorDataResponse]

app/schemas/sensor_data.py：
- SensorDataBase: device_id, temperature, vibration, current
- SensorDataCreate: 继承Base
- SensorDataResponse: 完整字段 + device_name: str

app/schemas/alert.py：
- 类似的Base/Create/Update/Response结构
- AlertResponse包含device_name

app/schemas/alert_rule.py：
- 类似的结构

app/schemas/common.py：
- class ResponseBase(Generic[T]): code, message, data
- class ListResponse(ResponseBase[T]): 额外加pagination字段
- pagination字段：page, size, total, pages

【验证脚本】
创建 test_models.py：
1. 验证所有模型能import
2. 验证能创建实例
3. 验证关系能建立
4. 输出所有表的SQL（可选）

执行：python test_models.py，确保无报错。

【要求】
- 所有模型加中文注释
- 所有枚举字段加文档字符串
- 使用TypeVar做泛型
- 生成后立即验证
```

---

## 预期输出

```
生成进度：
- app/models/device.py [完成]
- app/models/sensor_data.py [完成]
- app/models/alert.py [完成]
- app/models/alert_rule.py [完成]
- app/models/__init__.py [完成]
- app/schemas/device.py [完成]
- app/schemas/sensor_data.py [完成]
- app/schemas/alert.py [完成]
- app/schemas/alert_rule.py [完成]
- app/schemas/common.py [完成]
- app/schemas/__init__.py [完成]
- test_models.py [完成]

验证结果：
python test_models.py
[输出] 所有模型加载成功

下一步：确认模型设计OK，继续Prompt 3（API实现）
```

---

## 关键字段确认（人工决策）

| 字段 | 你的决策 | 说明 |
|------|----------|------|
| Device.status | disabled代替删除 | 已确认 |
| Alert.level | critical/warning/info三级 | 够用吗？ |
| AlertRule.duration | 0秒立即触发 | 需要防抖动吗？ |
| SensorData.timestamp | UTC存储 | 前端显示转本地时间 |

如果以上OK → 继续Prompt 3
如果需要改 → 告诉Claude改哪里
