# Day 4: 前端看板（Vue3 + ECharts）

**目标**：构建实时数据可视化看板，浏览器能看到跳动的图表和告警  
**核心交付**：完整的Vue3前端应用，支持实时数据推送和设备/告警管理

---

## 任务结构

| 序号 | 文件 | 内容 | 预计耗时 |
|------|------|------|----------|
| 00 | [项目初始化](00_project_setup.md) | Vue3 + TypeScript + Vite + Element Plus | 30分钟 |
| 01 | [布局框架](01_layout_framework.md) | 侧边栏导航 + Header + 响应式布局 | 25分钟 |
| 02 | [仪表盘图表](02_dashboard_charts.md) | 实时温度曲线、仪表盘、统计卡片 | 40分钟 |
| 03 | [WebSocket集成](03_websocket_integration.md) | 实时数据推送、通知、重连机制 | 30分钟 |
| 04 | [管理界面](04_management_ui.md) | 告警列表、设备管理、详情页 | 40分钟 |
| 05 | [验证构建](05_validation_build.md) | 测试脚本、Docker集成、Git提交 | 35分钟 |

**总计**：约3.5-4小时（含Review时间）

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Vue 3.4+ (Composition API) |
| 语言 | TypeScript 5+ |
| 构建工具 | Vite 5+ |
| UI组件库 | Element Plus 2.5+ |
| 图表库 | ECharts 5.4+ |
| 状态管理 | Pinia 2.1+ |
| 路由 | Vue Router 4+ |
| HTTP | Axios 1.6+ |
| 工具库 | VueUse 10+ |

---

## 页面结构

```
/
├── /                      # 仪表盘（实时图表）
│   ├── 统计卡片（在线设备、告警数、平均温度、数据速率）
│   ├── 实时温度曲线图（每10秒更新）
│   ├── 设备状态分布饼图
│   ├── 告警级别柱状图
│   └── 实时数据表格
│
├── /devices               # 设备管理
│   ├── 设备卡片网格（状态、实时数据）
│   └── /devices/:id       # 设备详情
│       ├── 实时数据面板
│       ├── 历史趋势图（可缩放）
│       └── 告警历史
│
├── /alerts                # 告警中心
│   ├── 告警列表（筛选、分页、批量操作）
│   └── /alert-rules       # 告警规则管理
│
└── /settings              # 系统设置
```

---

## 核心功能

### 1. 实时数据流
- WebSocket连接后端（ws://localhost:8000/ws）
- 每10秒接收传感器数据
- 温度曲线右侧推入新点，左侧移出旧点（保留30点）
- 断线自动重连（最多5次，5秒间隔）

### 2. 告警通知
- 新告警弹出Element Plus通知（Critical不自动关闭）
- Header显示未读告警数量Badge
- WebSocket推送alert_updated时更新列表

### 3. 数据可视化
- **实时曲线图**：温度趋势，平滑曲线，区域填充
- **仪表盘**：当前平均温度，分段颜色（绿/黄/红）
- **饼图**：设备状态分布
- **柱状图**：告警级别统计

### 4. 管理功能
- 告警筛选（时间、级别、状态、指标、设备）
- 批量确认/解决告警
- 告警规则CRUD（启用/禁用开关）
- 设备新增/编辑/删除（软删除）
- 设备详情历史数据查询（1小时/6小时/24小时/7天）

---

## 项目结构

```
frontend/
├── src/
│   ├── api/               # API接口封装
│   │   ├── index.ts       # Axios配置
│   │   ├── devices.ts     # 设备API
│   │   ├── alerts.ts      # 告警API
│   │   └── alert-rules.ts # 规则API
│   │
│   ├── components/        # 组件
│   │   ├── layout/        # 布局组件
│   │   │   ├── MainLayout.vue
│   │   │   ├── SidebarMenu.vue
│   │   │   └── BreadcrumbNav.vue
│   │   ├── common/        # 通用组件
│   │   │   └── ConnectionStatus.vue
│   │   ├── dashboard/     # 仪表盘组件
│   │   │   ├── StatCard.vue
│   │   │   └── RealtimeDataTable.vue
│   │   ├── charts/        # 图表组件
│   │   │   ├── RealtimeTemperatureChart.vue
│   │   │   ├── DeviceGaugeChart.vue
│   │   │   └── AlertStatistics.vue
│   │   ├── alerts/        # 告警组件
│   │   │   ├── AlertDetailDrawer.vue
│   │   │   └── AlertRuleFormDialog.vue
│   │   └── devices/       # 设备组件
│   │       ├── DeviceCard.vue
│   │       └── DeviceFormDialog.vue
│   │
│   ├── views/             # 页面视图
│   │   ├── Dashboard.vue
│   │   ├── devices/
│   │   │   ├── DeviceList.vue
│   │   │   └── DeviceDetail.vue
│   │   ├── alerts/
│   │   │   ├── AlertList.vue
│   │   │   └── AlertRules.vue
│   │   └── system/
│   │       └── Settings.vue
│   │
│   ├── stores/            # Pinia状态管理
│   │   ├── index.ts
│   │   ├── layout.ts
│   │   ├── dashboard.ts   # 仪表盘数据
│   │   ├── alerts.ts      # 告警状态
│   │   ├── devices.ts     # 设备状态
│   │   └── websocket.ts   # WebSocket状态
│   │
│   ├── composables/       # 组合式函数
│   │   ├── useWebSocket.ts       # WebSocket封装
│   │   ├── useRealtimeData.ts    # 实时数据
│   │   ├── useECharts.ts         # ECharts封装
│   │   └── useDeviceStats.ts     # 设备统计
│   │
│   ├── types/             # TypeScript类型
│   │   ├── index.ts
│   │   ├── device.ts
│   │   ├── alert.ts
│   │   └── sensor.ts
│   │
│   ├── utils/             # 工具函数
│   │   ├── date.ts        # 日期格式化
│   │   ├── format.ts      # 数据格式化
│   │   ├── constants.ts   # 常量
│   │   └── notification.ts # 通知封装
│   │
│   ├── router/            # 路由配置
│   │   └── index.ts
│   │
│   ├── App.vue
│   ├── main.ts
│   └── style.css          # 全局样式
│
├── .env.development       # 开发环境配置
├── .env.production        # 生产环境配置
├── package.json
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
├── validate_frontend.py   # 验证脚本
├── build.sh               # 构建脚本
└── README.md
```

---

## 关键设计

### 响应式布局
- **lg** (≥1200px)：完整侧边栏 + 4列卡片
- **md** (768-1199px)：可折叠侧边栏 + 2列卡片
- **sm** (<768px)：抽屉式侧边栏 + 单列布局

### 颜色方案：Supabase + Raycast 混合主题

**深色背景层级**
- 主背景：#0F0F0F（Raycast黑）
- 卡片背景：#1C1C1C（Supabase灰）
- 边框/分隔：#252525 / #333333

**主题色**
- 主色：#3ECF8E（Supabase翠绿）- 成功、在线、主要操作
- 强调：#BD93F9（Raycast紫罗兰）- 强调按钮、高亮
- 告警：#FF79C6（Raycast粉红）- Critical、危险、离线
- 警告：#FFB86C（Raycast橙）- Warning、注意
- 信息：#8BE9FD（Raycast青）- Info、提示

**文字颜色**
- 主要文字：#F8F8F2（Raycast白）
- 次要文字：#B0B0B0（Supabase灰）
- 禁用/提示：#6272A4（Raycast灰蓝）

**特殊效果**
- 绿→紫渐变：标题、数值、按钮
- 毛玻璃效果：弹出层、提示框
- 发光效果：在线状态、告警提示

📚 [完整配色文档](SUPABASE_RAYCAST_THEME.md) | [速查手册](COLOR_CHEAT_SHEET.md)

### 数据更新策略
1. **WebSocket优先**：实时推送传感器数据
2. **HTTP Fallback**：WebSocket断开时，5秒轮询
3. **分页数据**：进入页面时加载，操作后刷新
4. **统计数据**：5秒定时刷新

---

## 验证清单

### 功能验证
- [ ] 页面加载无Console报错
- [ ] WebSocket连接成功（Header绿色指示器）
- [ ] 模拟器数据实时显示（10秒间隔）
- [ ] 温度曲线自动滚动（右侧推入，30点窗口）
- [ ] 异常数据触发告警通知（Critical红色，不自动关闭）
- [ ] 告警列表筛选正常（时间/级别/状态/设备）
- [ ] 告警确认/解决后状态更新
- [ ] 设备卡片显示实时数据
- [ ] 设备详情历史图表可缩放
- [ ] 断线后自动重连（5秒间隔）

### 性能验证
- [ ] 页面运行10分钟不卡顿
- [ ] 内存占用稳定在200MB以内
- [ ] 温度曲线滚动流畅（60fps）
- [ ] 表格分页切换快速（<500ms）

### 兼容性验证
- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Edge 90+

---

## 启动指令

在Claude中输入：
```
请读取 prompts/day4/00_project_setup.md 并开始执行
```

每完成一个Prompt，Claude会询问是否继续。

---

## 关键命令

```bash
# 开发模式
cd frontend
npm install
npm run dev

# 构建
npm run build

# 验证
python3 validate_frontend.py

# Docker构建
docker build -t lqy-frontend .
docker run -p 80:80 lqy-frontend

# 完整环境启动
cd backend
docker-compose up -d  # 包含前端、后端、数据库、MQTT
```

---

## 昨日成果

Day 3已完成：
- 告警检测服务（阈值+趋势）
- 告警管理API
- WebSocket推送
- Redis重复抑制

## 明日预告

Day 5将构建：
- 趋势预测算法
- 提前预警机制
- 前端展示预测曲线

---

**开始**：`请读取 prompts/day4/00_project_setup.md 并开始执行`
