# Day 4 - Prompt 0: Vue3前端项目初始化

**时机**：Day 4开始，确认后端服务正常后执行
**预期耗时**：Claude生成20分钟，你Review 10分钟
**人工决策**：确认技术栈选择，验收项目结构

---

## 输入Prompt

```text
请在 frontend/ 目录下创建完整的Vue3前端项目。

【技术栈要求】

- Vite 5+（构建工具，要求快速冷启动）
- Vue 3.4+（使用Composition API + <script setup>语法）
- TypeScript 5+（严格类型检查）
- Element Plus 2.5+（UI组件库）
- ECharts 5.4+（图表库，支持实时数据流）
- Pinia 2.1+（状态管理，替代Vuex）
- Vue Router 4.2+（路由管理）
- Axios 1.6+（HTTP客户端）
- VueUse 10+（实用工具组合）

【项目结构】

frontend/
├── public/                    # 静态资源
│   └── favicon.ico
├── src/
│   ├── api/                   # API接口封装
│   │   ├── index.ts          # Axios实例配置
│   │   ├── devices.ts        # 设备API
│   │   ├── alerts.ts         # 告警API
│   │   └── sensor-data.ts    # 传感器数据API
│   ├── components/            # 公共组件
│   │   ├── common/           # 通用组件
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   └── Breadcrumb.vue
│   │   ├── charts/           # 图表组件
│   │   │   ├── RealtimeLineChart.vue   # 实时折线图
│   │   │   ├── GaugeChart.vue          # 仪表盘（温度/振动）
│   │   │   └── AlertStatistics.vue     # 告警统计图表
│   │   └── devices/          # 设备相关组件
│   │       ├── DeviceCard.vue
│   │       └── DeviceStatusBadge.vue
│   ├── views/                 # 页面视图
│   │   ├── Dashboard.vue     # 仪表盘（首页）
│   │   ├── devices/          # 设备管理
│   │   │   ├── DeviceList.vue
│   │   │   └── DeviceDetail.vue
│   │   ├── alerts/           # 告警中心
│   │   │   ├── AlertList.vue
│   │   │   └── AlertRules.vue
│   │   └── system/           # 系统设置
│   │       └── Settings.vue
│   ├── stores/                # Pinia状态管理
│   │   ├── index.ts
│   │   ├── devices.ts        # 设备状态
│   │   ├── alerts.ts         # 告警状态
│   │   ├── websocket.ts      # WebSocket状态
│   │   └── dashboard.ts      # 仪表盘实时数据
│   ├── composables/           # 组合式函数
│   │   ├── useWebSocket.ts   # WebSocket封装
│   │   ├── useRealtimeData.ts # 实时数据流
│   │   └── useDeviceStats.ts # 设备统计
│   ├── types/                 # TypeScript类型定义
│   │   ├── index.ts
│   │   ├── device.ts         # 设备类型
│   │   ├── alert.ts          # 告警类型
│   │   └── sensor.ts         # 传感器数据类型
│   ├── utils/                 # 工具函数
│   │   ├── date.ts           # 日期格式化
│   │   ├── format.ts         # 数据格式化
│   │   └── constants.ts      # 常量定义
│   ├── router/                # 路由配置
│   │   └── index.ts
│   ├── App.vue                # 根组件
│   ├── main.ts                # 入口文件
│   └── style.css              # 全局样式
├── .env.development           # 开发环境配置
├── .env.production            # 生产环境配置
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile

【核心配置】

1. Axios封装（src/api/index.ts）
   - 基础URL从环境变量读取（VITE_API_BASE_URL）
   - 请求拦截器：添加Content-Type
   - 响应拦截器：统一错误处理，Element Plus message提示
   - 导出apiClient实例

2. 环境变量配置
   .env.development:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   VITE_WS_URL=ws://localhost:8000/ws
   VITE_APP_TITLE=龙泉驿环卫智能体
   ```

   .env.production:
   ```
   VITE_API_BASE_URL=/api
   VITE_WS_URL=ws://localhost:8000/ws
   VITE_APP_TITLE=龙泉驿环卫智能体
   ```

3. TypeScript类型（从后端模型同步）
   - Device类型：id, name, type, status, location, created_at
   - Alert类型：id, device_id, device_name, alert_type, metric, message, level, status, created_at
   - SensorData类型：id, device_id, temperature, vibration, current, timestamp
   - 使用enum定义status、level、metric等

4. 路由配置（src/router/index.ts）
   - / - 仪表盘（Dashboard）
   - /devices - 设备列表（DeviceList）
   - /devices/:id - 设备详情（DeviceDetail）
   - /alerts - 告警列表（AlertList）
   - /alert-rules - 告警规则（AlertRules）
   - /settings - 系统设置（Settings）

5. Pinia Store结构
   - devicesStore：设备列表、当前设备、设备统计
   - alertsStore：告警列表、未读数量、告警统计
   - websocketStore：连接状态、消息历史、重连机制
   - dashboardStore：实时数据点、图表数据缓存

6. 全局样式（src/style.css）
   
   【Supabase + Raycast 混合配色方案 - 深色主题】
   
   CSS变量定义：
   ```css
   :root {
     /* 背景层级 - Raycast深黑 + Supabase深灰 */
     --bg-primary: #0F0F0F;        /* 页面主背景 */
     --bg-secondary: #1C1C1C;      /* 卡片、面板 */
     --bg-tertiary: #252525;       /* 悬浮、下拉 */
     --bg-hover: #2A2A2A;          /* 悬停状态 */
     --bg-active: #323232;         /* 激活状态 */
     
     /* 主题色 - Supabase绿 + Raycast紫 */
     --color-primary: #3ECF8E;     /* Supabase绿，主要操作 */
     --color-secondary: #BD93F9;   /* Raycast紫，强调 */
     --color-accent: #FF79C6;      /* Raycast粉，告警 */
     
     /* 状态色 */
     --success: #3ECF8E;           /* 成功、在线 */
     --warning: #FFB86C;           /* 警告 */
     --danger: #FF79C6;            /* 危险、Critical */
     --info: #8BE9FD;              /* 信息 */
     
     /* 文字色 - Raycast文字体系 */
     --text-primary: #F8F8F2;      /* 主要文字 */
     --text-secondary: #B0B0B0;    /* 次要文字 */
     --text-muted: #6272A4;        /* 禁用、提示 */
     --text-inverse: #0F0F0F;      /* 反色 */
     
     /* 边框与分隔 */
     --border: #333333;
     --divider: #252525;
     --shadow: rgba(0, 0, 0, 0.5);
   }
   ```
   
   Element Plus 主题覆盖（深色模式）：
   ```typescript
   // 在main.ts中配置Element Plus主题
   import { createApp } from 'vue'
   import ElementPlus from 'element-plus'
   import 'element-plus/dist/index.css'
   import App from './App.vue'
   
   const app = createApp(App)
   
   // 配置Element Plus为深色主题
   app.use(ElementPlus, {
     zIndex: 3000,
     // 覆盖主题变量
     config: {
       namespace: 'el',
       theme: {
         color: {
           primary: '#3ECF8E',
           success: '#3ECF8E',
           warning: '#FFB86C',
           danger: '#FF79C6',
           info: '#8BE9FD',
           background: '#0F0F0F',
           'bg-secondary': '#1C1C1C',
           text: '#F8F8F2',
           'text-secondary': '#B0B0B0',
           border: '#333333',
         }
       }
     }
   })
   ```
   
   全局样式类：
   - 布局基础类（flex、grid常用组合）
   - 动画定义（fade、slide）
   - 毛玻璃效果（glass-card）
   - 发光效果（glow-green、glow-purple）
   - 渐变文字（gradient-text）

【VSCode配置】（可选）

创建.vscode/settings.json：
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}

【验证要求】

生成后必须验证：
1. cd frontend
2. npm install
3. npm run dev
4. 浏览器访问 http://localhost:5173
5. 能看到空白页面无报错（Console无红色错误）
6. 能正常访问Element Plus组件（测试按钮）

【禁止】
- 不要提交node_modules到Git
- 不要使用Options API（必须用Composition API）
- 不要有any类型（除第三方库未定义外）
```

---

## 预期输出

```
生成文件结构：
frontend/
├── package.json          # 依赖定义
├── vite.config.ts        # Vite配置
├── tsconfig.json         # TS配置
├── index.html
├── .env.development
├── .env.production
├── Dockerfile
└── src/
    ├── main.ts
├── App.vue
    ├── router/
    ├── stores/
    ├── api/
    ├── components/
    ├── views/
    ├── composables/
    ├── types/
    └── utils/

命令执行：
npm install    # 安装依赖成功
npm run dev    # 启动成功，无报错
npm run build  # 构建成功（验证TS无错误）
```

---

## 你的决策

- [ ] 项目能正常启动 → 继续Prompt 1（布局框架）
- [ ] 有TypeScript错误 → 让Claude修复
- [ ] 想调整技术栈 → 告诉Claude修改

---

## 手工验证

```bash
cd frontend
npm install
npm run dev

# 检查点：
# 1. 终端无红色报错
# 2. 浏览器Console无错误
# 3. 访问 http://localhost:5173 能看到空白页面
# 4. 修改src/App.vue能热更新
```
