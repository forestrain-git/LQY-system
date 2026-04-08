# 部署指南 / Deployment Guide

**项目**: 龙泉驿环卫智能体  
**版本**: 1.0.0  
**日期**: 2026-04-07  

---

## 📋 环境要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **磁盘**: 20GB 可用空间
- **网络**: 互联网连接(用于AI功能)

### 推荐配置
- **CPU**: 4核心+
- **内存**: 8GB RAM+
- **磁盘**: 50GB SSD
- **网络**: 稳定互联网连接

### 依赖软件
- Docker 20.10+ & Docker Compose 2.0+
- 或 Python 3.10+ & Node.js 18+

---

## 🐳 Docker部署 (推荐)

### 1. 克隆代码

```bash
git clone <repository-url>
cd lqy-system
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件:

```env
# 数据库
POSTGRES_USER=lqy_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=lqy_db
DATABASE_URL=postgresql+asyncpg://lqy_user:your_secure_password@db:5432/lqy_db

# Redis
REDIS_URL=redis://redis:6379/0

# 安全
SECRET_KEY=your_random_secret_key_here

# AI (可选，不配置则AI功能不可用)
KIMI_API_KEY=your_kimi_api_key
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 运行数据库迁移

```bash
docker-compose exec backend alembic upgrade head
```

### 5. 访问服务

- 前端: http://localhost
- API: http://localhost/api/v1
- API文档: http://localhost/docs

---

## 🔧 手动部署

### 后端部署

#### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 配置数据库连接
```

#### 4. 运行迁移

```bash
alembic upgrade head
```

#### 5. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端部署

#### 1. 安装依赖

```bash
cd frontend
npm install
```

#### 2. 配置API地址

编辑 `.env.production`:

```env
VITE_API_BASE_URL=/api/v1
```

#### 3. 构建

```bash
npm run build
```

#### 4. 部署

将 `dist/` 目录内容部署到Web服务器(Nginx/Apache)。

---

## 🗄️ 数据库设置

### PostgreSQL

```bash
# 创建数据库
createdb lqy_db

# 创建用户
createuser -P lqy_user

# 授予权限
psql -d lqy_db -c "GRANT ALL PRIVILEGES ON DATABASE lqy_db TO lqy_user;"
```

### Redis

```bash
# 启动Redis
redis-server

# 或使用Docker
docker run -d -p 6379:6379 redis:7-alpine
```

---

## 🔒 安全配置

### 1. 修改默认密钥

```bash
# 生成随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

将生成的密钥设置到 `.env` 的 `SECRET_KEY`。

### 2. 配置HTTPS

使用Nginx作为反向代理:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 防火墙配置

```bash
# 开放端口
ufw allow 80
ufw allow 443
ufw allow 8000  # 开发环境
```

---

## 🔍 验证部署

### 1. 健康检查

```bash
curl http://localhost/health
```

应返回:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### 2. API测试

```bash
# 获取车辆列表
curl http://localhost/api/v1/dispatch/vehicles

# 创建测试告警
curl -X POST http://localhost/api/v1/safety/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "fence_violation",
    "level": "warning",
    "title": "测试告警",
    "location": "测试区域"
  }'
```

### 3. 前端检查

访问 http://localhost 应该能看到登录页面。

---

## 📊 监控

### 日志查看

```bash
# Docker方式
docker-compose logs -f backend
docker-compose logs -f frontend

# 手动方式
tail -f backend/logs/app.log
tail -f /var/log/nginx/access.log
```

### 性能监控

```bash
# 查看资源使用
docker stats

# 或
top
htop
```

---

## 🔄 更新部署

### 更新代码

```bash
git pull origin main
```

### 更新依赖

```bash
# 后端
pip install -r requirements.txt --upgrade

# 前端
npm install
```

### 运行迁移

```bash
alembic upgrade head
```

### 重启服务

```bash
# Docker
docker-compose restart

# 手动
# 停止旧进程，启动新进程
```

---

## 🆘 故障排查

### 问题1: 数据库连接失败

**症状**: 后端启动报错 `Connection refused`

**解决**:
1. 检查PostgreSQL是否运行: `docker-compose ps`
2. 检查连接字符串: `DATABASE_URL`
3. 检查网络连接: `docker network ls`

### 问题2: 前端无法连接API

**症状**: 页面显示 "Network Error"

**解决**:
1. 检查后端是否运行: `curl http://localhost:8000/health`
2. 检查前端API配置: `frontend/.env`
3. 检查跨域设置: `app/main.py` CORS配置

### 问题3: AI功能不可用

**症状**: AI对话返回错误

**解决**:
1. 检查 `KIMI_API_KEY` 是否配置
2. 验证API Key有效性
3. 检查网络连接

### 问题4: 迁移失败

**症状**: `alembic upgrade head` 报错

**解决**:
1. 检查数据库是否存在
2. 检查用户权限
3. 手动执行: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`

---

## 📞 支持

遇到问题?

1. 查看 [TECH_DEBT.md](./TECH_DEBT.md)
2. 查看 [SPRINT_SUMMARY.md](./SPRINT_SUMMARY.md)
3. 提交Issue到项目仓库

---

*部署指南版本: 1.0.0*  
*最后更新: 2026-04-07*
