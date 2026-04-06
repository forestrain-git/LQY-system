# 龙泉驿环卫智能体 - 7天AI密集编程冲刺计划

**目标**：验证AI编程能力边界，输出可运行的全栈POC系统
**原则**：99%代码由Claude Code生成，人工只做关键决策
**人员**：1人 + Claude Code
**交付**：设备监控+AI异常检测+预测预警的完整系统

---

## 前置准备（冲刺前完成）

```bash
# 1. 创建GitHub仓库
gh repo create lqy-system-poc --public --clone
cd lqy-system-poc

# 2. 初始化目录结构
mkdir -p backend frontend simulator docs

# 3. Claude Code配置检查
claude config get git.enabled
```

---

## Day 1：后端骨架（周一）

**目标**：FastAPI + PostgreSQL + Redis 能跑起来
**核心交付**：`docker-compose up` 一键启动完整后端

### 上午（3小时）

#### Step 1：项目结构（Claude生成）
**Prompt**：
```
请帮我创建一个FastAPI项目结构到 backend/ 目录：

1. 使用SQLModel作为ORM
2. PostgreSQL数据库连接，支持异步
3. Redis缓存支持（aioredis）
4. 项目结构按领域划分：
   - device/ - 设备管理
   - sensor/ - 传感器数据
   - alert/ - 告警管理
   - common/ - 公共组件
5. 包含完整的Docker Compose配置（PostgreSQL+Redis+后端）
6. 配置文件使用pydantic-settings
7. 包含健康检查端点 /health
8. 包含requirements.txt

请生成所有必要文件，确保docker-compose up能直接启动。
```

**人工决策点**：
- 确认技术栈选择（FastAPI+SQLModel vs Django）
- 确认目录结构是否清晰
- 确认Docker配置是否合理

#### Step 2：数据库模型（Claude生成）
**Prompt**：
```
请在 backend/app/models/ 下创建以下SQLModel模型：

1. Device（设备）
   - id: int, PK
   - name: str, 设备名称
   - type: str, 设备类型（compressor/pump/fan等）
   - location: str, 位置描述
   - status: str, 状态（online/offline/maintenance）
   - created_at: datetime
   - updated_at: datetime

2. SensorData（传感器数据）
   - id: int, PK
   - device_id: int, FK
   - temperature: float, 温度（℃）
   - vibration: float, 振动（mm/s）
   - current: float, 电流（A）
   - timestamp: datetime, 数据时间

3. Alert（告警）
   - id: int, PK
   - device_id: int, FK
   - alert_type: str, 告警类型（threshold/trend/prediction）
   - metric: str, 指标（temperature/vibration/current）
   - message: str, 告警描述
   - level: str, 级别（critical/warning/info）
   - status: str, 状态（active/acknowledged/resolved）
   - created_at: datetime
   - acknowledged_at: datetime, optional

4. AlertRule（告警规则）
   - id: int, PK
   - device_id: int, FK, nullable（null表示所有设备）
   - metric: str, 监控指标
   - operator: str, 操作符（gt/lt/eq）
   - threshold: float, 阈值
   - enabled: bool, 是否启用
   - description: str, 规则描述

要求：
- 包含表关系（Relationship）
- 包含Pydantic Schema（Create/Update/Response）
- 包含数据库迁移脚本（ Alembic ）
- 模型字段有中文注释
```

**人工决策点**：
- 确认字段是否完整
- 确认告警级别定义
- 确认是否需要软删除

### 下午（3小时）

#### Step 3：基础API（Claude生成）
**Prompt**：
```
请为Device和SensorData创建完整的RESTful API：

Device API：
- GET /api/v1/devices - 设备列表（分页、支持按状态筛选）
- GET /api/v1/devices/{id} - 设备详情（包含最近一条传感器数据）
- POST /api/v1/devices - 创建设备
- PUT /api/v1/devices/{id} - 更新设备
- DELETE /api/v1/devices/{id} - 删除设备（软删除）
- GET /api/v1/devices/{id}/data - 设备历史数据（分页、时间范围筛选）
- GET /api/v1/devices/{id}/latest - 最新一条数据
- GET /api/v1/devices/{id}/stats - 设备统计（今日数据条数、平均值等）

SensorData API：
- POST /api/v1/sensor-data - 接收传感器数据（供MQTT服务调用）
- GET /api/v1/sensor-data/export - 导出数据（CSV格式）

要求：
- 使用依赖注入
- 统一的API响应格式（code/message/data）
- 完整的错误处理
- 异步数据库操作
- OpenAPI文档自动生成
```

**人工决策点**：
- 确认API路径规范
- 确认分页参数（page/size vs limit/offset）
- 确认响应格式标准

#### Step 4：测试启动（人工执行）
```bash
cd backend
docker-compose up -d
# 检查容器状态
docker ps
# 测试API
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

**人工决策点**：
- 如果启动失败，看日志决定回退还是修复
- 确认Swagger UI是否正常

### 晚上（2小时）

#### Step 5：代码Review（Claude辅助）
**Prompt**：
```
请Review今天的代码：

1. 检查是否有明显的安全漏洞（SQL注入、未验证输入等）
2. 检查是否有内存泄漏或连接未关闭问题
3. 检查代码风格是否一致
4. 指出需要改进的地方
5. 给代码质量打分（1-10）
```

**人工决策点**：
- 决定是否采纳改进建议
- 判断是否要继续优化还是继续Day 2

#### Step 6：Git提交
```bash
git add .
git commit -m "Day 1: Backend skeleton with models and basic APIs

- FastAPI + SQLModel + PostgreSQL + Redis
- Device/SensorData/Alert/AlertRule models
- CRUD APIs with pagination and filtering
- Docker Compose setup
- Health check and OpenAPI docs

co-authored-by: Claude Code"
```

### Day 1验收标准
- [ ] `docker-compose up -d` 成功启动所有服务
- [ ] `curl http://localhost:8000/health` 返回200
- [ ] Swagger UI (`/docs`) 能看到所有API
- [ ] 能用curl创建设备和查询列表
- [ ] 代码已提交GitHub

### Day 1风险预案
| 风险 | 应对 |
|------|------|
| Docker启动失败 | 检查端口占用，修改docker-compose.yml端口映射 |
| 数据库连接失败 | 检查网络配置，确认容器间能通信 |
| API测试失败 | 看日志定位，让Claude修复 |

---

## Day 2：数据流（周二）

**目标**：模拟设备 → MQTT → 后端 → 数据库 → WebSocket
**核心交付**：数据能完整流动，WebSocket客户端能收到实时数据

### 上午（3小时）

#### Step 1：MQTT接入（Claude生成）
**Prompt**：
```
请在 backend/app/services/ 下创建 mqtt_service.py：

功能：
1. 使用 aiomqtt 异步MQTT客户端
2. 连接到本地的EMQX（mqtt://localhost:1883）
3. 订阅主题：sensors/+/data（+表示所有设备ID）
4. 接收到消息后：
   - 解析JSON数据
   - 验证数据格式
   - 写入SensorData表
   - 发布到Redis Channel: device:{device_id}:data
   - 调用告警检测服务（先留空接口）
5. 处理连接断开自动重连
6. 优雅关闭（程序退出时断开连接）

在 main.py 中启动MQTT服务（ lifespan 管理）。

同时创建 EMQX 的docker-compose配置。
```

**人工决策点**：
- 确认MQTT broker选择（EMQX vs Mosquitto）
- 确认主题命名规范
- 确认Redis Channel命名

#### Step 2：WebSocket服务（Claude生成）
**Prompt**：
```
请在 backend/app/api/ 下创建 websocket.py：

功能：
1. 使用FastAPI原生WebSocket
2. 两个端点：
   - /ws/devices - 推送所有设备最新数据
   - /ws/devices/{device_id} - 推送单个设备数据
3. 连接管理：
   - 维护活跃连接列表
   - 处理连接/断开事件
   - 异常处理（客户端突然断开）
4. 数据推送：
   - 从Redis订阅Channel
   - 收到数据后推送给相关WebSocket连接
   - 支持心跳检测（ping/pong）
5. 性能考虑：
   - 使用后台任务处理Redis订阅
   - 连接数限制（防止内存溢出）

包含完整的连接示例代码（供前端参考）。
```

**人工决策点**：
- 确认WebSocket路径设计
- 确认连接数上限
- 确认心跳机制

### 下午（3小时）

#### Step 3：设备模拟器（Claude生成）
**Prompt**：
```
请在 simulator/ 目录下创建 device_simulator.py：

功能：
1. 模拟10台设备（DEV001-DEV010）
2. 每台设备每2秒发送一次数据到MQTT
3. 数据格式：
   {
     "device_id": "DEV001",
     "temperature": 45.2,  // 正常范围40-60，偶尔70-80
     "vibration": 0.5,     // 正常范围0.1-2.0，偶尔5.0+
     "current": 10.5,      // 正常范围5-15，偶尔20+
     "timestamp": "2026-04-06T10:00:00Z"
   }
4. 数据生成逻辑：
   - 基础值+随机波动
   - 每5分钟有一次异常峰值（模拟故障前兆）
   - DEV001和DEV002更容易异常（用于测试）
5. 可配置：
   - 设备数量
   - 发送间隔
   - MQTT broker地址
6. 包含命令行参数解析（argparse）
7. 包含启动日志

创建 requirements.txt 和 Dockerfile。
```

**人工决策点**：
- 确认设备数量和数据频率
- 确认异常数据生成策略
- 确认时间戳格式

#### Step 4：联调测试（人工执行）
```bash
# 终端1：启动后端
cd backend && docker-compose up -d

# 终端2：启动模拟器
cd simulator && python device_simulator.py --count 10 --interval 2

# 终端3：检查数据流入
cd backend && docker-compose exec postgres psql -U postgres -d lqy_db -c "SELECT COUNT(*) FROM sensordata;"

# 终端4：测试WebSocket
# 用wscat或浏览器控制台：
# var ws = new WebSocket('ws://localhost:8000/ws/devices');
# ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

**人工决策点**：
- 如果数据没流入，检查MQTT连接
- 如果WebSocket没数据，检查Redis Channel
- 决定是否要加调试日志

### 晚上（2小时）

#### Step 5：数据验证（Claude辅助）
**Prompt**：
```
请帮我写数据验证脚本 check_data_flow.py：

功能：
1. 检查MQTT broker是否可连接
2. 检查后端是否正常接收数据（查询数据库最近1分钟的数据条数）
3. 检查Redis是否正常（发布测试消息，验证订阅）
4. 检查WebSocket服务是否正常
5. 输出完整的系统状态报告

如果发现问题，给出可能的解决方案。
```

**人工决策点**：
- 根据验证结果决定是否结束Day 2
- 如有问题，决定是否修复或记录为技术债

#### Step 6：Git提交
```bash
git add .
git commit -m "Day 2: Data flow complete - MQTT + WebSocket

- MQTT service for device data ingestion
- WebSocket for real-time data push
- Device simulator with 10 virtual devices
- Data validation scripts
- EMQX broker integration

co-authored-by: Claude Code"
```

### Day 2验收标准
- [ ] 运行模拟器后，数据库不断有数据写入（每秒5条）
- [ ] 查询API能返回历史数据
- [ ] WebSocket客户端能收到实时JSON数据
- [ ] 系统运行10分钟无内存泄漏
- [ ] 代码已提交GitHub

### Day 2风险预案
| 风险 | 应对 |
|------|------|
| MQTT连接不稳定 | 改用HTTP POST作为备选方案 |
| WebSocket性能差 | 添加数据采样（每5秒推送一次） |
| 数据格式不一致 | 添加严格的Pydantic验证 |

---

## Day 3：告警引擎（周三）

**目标**：异常检测 + 告警生成 + WebSocket推送
**核心交付**：模拟器异常数据能触发告警，前端能看到

### 上午（3小时）

#### Step 1：告警检测服务（Claude生成）
**Prompt**：
```
请在 backend/app/services/ 下创建 alert_service.py：

功能1：阈值检测（实时）
- 温度 > 75℃：Critical告警
- 温度 > 60℃：Warning告警
- 振动 > 5.0mm/s：Warning告警
- 电流 > 20A：Critical告警

功能2：趋势检测（每分钟扫描）
- 连续5个数据点温度上升且总上升>10℃：Warning告警
- 温度在10分钟内从正常升至>70℃：Critical告警

功能3：告警管理
- 同一设备同一指标5分钟内不重复告警
- 告警升级（Warning持续30分钟变Critical）
- 告警恢复检测（数值回到正常范围）

功能4：通知推送
- WebSocket推送告警消息
- 保存到Alert表
- 打印日志

要求：
- 异步执行，不阻塞主流程
- 支持从数据库读取AlertRule动态配置
- 包含单元测试
```

**人工决策点**：
- 确认告警阈值是否合理
- 确认防重复机制
- 确认是否支持规则动态配置

#### Step 2：告警API（Claude生成）
**Prompt**：
```
请创建完整的告警管理API（/api/v1/alerts）：

1. GET /alerts - 告警列表
   - 分页
   - 筛选：level、status、device_id、时间范围
   - 排序：created_at desc

2. GET /alerts/stats - 告警统计
   - 今日告警总数
   - 各级别数量
   - 各设备告警数量
   - 未处理告警数量

3. GET /alerts/{id} - 告警详情

4. POST /alerts/{id}/acknowledge - 确认告警
   - 更新status为acknowledged
   - 记录acknowledged_at和acknowledged_by

5. POST /alerts/{id}/resolve - 解决告警
   - 更新status为resolved

6. DELETE /alerts/{id} - 删除告警（管理员）

7. GET /alerts/active - 当前活跃告警（WebSocket订阅用）

要求：
- 包含权限检查（简单版：只有管理员能删除）
- 响应包含设备名称（Join查询）
- OpenAPI文档完整
```

### 下午（3小时）

#### Step 3：告警规则管理（Claude生成）
**Prompt**：
```
请创建告警规则管理API（/api/v1/alert-rules）：

1. CRUD完整接口
2. 支持启用/禁用规则
3. 支持按设备配置或全局配置
4. 规则字段：
   - metric: temperature/vibration/current
   - operator: gt(greater than)/lt(less than)/eq(equal)
   - threshold: float
   - duration: 持续多少秒才触发（防抖动）
5. 规则变化实时生效（无需重启服务）

前端管理页面：规则列表、添加/编辑规则、启用/禁用开关
```

#### Step 4：告警WebSocket（Claude生成）
**Prompt**：
```
扩展WebSocket服务，添加告警推送：

1. 新告警产生时，推送给所有连接
2. 告警状态变化时（acknowledged/resolved），推送更新
3. 消息格式：
   {
     "type": "alert/new" | "alert/update",
     "data": {告警对象}
   }
4. 支持按级别过滤订阅（可选）
```

### 晚上（2小时）

测试与提交。

### Day 3验收标准
- [ ] 模拟器产生异常数据时，3秒内生成告警
- [ ] 告警写入数据库，WebSocket推送成功
- [ ] 告警API能正常查询和确认
- [ ] 规则启用/禁用实时生效

---

## Day 4：前端看板（周四）

**目标**：Vue3 + ECharts 实时看板
**核心交付**：浏览器能看到实时跳动的图表和告警

### 上午（3小时）

#### Step 1：前端项目初始化（Claude生成）
**Prompt**：
```
请在 frontend/ 目录下创建Vue3项目：

技术栈：
- Vite（构建工具）
- Vue 3.4+（Composition API + <script setup>）
- TypeScript
- Element Plus（UI组件库）
- ECharts 5（图表库）
- Pinia（状态管理）
- Vue Router 4
- Axios（HTTP客户端）

项目结构：
- src/
  - api/ - API接口封装
  - components/ - 公共组件
  - views/ - 页面
  - stores/ - Pinia状态
  - utils/ - 工具函数
  - types/ - TypeScript类型

包含：
- 环境配置文件（.env.development/.env.production）
- Axios封装（拦截器、错误处理）
- 路由配置
- Pinia Store示例
- Dockerfile

确保：npm run dev 能正常启动
```

#### Step 2：布局框架（Claude生成）
**Prompt**：
```
请创建主布局组件：

1. 左侧导航栏：
   - 仪表盘
   - 设备管理
   - 告警中心
   - 系统设置
   - 支持折叠/展开

2. 顶部Header：
   - 系统名称：龙泉驿环卫智能体POC
   - 当前时间（实时更新）
   - 告警数量Badge（红色，实时更新）
   - 用户头像（占位）

3. 主内容区域：
   - 面包屑导航
   - 内容区域
   - 自适应高度

4. 整体风格：
   - 深色主题（适合大屏展示）
   - Element Plus的dark模式
   - 侧边栏宽度200px

创建对应的Router配置和入口页面。
```

### 下午（3小时）

#### Step 3：仪表盘页面（Claude生成）
**Prompt**：
```
请创建仪表盘页面（/dashboard），包含：

顶部统计卡片（4个）：
1. 设备总数 - 显示数字，在线/离线比例小字
2. 在线设备数 - 绿色大数字，带图标
3. 今日告警数 - 红色，Critical数量单独显示
4. 平均温度 - 实时计算，带趋势箭头

中间区域：
- 温度实时趋势图（ECharts折线图）
  - 横轴：时间（最近5分钟）
  - 纵轴：温度（℃）
  - 多条线：每台设备的温度曲线
  - 自动滚动更新
  - WebSocket实时数据驱动

右侧区域：
- 设备状态列表
  - 设备名称、状态（在线绿点/离线灰点）
  - 当前温度、振动、电流数值
  - 按状态排序，在线在前
  - 点击跳转到设备详情

底部区域：
- 最新告警滚动列表（最近5条）
  - 时间、设备、告警内容、级别（颜色区分）
  - 自动刷新

响应式：1920x1080屏幕完美显示
```

#### Step 4：WebSocket前端封装（Claude生成）
**Prompt**：
```
请在前端创建WebSocket服务封装：

1. services/websocket.ts：
   - 自动连接后端WebSocket
   - 心跳检测（ping/pong）
   - 断线自动重连（指数退避）
   - 消息订阅/发布机制
   - TypeScript类型定义

2. 与Pinia集成：
   - WebSocket收到的数据更新Store
   - 组件从Store读取数据

3. 消息处理：
   - 设备数据：更新设备Store
   - 告警消息：更新告警Store + 弹出Notification

4. 错误处理：
   - 连接失败提示
   - 重连状态显示
```

### 晚上（2小时）

#### Step 5：告警中心页面（Claude生成）
**Prompt**：
```
请创建告警中心页面（/alerts）：

1. 筛选区域：
   - 级别选择（Critical/Warning/Info多选）
   - 状态选择（Active/Acknowledged/Resolved）
   - 时间范围（今天/最近7天/自定义）
   - 设备选择（下拉框）

2. 数据表格：
   - 时间、设备名称、告警类型、指标、当前值、阈值、级别
   - 级别用Tag颜色区分
   - 分页显示

3. 操作列：
   - 确认按钮（Active状态显示）
   - 解决按钮
   - 详情按钮

4. 统计卡片：
   - 顶部显示当前筛选条件下的统计

5. 自动刷新：
   - 每30秒自动刷新列表
   - WebSocket推送新告警时立即刷新
```

### Day 4验收标准
- [ ] 打开浏览器能看到实时跳动的温度曲线
- [ ] 模拟器异常时，前端弹出告警通知
- [ ] 设备列表实时更新状态
- [ ] 告警中心能筛选和确认告警
- [ ] 页面运行30分钟不卡顿

---

## Day 5：预测算法（周五）

**目标**：简单预测 + 提前预警
**核心交付**：图表上有预测虚线，能提前预警

### 上午（3小时）

#### Step 1：预测服务（Claude生成）
**Prompt**：
```
请在 backend/app/services/ 下创建 prediction_service.py：

功能：温度趋势预测

算法（简单有效）：
1. 线性回归预测
   - 取最近10个数据点
   - 用scikit-learn的LinearRegression
   - 预测未来3个点的值

2. 预测触发条件
   - 每2分钟运行一次
   - 只预测在线设备
   - 只预测温度（其他指标暂不预测）

3. 预警生成
   - 如果预测值将在5分钟内超过60℃：生成PredictionWarning
   - 如果预测值将在5分钟内超过75℃：生成PredictionCritical
   - 预警写入Alert表，type='prediction'

4. 预测准确率记录
   - 记录预测值和实际值
   - 计算误差（MAE）
   - 用于后续优化

要求：
- 异步执行
- 轻量级（不要用深度学习）
- 包含单元测试
```

**人工决策点**：
- 确认算法选择（线性回归 vs 移动平均）
- 确认预测时间窗口
- 确认预警阈值

#### Step 2：预测API（Claude生成）
**Prompt**：
```
添加预测相关API：

1. GET /api/v1/devices/{id}/prediction
   - 返回该设备的预测数据（未来3个点）
   - 包含预测时间戳

2. GET /api/v1/predictions/accuracy
   - 返回预测准确率统计
   - 今日平均误差
   - 各设备预测准确率

3. WebSocket推送预测更新
   - 每次预测完成后推送
   - 消息格式：{type: 'prediction/update', data: {...}}
```

### 下午（3小时）

#### Step 3：预测可视化（Claude生成）
**Prompt**：
```
扩展仪表盘温度图表，添加预测曲线：

1. ECharts配置修改：
   - 实线：历史数据（过去5分钟）
   - 虚线：预测数据（未来3个点，约1分钟）
   - 不同颜色区分

2. 预测预警卡片：
   - 顶部添加"即将超温预警"卡片
   - 显示哪些设备预测将超标
   - 预计超温时间

3. 预测准确率显示：
   - 小字显示今日预测准确率
   - 鼠标悬停显示详情

4. 图例说明：
   - 添加预测线的图例
   - 说明虚线含义
```

### 晚上（2小时）

测试预测效果，调整参数。

### Day 5验收标准
- [ ] 图表上有预测虚线（即使不准也要有）
- [ ] 预测虚线基于真实算法（不是随机数）
- [ ] 能提前1-2分钟预警温度超标
- [ ] 有预测准确率统计

---

## Day 6：3D展示 + 优化（周六）

**目标**：Three.js简单3D + 系统优化
**核心交付**：能看到设备状态的3D方块

### 上午（3小时）

#### Step 1：Three.js基础场景（Claude生成）
**Prompt**：
```
请在 frontend 中添加Three.js 3D场景：

1. 安装three和@types/three

2. 创建3D组件：
   - 一个平面代表厂房地面（灰色）
   - 10个小方块代表设备（位置随机分布）
   - 方块颜色表示状态：
     - 绿色：正常
     - 黄色：Warning
     - 红色：Critical
     - 灰色：离线

3. 交互：
   - 鼠标悬停显示设备名称和当前温度
   - 点击设备弹出详情卡片
   - 支持旋转、缩放视角

4. 实时更新：
   - 从WebSocket获取状态变化
   - 平滑过渡颜色变化

5. 性能：
   - 限制帧率30fps
   - 组件卸载时清理资源

先不用真实BIM模型，用BoxGeometry即可。
```

#### Step 2：系统优化（Claude辅助）
**Prompt**：
```
请帮我优化以下性能问题：

1. 数据库：
   - SensorData表添加索引（device_id, timestamp）
   - 查询优化（检查慢查询）

2. 前端：
   - ECharts数据点限制（最多显示100个点）
   - 内存泄漏检查
   - 组件懒加载

3. 后端：
   - 数据库连接池配置
   - WebSocket连接数限制
   - 添加请求限流

4. 日志：
   - 减少不必要的日志
   - 添加关键路径日志
```

### 下午（3小时）

#### Step 3：数据导出（Claude生成）
**Prompt**：
```
添加数据导出功能：

1. 后端API：
   - GET /api/v1/sensor-data/export?device_id=xxx&start=xxx&end=xxx
   - 返回CSV文件
   - 支持大数据量（流式导出）

2. 前端页面：
   - 设备详情页添加"导出数据"按钮
   - 时间范围选择器
   - 下载进度显示

3. 告警导出：
   - 类似功能，导出告警记录
```

### 晚上（2小时）

完整测试，准备最终演示。

### Day 6验收标准
- [ ] 3D场景能正常显示，不卡顿
- [ ] 设备状态变化时颜色更新
- [ ] 能导出CSV数据
- [ ] 系统运行稳定

---

## Day 7：复盘 + 文档（周日）

**目标**：输出完整的验证报告
**核心交付**：可演示的系统 + 验证报告

### 上午（3小时）

#### Step 1：代码Review（Claude辅助）
**Prompt**：
```
请Review整个项目的代码：

后端：
1. 检查安全漏洞（SQL注入、未授权访问等）
2. 检查性能瓶颈（N+1查询、内存泄漏等）
3. 检查代码规范（PEP8、类型注解等）
4. 给出改进建议（按优先级排序）

前端：
1. 检查内存泄漏
2. 检查类型安全（TypeScript严格模式）
3. 检查组件设计
4. 给出改进建议

总体：
1. 代码质量打分（1-10）
2. 可维护性评估
3. 如果要继续开发，优先改进哪些？
```

#### Step 2：性能测试（Claude辅助）
**Prompt**：
```
请帮我写性能测试脚本 benchmark.py：

1. WebSocket并发测试
   - 模拟100个WebSocket连接
   - 测量延迟和内存占用

2. API压力测试
   - GET /devices 并发请求
   - 测量QPS和响应时间

3. 数据库测试
   - 模拟1000设备同时写入
   - 测量写入性能

4. 输出测试报告
   - 瓶颈分析
   - 优化建议
```

### 下午（3小时）

#### Step 3：写验证报告
手动编写 docs/validation_report.md：

```markdown
# AI编程验证报告

## 1. 项目概述
- 项目目标：验证AI编程能力边界
- 时间周期：7天
- 人员配置：1人 + Claude Code
- 代码生成比例：99% Claude生成

## 2. 完成度统计
| 模块 | 计划功能 | 完成功能 | 完成度 |
|------|---------|---------|--------|
| 后端API | 20个 | xx个 | xx% |
| 前端页面 | 5个 | xx个 | xx% |
| AI算法 | 2个 | xx个 | xx% |
| 3D展示 | 1个 | xx个 | xx% |

## 3. AI使用统计
- 总Prompt数：xxx
- 平均响应时间：xxx秒
- 代码生成行数：xxx行
- 人工修改比例：x%

## 4. 卡点记录（AI搞不定的）
| 问题 | 解决方案 | 耗时 |
|------|---------|------|
| xxx | xxx | xxx |

## 5. 效率评估
- 传统开发估算：xx人天
- AI辅助实际：7人天
- 效率倍数：xx倍

## 6. 正式项目建议
基于本次验证，正式项目建议：
- 可以做：xxx
- 谨慎做：xxx
- 必须外包：xxx
- 团队配置建议：xxx

## 7. 演示截图/视频
[插入图片和视频链接]
```

### 晚上（2小时）

#### Step 4：最终提交
```bash
# 完善README
cat > README.md << 'EOF'
# 龙泉驿环卫智能体 POC

7天AI密集编程验证项目。

## 快速开始

```bash
# 启动后端
cd backend && docker-compose up -d

# 启动前端
cd frontend && npm install && npm run dev

# 启动模拟器
cd simulator && python device_simulator.py
```

## 功能特性
- 设备监控：实时温度、振动、电流监测
- AI告警：阈值检测 + 趋势分析 + 预测预警
- 数字孪生：3D可视化展示
- 实时通信：WebSocket推送

## 技术栈
- 后端：FastAPI + SQLModel + PostgreSQL + Redis + MQTT
- 前端：Vue3 + TypeScript + Element Plus + ECharts + Three.js
- AI：scikit-learn + 自定义算法

## 演示
[视频链接]

## 验证报告
详见 docs/validation_report.md
EOF

git add .
git commit -m "Day 7: POC complete - validation report and documentation

- Code review and performance benchmark
- Complete validation report
- README with quick start guide
- System ready for demo

co-authored-by: Claude Code"

git tag -a v0.1-poc -m "7-day AI sprint POC complete"
git push origin main --tags
```

### Day 7验收标准
- [ ] GitHub仓库完整，有README
- [ ] 验证报告完成
- [ ] 5分钟演示视频录制完成
- [ ] 系统能完整演示（设备数据→AI检测→告警→3D展示）

---

## 每日时间分配

| 时间段 | 做什么 | 说明 |
|--------|--------|------|
| 09:00-12:00 | 核心开发 | 精力最好，写复杂功能 |
| 12:00-13:00 | 休息 | 必须休息 |
| 13:00-15:00 | 调试+测试 | 下午处理bug |
| 15:00-15:30 | 强制休息 | 保护颈椎 |
| 15:30-18:00 | 继续开发 | 下午后半段 |
| 18:00-19:00 | 休息 | 吃饭 |
| 19:00-21:00 | 代码整理+Git | 不写复杂功能 |
| 21:00后 | 休息 | 不加班，保证第二天状态 |

---

## 风险预案汇总

| 天数 | 风险 | 应对 |
|------|------|------|
| Day 1 | Docker启动失败 | 检查端口，修改docker-compose.yml |
| Day 2 | MQTT连接不稳定 | 改用HTTP POST备选 |
| Day 3 | 告警规则复杂 | 先硬编码，后配置化 |
| Day 4 | 前端卡顿 | 限制数据点数量 |
| Day 5 | 预测算法不准 | 降级为移动平均 |
| Day 6 | Three.js性能差 | 减少设备数量/简化模型 |
| Day 7 | 报告来不及写 | 提前准备模板 |

---

## 关键决策清单（人工必须介入）

- [ ] Day 1上午：确认技术栈（FastAPI+SQLModel）
- [ ] Day 1下午：确认API规范
- [ ] Day 2上午：确认MQTT broker选择
- [ ] Day 2下午：确认数据生成策略
- [ ] Day 3上午：确认告警阈值
- [ ] Day 3下午：确认规则配置方式
- [ ] Day 4上午：确认UI风格（深色主题）
- [ ] Day 5上午：确认预测算法选择
- [ ] Day 6上午：确认3D简化方案
- [ ] Day 7上午：确认是否继续优化或结束

---

**计划完成。现在可以开始详细讨论前20%的内容（Day 1-2）。**
