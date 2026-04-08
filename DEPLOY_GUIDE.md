# 龙泉驿环卫智能体 - 部署指南

## 部署方式选择

### 方式一: Docker部署（推荐）
适用场景: 生产环境，需要完整的容器化支持

### 方式二: 原生部署
适用场景: 开发测试环境，快速启动

---

## 方式一: Docker部署

### 前提条件
- Docker >= 20.10
- Docker Compose >= 2.0

### 部署步骤

```bash
# 1. 克隆代码
git clone https://github.com/forestrain-git/LQY-system.git
cd LQY-system

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库密码和Kimi API Key

# 3. 启动服务
docker-compose up -d

# 4. 执行数据库迁移
docker-compose exec backend alembic upgrade head

# 5. 检查状态
docker-compose ps
```

### 访问地址
- 前端: http://localhost:8080
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- EMQX Dashboard: http://localhost:18085 (admin/public)

---

## 方式二: 原生部署

### 前提条件
- Python >= 3.11
- Node.js >= 18
- PostgreSQL >= 15
- Redis >= 7

### 部署步骤

#### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm postgresql redis-server

# CentOS/RHEL
sudo yum install -y python3 python3-pip nodejs npm postgresql-server redis
```

#### 2. 配置数据库

```bash
# 启动PostgreSQL
sudo systemctl start postgresql

# 创建数据库
sudo -u postgres psql -c "CREATE USER lqy_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE lqy_db OWNER lqy_user;"
```

#### 3. 配置Redis

```bash
# 启动Redis
sudo systemctl start redis
```

#### 4. 部署应用

```bash
# 克隆代码
git clone https://github.com/forestrain-git/LQY-system.git
cd LQY-system

# 使用部署脚本
chmod +x deploy-native.sh
./deploy-native.sh full-deploy
```

或者手动部署:

```bash
# 安装依赖
./deploy-native.sh install

# 执行迁移
./deploy-native.sh migrate

# 启动服务
./deploy-native.sh start
```

### 管理服务

```bash
# 查看状态
./deploy-native.sh status

# 健康检查
./deploy-native.sh health

# 查看日志
./deploy-native.sh logs

# 重启服务
./deploy-native.sh restart

# 停止服务
./deploy-native.sh stop
```

---

## 系统服务部署（生产环境）

### 1. 复制文件

```bash
# 复制项目到系统目录
sudo mkdir -p /opt/lqy-system
sudo cp -r . /opt/lqy-system/

# 创建用户
sudo useradd -r -s /bin/false lqy
sudo chown -R lqy:lqy /opt/lqy-system
```

### 2. 安装systemd服务

```bash
# 复制服务文件
sudo cp systemd/*.service /etc/systemd/system/

# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl enable lqy-backend lqy-frontend
sudo systemctl start lqy-backend lqy-frontend

# 查看状态
sudo systemctl status lqy-backend
sudo systemctl status lqy-frontend
```

---

## 配置说明

### 环境变量 (.env)

```bash
# 数据库配置
POSTGRES_USER=lqy_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=lqy_db
DATABASE_URL=postgresql+asyncpg://lqy_user:your_secure_password@localhost:5432/lqy_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# MQTT配置
MQTT_BROKER=localhost
MQTT_PORT=1883

# 安全配置
SECRET_KEY=your-super-secret-key-change-in-production

# AI配置
KIMI_API_KEY=sk-kimi-your-api-key-here

# 应用配置
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Nginx反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 验证部署

### 1. 服务状态检查

```bash
# Docker方式
docker-compose ps

# 原生方式
./deploy-native.sh status
```

### 2. API健康检查

```bash
# 检查后端API
curl http://localhost:8000/health

# 预期响应
{
  "status": "ok",
  "version": "1.0.0"
}
```

### 3. 前端访问

打开浏览器访问: http://localhost:8080

### 4. 登录测试

使用默认账号测试:
- 用户名: admin
- 密码: admin123

---

## 故障排查

### 问题1: 数据库连接失败

```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 检查数据库是否存在
sudo -u postgres psql -l

# 查看后端日志
tail -f logs/backend.log
```

### 问题2: 后端服务无法启动

```bash
# 检查依赖
pip install -r requirements.txt

# 检查端口占用
lsof -i :8000

# 手动启动查看错误
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 问题3: 前端构建失败

```bash
# 清理缓存
rm -rf node_modules
npm install

# 重新构建
npm run build
```

### 问题4: 端口冲突

修改 `.env` 文件:
```bash
# 修改后端端口
BACKEND_PORT=8001

# 修改前端端口
FRONTEND_PORT=8081
```

---

## 性能优化

### 后端优化

```bash
# 增加工作进程数
uvicorn app.main:app --workers 4

# 使用gunicorn + uvicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### 前端优化

```bash
# 构建优化
npm run build -- --mode production

# 启用gzip
# nginx配置中添加:
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_safety_alerts_status ON safety_alerts(status);
CREATE INDEX idx_work_orders_status ON work_orders(status);

-- 分析表
ANALYZE;
```

---

## 安全建议

### 1. 修改默认密码

立即修改默认账号密码:
- admin / admin123
- operator / operator123

### 2. 配置HTTPS

使用Let's Encrypt获取免费证书:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 防火墙配置

```bash
# 仅开放必要端口
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. 定期备份

```bash
# 数据库备份
pg_dump -U lqy_user lqy_db > backup_$(date +%Y%m%d).sql

# 文件备份
tar -czf backup_files_$(date +%Y%m%d).tar.gz /opt/lqy-system
```

---

## 监控与维护

### 日志监控

```bash
# 实时日志
tail -f logs/backend.log

# 错误统计
grep "ERROR" logs/backend.log | wc -l
```

### 性能监控

```bash
# 查看资源使用
top -p $(pgrep -d',' uvicorn)

# 查看数据库连接
ps aux | grep postgres | wc -l
```

### 定期维护

```bash
# 清理日志
find logs/ -name "*.log" -mtime +30 -delete

# 更新依赖
pip list --outdated
npm outdated
```

---

## 升级指南

### 代码更新

```bash
# 拉取最新代码
git pull origin main

# 安装新依赖
./deploy-native.sh install

# 执行迁移
./deploy-native.sh migrate

# 重启服务
./deploy-native.sh restart
```

### 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 支持

遇到问题？

1. 查看日志: `./deploy-native.sh logs`
2. 健康检查: `./deploy-native.sh health`
3. 查看文档: `README.md`

---

*部署版本: v1.0.1*  
*最后更新: 2026-04-08*
