# 龙泉驿环卫智能体 - 后端API

龙泉驿区环境卫生智能管理系统后端服务

## 快速开始（3步启动）

```bash
cd backend
make up          # 启动所有服务
make migrate     # 运行数据库迁移（首次）
# 访问 http://localhost:8000/docs
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `make up` | 启动所有服务 |
| `make down` | 停止所有服务 |
| `make logs` | 查看后端日志 |
| `make test` | 运行单元测试 |
| `make shell` | 进入后端容器 |
| `make migrate` | 运行数据库迁移 |
| `make db-shell` | 进入PostgreSQL命令行 |
| `make diagnose` | 运行故障诊断 |

## API文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 项目结构

```
backend/
├── app/
│   ├── api/v1/          # API路由
│   ├── models/          # 数据库模型
│   ├── schemas/         # Pydantic模型
│   ├── services/        # 业务逻辑
│   ├── tests/           # 单元测试
│   ├── exceptions/      # 异常处理
│   ├── middleware/      # 中间件
│   ├── main.py          # 应用入口
│   ├── config.py        # 配置
│   ├── database.py      # 数据库连接
│   └── redis.py         # Redis连接
├── alembic/             # 数据库迁移
├── docker-compose.yml   # Docker编排
├── Dockerfile           # 容器镜像
├── Makefile            # 常用命令
├── start.sh            # 启动脚本
├── diagnose.py         # 故障诊断
└── requirements.txt    # Python依赖
```

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| DATABASE_URL | postgresql+asyncpg://postgres:postgres@localhost:5432/lqy_db | PostgreSQL连接字符串 |
| REDIS_URL | redis://localhost:6379/0 | Redis连接字符串 |
| LOG_LEVEL | info | 日志级别 (debug/info/warning/error) |
| PYTHONUNBUFFERED | 1 | Python无缓冲输出 |

## 模型说明

- **Device** (设备) - 环卫设备基本信息和状态
- **SensorData** (传感器数据) - 温度、振动、电流等实时数据
- **Alert** (告警) - 设备告警记录
- **AlertRule** (告警规则) - 告警触发条件

## 常见错误

### 端口被占用

```bash
# Windows: 检查占用
netstat -ano | findstr :5432
# 修改docker-compose.yml中的端口映射
```

### 数据库连接失败

```bash
# 检查PostgreSQL日志
make logs

# 运行诊断
python diagnose.py

# 重置数据库
docker-compose down -v
make up
make migrate
```

### 测试失败

```bash
# 运行单个测试
pytest app/tests/test_devices.py::TestCreateDevice::test_create_device_success -xvs

# 检查覆盖率
pytest --cov=app --cov-report=html
```

## 开发指南

### 添加新API

1. 在 `app/api/v1/` 创建路由文件
2. 在 `app/main.py` 注册路由
3. 在 `app/tests/` 添加测试

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 技术栈

- **FastAPI** - Web框架
- **SQLModel** - ORM
- **PostgreSQL** - 数据库
- **Redis** - 缓存
- **Alembic** - 数据库迁移
- **pytest** - 测试框架

## License

MIT
