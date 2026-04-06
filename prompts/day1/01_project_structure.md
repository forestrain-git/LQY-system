# Day 1 - Prompt 1: 项目结构生成

**时机**：环境检查通过后执行
**预期耗时**：Claude生成5-10分钟，你Review 5分钟
**人工决策**：确认目录结构后继续

---

## 输入Prompt

```text
请创建FastAPI项目结构到 backend/ 目录。

【硬性要求】
1. Python 3.10+，使用async/await
2. 数据库：PostgreSQL 14+，只用单库（不要TimescaleDB）
3. ORM：SQLModel 0.0.14+
4. 缓存：Redis 7+
5. 配置：pydantic-settings，支持.env文件

【目录结构】
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # 入口，包含lifespan管理
│   ├── config.py            # 配置类
│   ├── database.py          # 数据库连接
│   ├── redis.py             # Redis连接
│   ├── models/              # SQLModel模型（空文件，Prompt 2填充）
│   ├── schemas/             # Pydantic Schema（空文件，Prompt 2填充）
│   ├── api/v1/              # API路由（空文件，Prompt 3填充）
│   ├── services/            # 业务逻辑（空文件）
│   └── tests/               # 单元测试（空文件，Prompt 3填充）
├── alembic/                 # 数据库迁移（初始化配置）
├── docker-compose.yml       # 完整配置
├── Dockerfile
├── requirements.txt         # 所有依赖
└── pytest.ini

【关键文件内容要求】

1. requirements.txt
- fastapi>=0.104.0
- uvicorn[standard]>=0.24.0
- sqlalchemy[asyncio]>=2.0.0
- sqlmodel>=0.0.14
- asyncpg>=0.29.0
- redis>=5.0.0
- pydantic-settings>=2.0.0
- alembic>=1.12.0
- pytest>=7.4.0
- pytest-asyncio>=0.21.0
- pytest-cov>=4.1.0
- httpx>=0.25.0

2. docker-compose.yml
- PostgreSQL：端口5432，数据库lqy_db，用户postgres/密码postgres
- Redis：端口6379，无密码
- 后端：端口8000，健康检查依赖PostgreSQL和Redis
- 包含健康检查配置

3. config.py
- 使用pydantic-settings
- 从环境变量读取DATABASE_URL和REDIS_URL
- 包含默认配置

4. main.py
- 包含lifespan管理（启动时连接DB，关闭时断开）
- 包含/health端点，返回{status: ok, version: 0.1.0}
- 包含/docs端点（Swagger自动）

【容错设计】
- 数据库连接失败时，后端应重试3次后退出
- Redis连接失败时，后端应能启动但打印警告
- 所有配置有默认值，不配置也能跑

【备选方案】
如果Docker Compose配置复杂，先提供能本地运行的版本，Docker作为Bonus。

请生成所有文件，每生成一个主要文件告诉我进度。生成完成后，输出文件树结构。
```

---

## 预期输出

```
生成进度：
- requirements.txt [完成]
- docker-compose.yml [完成]
- Dockerfile [完成]
- app/config.py [完成]
- app/database.py [完成]
- app/redis.py [完成]
- app/main.py [完成]
- alembic配置 [完成]
- 空目录结构 [完成]

文件树：
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ...

下一步：请确认结构OK，然后继续Prompt 2（模型生成）
```

---

## 你的决策

- [ ] 结构OK → 继续Prompt 2
- [ ] 需要调整 → 告诉Claude修改哪里
- [ ] 想先本地测试 → 执行`cd backend && pip install -r requirements.txt && python -c "from app.main import app; print('OK')"`
