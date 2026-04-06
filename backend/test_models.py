"""模型验证脚本

验证所有模型和Schema能正确导入和实例化
"""

import sys
from datetime import datetime, timezone

print("=" * 50)
print("龙泉驿环卫智能体 - 模型验证")
print("=" * 50)

# 1. 验证模型导入
print("\n[1/4] 验证模型导入...")
try:
    from app.models import (
        Alert,
        AlertLevel,
        AlertMetric,
        AlertRule,
        AlertStatus,
        AlertType,
        Device,
        DeviceStatus,
        DeviceType,
        RuleMetric,
        RuleOperator,
        SensorData,
    )
    print("  ✓ 所有模型导入成功")
except Exception as e:
    print(f"  ✗ 模型导入失败: {e}")
    sys.exit(1)

# 2. 验证Schema导入
print("\n[2/4] 验证Schema导入...")
try:
    from app.schemas import (
        AlertCreate,
        AlertResponse,
        AlertRuleCreate,
        AlertRuleResponse,
        DeviceCreate,
        DeviceResponse,
        DeviceUpdate,
        ListResponse,
        Pagination,
        ResponseBase,
        SensorDataCreate,
        SensorDataResponse,
    )
    print("  ✓ 所有Schema导入成功")
except Exception as e:
    print(f"  ✗ Schema导入失败: {e}")
    sys.exit(1)

# 3. 验证模型实例创建
print("\n[3/4] 验证模型实例化...")
try:
    # 创建设备
    device = Device(
        name="测试设备-01",
        type=DeviceType.COMPRESSOR,
        location="测试位置",
        status=DeviceStatus.ONLINE,
    )
    print(f"  ✓ 设备模型: {device}")

    # 创建传感器数据
    sensor_data = SensorData(
        device_id=1,
        temperature=65.5,
        vibration=2.3,
        current=12.5,
        timestamp=datetime.now(timezone.utc),
    )
    print(f"  ✓ 传感器数据模型: {sensor_data}")

    # 创建告警
    alert = Alert(
        device_id=1,
        alert_type=AlertType.THRESHOLD,
        metric=AlertMetric.TEMPERATURE,
        message="温度过高: 85℃",
        level=AlertLevel.WARNING,
    )
    print(f"  ✓ 告警模型: {alert}")

    # 创建告警规则
    rule = AlertRule(
        device_id=1,
        metric=RuleMetric.TEMPERATURE,
        operator=RuleOperator.GT,
        threshold=80.0,
        duration=60,
        description="温度超过80℃持续1分钟",
    )
    print(f"  ✓ 告警规则模型: {rule}")

    # 验证规则检查
    assert rule.check_condition(85.0) == True, "规则检查应该返回True"
    assert rule.check_condition(75.0) == False, "规则检查应该返回False"
    print("  ✓ 规则检查逻辑验证通过")

except Exception as e:
    print(f"  ✗ 模型实例化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 验证Schema实例创建
print("\n[4/4] 验证Schema实例化...")
try:
    # 设备Schema
    device_create = DeviceCreate(
        name="新设备",
        type=DeviceType.PUMP,
        location="A区",
        status=DeviceStatus.OFFLINE,
    )
    print(f"  ✓ 设备创建Schema: {device_create.name}")

    device_update = DeviceUpdate(name="更新后的名称")
    print(f"  ✓ 设备更新Schema: {device_update.name}")

    # 传感器数据Schema
    sensor_create = SensorDataCreate(
        device_id=1,
        temperature=70.0,
        vibration=1.5,
        current=10.0,
    )
    print(f"  ✓ 传感器数据创建Schema: device_id={sensor_create.device_id}")

    # 告警Schema
    alert_create = AlertCreate(
        device_id=1,
        message="测试告警",
        level=AlertLevel.CRITICAL,
    )
    print(f"  ✓ 告警创建Schema: {alert_create.level.value}")

    # 告警规则Schema
    rule_create = AlertRuleCreate(
        metric=RuleMetric.VIBRATION,
        operator=RuleOperator.GT,
        threshold=5.0,
    )
    print(f"  ✓ 告警规则创建Schema: {rule_create.metric.value}")

    # 响应Schema
    response = ResponseBase(data={"test": "data"})
    print(f"  ✓ 基础响应Schema: code={response.code}")

    pagination = Pagination(page=1, size=20, total=100, pages=5)
    print(f"  ✓ 分页Schema: page={pagination.page}, total={pagination.total}")

except Exception as e:
    print(f"  ✗ Schema实例化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 输出表信息
print("\n" + "=" * 50)
print("数据库表信息")
print("=" * 50)
try:
    from app.models import SQLModel
    from app.database import engine

    for table_name in SQLModel.metadata.tables:
        table = SQLModel.metadata.tables[table_name]
        print(f"\n表: {table_name}")
        for column in table.columns:
            print(f"  - {column.name}: {column.type}")
except Exception as e:
    print(f"  无法输出表信息（数据库未连接）: {e}")

print("\n" + "=" * 50)
print("✓ 所有验证通过！")
print("=" * 50)
