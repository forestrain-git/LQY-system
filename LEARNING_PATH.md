# 龙泉驿项目 - 新手快速学习路径

> **目标**：掌握项目最关键的20%内容，覆盖80%的实际开发需求
> 
> **学习方式**：边做边学，而非先学后做
> **时间投入**：每天2-3小时，预计5-7天可独立开发基础功能

---

## 第一阶段：地基搭建（第1-2天）—— 掌握核心30%

### 1. FastAPI 极简入门（3小时）

**只学这4个概念，其他的先跳过：**

```python
# 1. 创建路由（处理请求）
from fastapi import FastAPI
app = FastAPI()

@app.get("/hello")
async def hello():
    return {"message": "Hello"}  # 自动变成JSON

# 2. 请求/响应模型（数据验证）
from pydantic import BaseModel

class DeviceCreate(BaseModel):
    name: str
    location: str = None  # 可选字段
    
@app.post("/devices")
async def create_device(data: DeviceCreate):
    return {"id": 1, **data.dict()}

# 3. 依赖注入（复用代码，如数据库连接）
from fastapi import Depends

async def get_db():
    db = create_connection()
    try:
        yield db
    finally:
        db.close()

@app.get("/devices")
async def list_devices(db = Depends(get_db)):  # 自动注入
    return db.query(Device).all()

# 4. 异常处理
from fastapi import HTTPException

@app.get("/devices/{id}")
async def get_device(id: int):
    device = find_device(id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device
```

**实战任务**：
- [ ] 创建一个最简单的设备CRUD API（30分钟）
- [ ] 用Postman/浏览器测试这4个接口（15分钟）
- [ ] 反复修改请求模型，观察自动验证效果（15分钟）

### 2. SQLModel 数据库操作（2小时）

**只学这3个模式：**

```python
# 模式1：定义模型（= 数据表）
from sqlmodel import SQLModel, Field

class Device(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    status: str = "offline"  # 默认值

# 模式2：基本CRUD
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

# 创建
async def create_device(db: AsyncSession, device: Device):
    db.add(device)
    await db.commit()
    await db.refresh(device)  # 获取生成的id
    return device

# 查询（列表 + 单条）
async def get_devices(db: AsyncSession):
    result = await db.execute(select(Device))
    return result.scalars().all()

async def get_device(db: AsyncSession, device_id: int):
    result = await db.execute(select(Device).where(Device.id == device_id))
    return result.scalar_one_or_none()

# 模式3：简单过滤
async def get_online_devices(db: AsyncSession):
    result = await db.execute(
        select(Device).where(Device.status == "online")
    )
    return result.scalars().all()
```

**实战任务**：
- [ ] 创建2个模型：Device 和 SensorData（30分钟）
- [ ] 实现这3个模型的完整CRUD（45分钟）
- [ ] 练习3种不同的where过滤条件（15分钟）

### 3. 异步编程极简版（1小时）

**只理解这个概念：**

```python
# 普通函数（同步）
def normal_function():
    data = fetch_data()  # 等待3秒，CPU干等着
    return data

# 异步函数（非阻塞）
async def async_function():
    data = await fetch_data()  # 等待时CPU可以干别的
    return data

# 项目中只有3个地方需要async：
# 1. 路由处理函数
# 2. 数据库操作
# 3. 外部API调用（MQTT/Redis）
```

**口诀**：
- 定义异步函数用 `async def`
- 调用异步函数用 `await`
- FastAPI路由自动处理异步，你只管写就行

---

## 第二阶段：IoT核心（第3-4天）—— 掌握关键40%

### 4. MQTT 通信机制（2小时）

**只理解这个流程：**

```
设备 --(MQTT)--> EMQX Broker --(Python订阅)--> FastAPI处理 --> 数据库
```

**核心代码模式（照抄即可）：**

```python
import aiomqtt

class MQTTService:
    def __init__(self):
        self.client = None
        
    async def start(self):
        # 1. 连接到MQTT Broker
        self.client = aiomqtt.Client(hostname="localhost", port=1883)
        
        async with self.client:
            # 2. 订阅主题（= 监听频道）
            await self.client.subscribe("sensors/+/data")
            
            # 3. 循环接收消息
            async for message in self.client.messages:
                await self.handle_message(message)
    
    async def handle_message(self, message):
        # 解析数据
        data = json.loads(message.payload)
        device_id = data["device_id"]
        temperature = data["temperature"]
        
        # 保存到数据库
        await save_sensor_data(device_id, temperature)
        
        # 检查是否需要告警
        if temperature > 80:
            await create_alert(device_id, "温度过高")

# 在FastAPI中启动
@app.on_event("startup")
async def startup():
    mqtt = MQTTService()
    asyncio.create_task(mqtt.start())
```

**实战任务**：
- [ ] 运行现有的device_simulator.py，观察MQTT消息（30分钟）
- [ ] 修改handle_message，添加一个自己的判断逻辑（30分钟）
- [ ] 实现一个简单命令下发（从后端发送给设备）（30分钟）

### 5. WebSocket 实时推送（2小时）

**只理解这个模式：**

```python
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
    
    async def broadcast(self, message: dict):
        """广播给所有连接的客户端"""
        for conn in self.connections:
            await conn.send_json(message)

manager = ConnectionManager()

# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接，接收客户端消息
            data = await websocket.receive_text()
    except:
        manager.connections.remove(websocket)

# 在MQTT收到数据时广播
async def handle_message(self, message):
    data = json.loads(message.payload)
    await manager.broadcast({
        "type": "sensor_data",
        "data": data
    })
```

**实战任务**：
- [ ] 用浏览器Console测试WebSocket连接（30分钟）
- [ ] 修改广播逻辑，只发送温度超过阈值的数据（30分钟）
- [ ] 实现一个简单的前端页面展示实时数据（1小时）

### 6. 数据模型关系（1小时）

**只学这2种关系：**

```python
# 一对多：一个设备有多条传感器数据
class Device(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    # 定义关系
    sensor_data: list["SensorData"] = Relationship(back_populates="device")

class SensorData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id")
    temperature: float
    # 反向关系
    device: Device = Relationship(back_populates="sensor_data")

# 查询时自动关联
async def get_device_with_data(db: AsyncSession, device_id: int):
    result = await db.execute(
        select(Device).where(Device.id == device_id)
        .options(selectinload(Device.sensor_data))  # 自动加载关联数据
    )
    return result.scalar_one()
# 结果：device.sensor_data 直接就是列表，不需要再查询
```

---

## 第三阶段：业务闭环（第5-6天）—— 掌握最后30%

### 7. 告警系统核心逻辑（2小时）

**告警检测 = 条件判断 + 重复抑制**

```python
# 1. 简单阈值检测
def check_threshold(value, threshold, operator="gt"):
    if operator == "gt" and value > threshold:
        return True
    if operator == "lt" and value < threshold:
        return True
    return False

# 2. Redis重复抑制（5分钟内不重复告警）
import redis

async def should_create_alert(device_id: str, metric: str) -> bool:
    key = f"alert:last:{device_id}:{metric}"
    last_time = redis.get(key)
    
    if last_time and time.now() - last_time < 300:  # 5分钟
        return False  # 不创建
    
    redis.setex(key, 300, time.now())  # 记录本次时间
    return True

# 3. 完整检测流程
async def process_sensor_data(data):
    # 检查阈值
    if data["temperature"] > 80:
        # 检查是否可以创建（非重复）
        if await should_create_alert(data["device_id"], "temperature"):
            await create_alert(
                device_id=data["device_id"],
                message=f"温度过高: {data['temperature']}℃",
                level="critical"
            )
            # 推送到前端
            await manager.broadcast({"type": "new_alert", ...})
```

### 8. 快速调试技巧（贯穿全程）

**必须掌握的5个命令：**

```bash
# 1. 查看后端日志（实时）
docker logs -f lqy_backend

# 2. 测试API（比Postman更快）
curl http://localhost:8000/api/v1/devices | jq

# 3. 直接查数据库
docker exec -it lqy_postgres psql -U postgres -d lqy_db -c "SELECT * FROM devices;"

# 4. 监控MQTT消息
docker exec -it lqy_emqx emqx_ctl pubsub sub sensors/+/data

# 5. 查看WebSocket连接状态
curl http://localhost:8000/health
```

**Python调试3法宝：**

```python
# 1. 打印变量（比print更强）
from pprint import pp
pp(complex_dict)

# 2. 断点调试
import pdb; pdb.set_trace()  # 运行到这会暂停，可以检查变量

# 3. 性能计时
import time
start = time.time()
# ... 你的代码
print(f"耗时: {time.time() - start:.3f}s")
```

---

## 实战项目：从0到可运行

**跟着这个项目练手（由简到繁）：**

### Level 1：极简设备管理（练基础API）
- 创建Device模型（id, name, status）
- 实现5个API：增删改查 + 列表
- 用curl或浏览器测试通过
- **目标**：熟悉FastAPI基本流程

### Level 2：传感器数据接入（练MQTT）
- 运行device_simulator产生数据
- 订阅MQTT主题，接收数据
- 保存到SensorData表
- 查询设备的最新数据
- **目标**：理解IoT数据流

### Level 3：实时展示（练WebSocket）
- 前端页面展示设备列表
- WebSocket接收实时数据
- 温度实时刷新
- **目标**：掌握实时通信

### Level 4：智能告警（练业务逻辑）
- 温度>75时生成告警
- 5分钟内不重复告警
- WebSocket推送告警
- 告警确认/解决功能
- **目标**：完整业务闭环

---

## 避坑指南（新手常见错误）

### ❌ 不要做的事

1. **不要先系统学Python**
   - 本项目用到的Python只是冰山一角
   - 用到什么查什么，边查边做

2. **不要深入SQLAlchemy高级特性**
   - 先用SQLModel（已封装好）
   - 复杂查询用原生SQL反而更简单

3. **不要研究MQTT协议细节**
   - 把它当成"黑盒子"：发布/订阅
   - 本项目用的aiomqtt已经很简单

4. **不要纠结异步原理**
   - 记住：路由用async def，数据库操作加await
   - 其他不用管，FastAPI帮你处理

### ✅ 应该做的事

1. **多改代码做实验**
   - 改个参数看效果
   - 故意写错看报错信息
   - 每次只改一处，观察变化

2. **善用自动生成的文档**
   - 启动后访问 http://localhost:8000/docs
   - 这里可以测试所有API，不用Postman

3. **复制现有代码改**
   - Day 1-2的代码已经是最佳实践
   - 复制过来改改就能用

4. **先跑通，再优化**
   - 第一版能工作就行
   - 性能、代码质量以后再说

---

## 学习检查清单

完成这些你就能独立开发80%的功能：

- [ ] 能独立创建1个CRUD API（从模型到路由）
- [ ] 能连接MQTT收发消息
- [ ] 能用WebSocket推送数据到浏览器
- [ ] 能实现简单的条件判断+数据存储
- [ ] 能调试问题（看日志、打断点）
- [ ] 能复制现有代码改成新功能

---

## 推荐学习资源（极简版）

**只读这3个，其他的先不要看：**

1. **FastAPI官方文档 - 教程部分**（前5节）
   - https://fastapi.tiangolo.com/tutorial/
   - 只看教程，不看高级用户指南

2. **SQLModel官方文档 - 基础部分**
   - https://sqlmodel.tiangolo.com/
   - 重点看"Hero"示例项目

3. **MQTT协议图解**（概念理解）
   - 搜"MQTT协议 图解"
   - 理解发布/订阅模式即可

**遇到问题：**
- 先问Claude："报错xxx是什么意思"
- 再问Claude："怎么实现xxx功能"
- 最后才查文档

---

## 总结：核心口诀

```
FastAPI三要素：路由 + 模型 + 依赖注入
数据库三操作：增（add）查（select）改（commit）
IoT两通道：MQTT收数据，WebSocket推前端
告警两步骤：条件判断 + 重复抑制
调试三法宝：打印、断点、看日志
```

**记住：完成比完美重要，先跑起来再优化！**
