# Day5 测试指南

## 1. 后端启动步骤

```bash
cd /mnt/c/users/administrator/projects/lqy-system/backend

# 创建虚拟环境
python -m venv venv

# 激活（Windows）
venv\Scripts\activate

# 激活（Linux/Mac）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

## 2. 测试 MQTT 集成

后端已包含完整 MQTT 服务：

- **文件**: `app/services/mqtt_service.py`
- **Broker**: EMQX (localhost:1883)
- **主题**: `sensors/+/data`
- **功能**: 
  - 接收设备传感器数据
  - 自动保存到 PostgreSQL
  - 发布到 Redis 供 WebSocket 推送

### 测试数据格式

```json
{
  "device_id": "DEV001",
  "temperature": 65.5,
  "vibration": 3.2,
  "current": 15.1,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 3. 前端连接后端

修改 `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## 4. 验证功能

- [ ] Dashboard 实时数据更新
- [ ] WebSocket 连接状态显示
- [ ] 告警自动检测和推送
- [ ] 设备数据历史记录

## 5. 后端架构

```
┌─────────────┐     ┌──────────┐     ┌──────────┐
│   Device    │────▶│  MQTT    │────▶│PostgreSQL│
│  Simulator  │     │  Broker  │     │          │
└─────────────┘     └──────────┘     └──────────┘
                           │                │
                           ▼                ▼
                    ┌──────────┐     ┌──────────┐
                    │  Redis   │◀────│  FastAPI │
                    │  Pub/Sub │     │  Backend │
                    └──────────┘     └──────────┘
                           │                │
                           ▼                ▼
                    ┌──────────┐     ┌──────────┐
                    │WebSocket │────▶│  Frontend│
                    │  Manager │     │   Vue3   │
                    └──────────┘     └──────────┘
```

## 6. 关键配置

### EMQX (MQTT Broker)
- 端口: 1883 (MQTT), 18083 (Dashboard)
- 无需认证（开发环境）

### PostgreSQL
- 端口: 5432
- 数据库: sanitation_db
- 自动建表（SQLModel）

### Redis
- 端口: 6379
- 用于实时数据缓存和 WebSocket 广播

## 7. 测试端点

```bash
# 健康检查
curl http://localhost:8000/health

# 获取设备列表
curl http://localhost:8000/api/v1/devices

# 获取实时数据
curl http://localhost:8000/api/v1/sensor-data/latest
```

## 8. 查看日志

后端日志会显示：
- MQTT 连接状态
- 接收到的传感器数据
- 告警检测触发
- WebSocket 客户端连接

启动后能看到类似输出：
```
INFO - MQTT服务已启动
INFO - 已连接到MQTT Broker: localhost:1883
INFO - 已订阅主题: sensors/+/data
INFO - 自动创建设备: DEV001
INFO - 保存传感器数据: Device DEV001, Temp: 65.5°C
```
