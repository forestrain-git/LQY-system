# 架构契约（不可变）

**规则**：Claude生成任何代码前，必须读取此文件。所有代码必须符合以下规范。

---

## 1. 技术栈（锁定）

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 后端 | FastAPI | >=0.104 | 异步优先 |
| ORM | SQLModel | >=0.0.14 | 基于SQLAlchemy 2.0 |
| 数据库 | PostgreSQL | 15 | 单库，不用TimescaleDB |
| 缓存 | Redis | 7 | 简单键值 |
| Python | Python | 3.11+ | 必须使用async/await |

---

## 2. API响应格式（强制）

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 100,
    "pages": 5
  }
}
```

- `code`: 0表示成功，非0表示错误（见错误代码表）
- `pagination`: 仅列表接口需要
- 所有时间字段: ISO8601格式 (2026-04-06T10:00:00Z)

---

## 3. 错误代码表

| 代码 | 含义 | HTTP状态 |
|------|------|----------|
| 0 | 成功 | 200 |
| 1001 | 参数验证错误 | 422 |
| 1002 | 资源不存在 | 404 |
| 1003 | 资源已存在 | 409 |
| 2001 | 数据库错误 | 500 |
| 2002 | 外部服务错误 | 502 |
| 3001 | 业务逻辑错误 | 400 |

---

## 4. 数据库规范

### 命名
- 表名: snake_case, 复数 (devices, sensor_data)
- 字段: snake_case (created_at, device_id)
- 索引: idx_表名_字段名
- 外键: fk_表名_引用表

### 必须字段
所有表必须有：
- `id`: int, PrimaryKey, autoincrement
- `created_at`: datetime, 默认now
- `updated_at`: datetime, onupdate=now

### 软删除策略
**不允许物理删除**，使用status字段：
- `status`: enum (active/disabled)
- 删除操作 = UPDATE status='disabled'

---

## 5. 代码风格

### Python
- 使用类型注解（必须）
- 函数docstring格式：
  ```python
  async def create_device(data: DeviceCreate) -> DeviceResponse:
      """创建设备

      Args:
          data: 设备创建数据

      Returns:
          DeviceResponse: 创建后的设备

      Raises:
          HTTPException: 409 如果名称已存在
      """
  ```

### 文件组织
```
app/
├── models/      # 数据库模型
├── schemas/     # Pydantic模型
├── api/v1/      # API路由
├── services/    # 业务逻辑
└── tests/       # 单元测试
```

---

## 6. 测试要求

- 覆盖率 > 80%
- 每个API至少2个测试（成功+失败）
- 使用pytest-asyncio
- 测试数据库隔离

---

## 7. 关键决策（已确定）

| 决策 | 选择 | 原因 |
|------|------|------|
| 删除策略 | status=disabled | 数据完整性 |
| 分页参数 | page/size | 标准做法 |
| 时间存储 | UTC | 统一标准 |
| 数据库 | PostgreSQL单库 | 简单够用 |

**这些决策不可更改**，如果Claude发现冲突，必须询问。
