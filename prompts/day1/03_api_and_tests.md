# Day 1 - Prompt 3: API实现与单元测试

**时机**：模型OK后执行
**预期耗时**：Claude生成20分钟，你Review 10分钟
**人工决策**：确认API设计，验收测试通过率

---

## 输入Prompt

```text
请实现完整的Device和SensorData API，包含单元测试。

【Device API】（app/api/v1/devices.py）

1. POST /api/v1/devices
   - Body: DeviceCreate
   - 检查name是否已存在，存在返回409 Conflict
   - 创建成功返回201，body是DeviceResponse

2. GET /api/v1/devices
   - Query参数：
     - page: int=1, 从1开始
     - size: int=20, 最大100
     - status: str=None, 支持多选（逗号分隔：online,offline）
     - type: str=None, 支持多选
     - name: str=None, 模糊搜索（ilike）
   - 默认排序：updated_at desc
   - 返回ListResponse[DeviceResponse]

3. GET /api/v1/devices/{id}
   - Path参数：id: int
   - 不存在返回404
   - 返回DeviceResponse（包含latest_sensor_data）
   - latest_sensor_data通过子查询获取最新一条

4. PUT /api/v1/devices/{id}
   - Body: DeviceUpdate（所有字段optional）
   - 不能修改status为deleted（没有这个值）
   - 返回更新后的DeviceResponse

5. DELETE /api/v1/devices/{id}
   - 实际是禁用：UPDATE status='disabled'
   - 返回204 No Content（无body）
   - 已经是disabled的返回204（幂等）

6. GET /api/v1/devices/{id}/data
   - Query参数：page, size, start, end（ISO8601时间）
   - 返回该设备的SensorData列表
   - 按timestamp desc排序

7. GET /api/v1/devices/{id}/stats
   - 返回今日统计：
     - total_records: 今日数据条数
     - avg_temperature: 平均温度（可为null）
     - avg_vibration: 平均振动
     - avg_current: 平均电流
     - latest_timestamp: 最新数据时间

【SensorData API】（app/api/v1/sensor_data.py）

1. POST /api/v1/sensor-data
   - Body: 单条或列表（List[SensorDataCreate]）
   - 最多接受100条
   - 验证device_id存在且status!=disabled
   - 批量插入
   - 返回{ids: [1,2,3], count: 3}

2. GET /api/v1/sensor-data/export
   - Query: device_id, start, end
   - 返回CSV文件（StreamingResponse）
   - CSV列：timestamp,device_name,temperature,vibration,current

【统一错误处理】（app/exceptions/handlers.py）
- HTTPException：返回{code: status_code, message: detail}
- 通用Exception：返回{code: 500, message: "Internal Server Error"}，打印堆栈
- RequestValidationError：返回{code: 422, message: "Validation Error", details: [...]}

【日志】（app/middleware/logging.py）
- 记录每个请求：method, path, status_code, duration_ms
- 使用标准logging
- 格式："{timestamp} {method} {path} {status} {duration}ms"

【单元测试】（app/tests/）

conftest.py：
- 创建async测试客户端（httpx.AsyncClient）
- 使用测试数据库（SQLite内存或测试PostgreSQL）
- 每个测试后清理数据

test_devices.py（至少9个测试）：
1. test_create_device_success - 正常创建，返回201
2. test_create_device_duplicate_name - 重复名，返回409
3. test_list_devices_pagination - 分页正常
4. test_list_devices_filter_by_status - 状态过滤
5. test_list_devices_search_by_name - 模糊搜索
6. test_get_device_success - 获取成功，包含latest_data
7. test_get_device_not_found - 不存在，返回404
8. test_update_device_success - 更新成功
9. test_delete_device_actually_disables - 删除后status=disabled
10. test_get_device_stats - 统计正确

test_sensor_data.py（至少4个测试）：
1. test_create_sensor_data_success - 单条创建
2. test_create_sensor_data_batch - 批量创建（最多100）
3. test_create_sensor_data_device_disabled - 设备disabled返回400
4. test_export_sensor_data - CSV导出

【测试要求】
- 使用pytest-asyncio
- 覆盖率>80%（pytest-cov）
- 测试独立，不依赖顺序
- 使用fixture准备测试数据

【在main.py中注册】
- 注册路由：/api/v1/devices, /api/v1/sensor-data
- 注册异常处理器
- 注册日志中间件

【验证步骤】
生成后执行：
1. cd backend
2. docker-compose up -d postgres redis
3. pytest -v --cov=app --cov-report=term-missing
4. 预期：13个测试全部通过，覆盖率>80%

如果有测试失败，修复后再继续。
```

---

## 预期输出

```
生成进度：
- app/api/v1/devices.py [完成]
- app/api/v1/sensor_data.py [完成]
- app/api/v1/__init__.py [完成]
- app/api/__init__.py [完成]
- app/exceptions/handlers.py [完成]
- app/middleware/logging.py [完成]
- app/tests/conftest.py [完成]
- app/tests/test_devices.py [完成]
- app/tests/test_sensor_data.py [完成]
- app/main.py更新 [完成]

测试执行：
pytest -v --cov=app
===================
test_devices.py::test_create_device_success PASSED
test_devices.py::test_create_device_duplicate_name PASSED
... 共13个测试 PASSED

覆盖率：
app/api/v1/devices.py: 95%
app/api/v1/sensor_data.py: 88%
app/models/: 100%
app/schemas/: 100%
总体: 87%

下一步：确认测试通过，继续Prompt 4（Docker完善）
```

---

## 你的决策

- [ ] 全部测试通过 → 继续Prompt 4
- [ ] 部分测试失败 → 让Claude修复失败的测试
- [ ] 覆盖率不够 → 决定接受或补充测试
- [ ] API设计想调整 → 告诉Claude修改

---

## 手工验证命令（可选）

```bash
cd backend
docker-compose up -d postgres redis
# 等待5秒
pytest -xvs app/tests/test_devices.py::test_create_device_success
# 单测试调试用
curl -X POST http://localhost:8000/api/v1/devices \
  -H "Content-Type: application/json" \
  -d '{"name":"TEST001","type":"compressor"}'
```
