# 设备数据模拟器

模拟多台环卫设备发送传感器数据到MQTT Broker。

## 功能特性

- **多设备模拟**: 同时模拟多台虚拟设备
- **异常模拟**: 自动触发温度/振动/电流异常
- **可配置参数**: 设备数量、数据频率、异常概率
- **数据验证**: 内置数据流验证脚本

## 快速开始

```bash
cd simulator
python device_simulator.py
```

## 命令行参数

```bash
python device_simulator.py --broker localhost --port 1883 --count 10
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--broker` | localhost | MQTT Broker地址 |
| `--port` | 1883 | MQTT端口 |
| `--count` | 10 | 设备数量 |

## 数据格式

```json
{
  "device_id": "DEV001",
  "temperature": 52.3,
  "vibration": 1.2,
  "current": 10.5,
  "timestamp": "2025-01-01T12:00:00+00:00",
  "anomaly": false
}
```

## 异常模拟规则

- **异常概率**: DEV001/DEV002为15%，其他设备5%
- **异常持续**: 3-6个数据周期
- **异常表现**:
  - 温度: +20~30°C
  - 振动: +3~8 mm/s
  - 电流: +5~10 A

## 数据流验证

```bash
# 终端1: 启动模拟器
python device_simulator.py

# 终端2: 运行验证（需先启动后端服务）
python check_data_flow.py
```

验证脚本会检查:
- MQTT Broker连接
- 后端API状态
- WebSocket连接
- 数据接收统计
- 异常事件检测

## 依赖安装

```bash
pip install -r requirements.txt
```

## 完整测试流程

```bash
# 1. 启动基础设施
cd backend
make up

# 2. 启动模拟器（新终端）
cd simulator
python device_simulator.py

# 3. 运行验证（新终端）
python check_data_flow.py

# 4. 查看EMQX Dashboard
open http://localhost:18083
# 用户名: admin, 密码: public
```
