# Day 4 - Prompt 1: 布局框架与导航

**时机**：项目初始化完成后执行
**预期耗时**：Claude生成15分钟，你Review 10分钟
**人工决策**：确认布局设计，导航结构

---

## 输入Prompt

```text
请创建前端布局框架和导航系统。

【主布局组件】（src/components/layout/MainLayout.vue）

整体结构：
- 顶部：Header（Logo + 标题 + 用户信息）
- 左侧：Sidebar（导航菜单）
- 右侧：内容区（路由视图 + Breadcrumb）
- 底部：Footer（版权信息）

详细规格：
1. Header（高度64px）
   - 左侧：Logo图标 + 系统名称"龙泉驿环卫智能体"
   - 右侧：
     * 实时连接状态（WebSocket状态指示器：绿/红/黄）
     * 未读告警数量（Badge红点）
     * 当前时间（实时更新）
   - 样式：
     * 背景：rgba(15, 15, 15, 0.9)（Raycast黑 + 90%透明度）
     * backdrop-filter: blur(10px)（毛玻璃效果）
     * 底部边框：1px solid #252525
     * 系统名称：渐变文字（Supabase绿 → Raycast紫）

2. Sidebar（宽度220px，可折叠）
   - Logo区域（折叠时隐藏）
   - 菜单项：
     * 仪表盘（Dashboard）- 图标：Home
     * 设备管理（Devices）- 图标：Monitor
     * 告警中心（Alerts）- 图标：Bell（带未读数量Badge）
     * 系统设置（Settings）- 图标：Setting
   - 当前菜单高亮（匹配路由）
   - 折叠按钮（在Sidebar底部）
   - 样式（Supabase+Raycast深色主题）：
     * 背景：#0F0F0F（Raycast黑）
     * 边框右侧：1px solid #252525
     * 菜单文字：#B0B0B0（次要文字色）
     * 悬停背景：#1C1C1C（Supabase灰）
     * 悬停文字：#F8F8F2（主要文字色）
     * 激活背景：#252525
     * 激活文字：#3ECF8E（Supabase绿）
     * 激活指示器：左侧3px边框，#3ECF8E色

3. Content区域
   - Breadcrumb导航（当前位置：首页 > 设备管理 > 列表）
   - 路由视图（router-view）
   - 过渡动画（fade-slide）
   - 内边距：20px
   - 背景：#0F0F0F（Raycast黑）
   - 文字颜色：#F8F8F2（Raycast白）

4. Footer（高度48px）
   - 版权信息：© 2026 龙泉驿环卫智能体 v1.0
   - 样式：
     * 背景：#0F0F0F
     * 文字：#6272A4（Raycast灰蓝）
     * 居中文字
     * 顶部边框：1px solid #252525

【导航菜单组件】（src/components/layout/SidebarMenu.vue）

使用Element Plus的el-menu：
- mode="vertical"
- :collapse="isCollapsed"
- :default-active="currentRoute"
- @select="handleMenuSelect"

菜单数据结构：
```typescript
interface MenuItem {
  path: string
  title: string
  icon: string
  badge?: number  // 未读数量
}

const menus: MenuItem[] = [
  { path: '/', title: '仪表盘', icon: 'HomeFilled' },
  { path: '/devices', title: '设备管理', icon: 'Monitor' },
  { path: '/alerts', title: '告警中心', icon: 'Bell', badge: 0 },
  { path: '/settings', title: '系统设置', icon: 'Setting' },
]
```

【面包屑组件】（src/components/layout/BreadcrumbNav.vue）

自动根据路由生成面包屑：
- 首页 > 仪表盘
- 首页 > 设备管理 > 设备列表
- 首页 > 告警中心 > 告警列表

使用Element Plus的el-breadcrumb

【WebSocket状态组件】（src/components/common/ConnectionStatus.vue）

实时显示连接状态（Supabase+Raycast配色）：
- connected：
  * 圆点：#3ECF8E（Supabase绿）
  * 发光效果：box-shadow: 0 0 10px rgba(62, 207, 142, 0.4)
  * 文字："已连接"
- connecting：
  * 圆点：#FFB86C（Raycast橙）
  * 动画：pulse 1.5s infinite
  * 文字："连接中..."
- disconnected：
  * 圆点：#FF79C6（Raycast粉）
  * 文字："已断开（5秒后重连）"
- 点击可手动触发重连
- 背景：半透明毛玻璃效果（rgba(28, 28, 28, 0.7) + backdrop-filter: blur(10px)）

【基础页面模板】（src/views/Template.vue）

创建临时占位页面：
- Dashboard.vue：欢迎语 + 系统状态概览卡片
- DeviceList.vue：页面标题"设备管理"
- DeviceDetail.vue：页面标题"设备详情" + 返回按钮
- AlertList.vue：页面标题"告警中心"
- AlertRules.vue：页面标题"告警规则"
- Settings.vue：页面标题"系统设置"

【响应式设计】

断点定义：
- lg: >=1200px - 完整显示Sidebar
- md: 768px-1199px - 可折叠Sidebar
- sm: <768px - Sidebar隐藏，通过按钮触发抽屉

使用Element Plus的响应式布局工具

【全局状态集成】（src/stores/layout.ts）

创建layoutStore：
- sidebarCollapsed: boolean
- toggleSidebar(): void
- setSidebarCollapsed(collapsed: boolean): void

【路由集成】（更新src/router/index.ts）

所有路由使用MainLayout作为layout：
```typescript
{
  path: '/',
  component: MainLayout,
  children: [
    { path: '', component: Dashboard },
    { path: 'devices', component: DeviceList },
    { path: 'devices/:id', component: DeviceDetail },
    { path: 'alerts', component: AlertList },
    { path: 'alert-rules', component: AlertRules },
    { path: 'settings', component: Settings },
  ]
}
```

【样式细节 - Supabase + Raycast 混合配色】

1. 颜色方案（深色主题）：
   - 背景层级：
     * --bg-primary: #0F0F0F（Raycast黑，页面背景）
     * --bg-secondary: #1C1C1C（Supabase灰，卡片背景）
     * --bg-tertiary: #252525（悬浮、下拉）
   
   - 主题色：
     * --color-primary: #3ECF8E（Supabase绿，主要操作、在线状态）
     * --color-secondary: #BD93F9（Raycast紫，强调、按钮）
     * --color-accent: #FF79C6（Raycast粉，告警、通知）
   
   - 状态色：
     * 成功/在线：#3ECF8E（Supabase绿）
     * 警告：#FFB86C（Raycast橙）
     * 危险/Critical：#FF79C6（Raycast粉）
     * 信息：#8BE9FD（Raycast青）
   
   - 文字色：
     * 主要文字：#F8F8F2（Raycast白）
     * 次要文字：#B0B0B0（Supabase灰）
     * 禁用/提示：#6272A4（Raycast灰蓝）
   
   - 边框：#333333
   - 分隔线：#252525

2. 渐变效果：
   - 系统标题：linear-gradient(135deg, #3ECF8E 0%, #BD93F9 100%)
   - 统计数值：linear-gradient(135deg, #3ECF8E 0%, #BD93F9 100%)
   - 主要按钮：linear-gradient(135deg, #3ECF8E 0%, #2EB87C 100%)
   - 强调按钮：linear-gradient(135deg, #BD93F9 0%, #9A6DE0 100%)

3. 特殊效果：
   - 毛玻璃：backdrop-filter: blur(10px)，背景 rgba(28, 28, 28, 0.7)
   - 绿光发光：box-shadow: 0 0 20px rgba(62, 207, 142, 0.3)
   - 粉光发光：box-shadow: 0 0 20px rgba(255, 121, 198, 0.3)
   - 卡片悬停：transform: translateY(-2px) + 绿色微光阴影

2. 字体：
   - 系统字体栈：'Helvetica Neue', Helvetica, 'PingFang SC', sans-serif
   - 基础字号：14px

3. 间距：
   - 基础单位：8px
   - 内容区内边距：20px
   - 组件间距：16px

【验证步骤】

1. npm run dev启动项目
2. 访问 http://localhost:5173
3. 验证：
   - 能看到左侧深色Sidebar
   - 顶部Header显示系统名称
   - 点击菜单能切换路由
   - 当前菜单项高亮
   - 折叠/展开Sidebar正常
   - 面包屑显示正确
   - WebSocket状态指示器显示（可以先mock状态）
```

---

## 预期输出

```
生成文件：
- src/components/layout/MainLayout.vue [完成]
- src/components/layout/SidebarMenu.vue [完成]
- src/components/layout/BreadcrumbNav.vue [完成]
- src/components/common/ConnectionStatus.vue [完成]
- src/stores/layout.ts [完成]
- src/router/index.ts [更新]
- src/views/Dashboard.vue [完成]
- src/views/devices/DeviceList.vue [完成]
- src/views/devices/DeviceDetail.vue [完成]
- src/views/alerts/AlertList.vue [完成]
- src/views/alerts/AlertRules.vue [完成]
- src/views/system/Settings.vue [完成]

界面效果：
- 左侧深色Sidebar，有4个菜单项
- 顶部Header白色，显示系统名称
- 中间内容区白色背景
- 点击菜单切换路由，URL变化
- 页面切换有平滑过渡动画
```

---

## 你的决策

- [ ] 布局正常显示 → 继续Prompt 2（仪表盘图表）
- [ ] 颜色想调整 → 提供新的颜色方案
- [ ] 需要更多菜单 → 添加菜单项

---

## 手工验证

```bash
cd frontend
npm run dev

# 测试点：
# 1. 访问 http://localhost:5173
# 2. 能看到左侧侧边栏（深色）
# 3. 能看到顶部Header（白色）
# 4. 点击"设备管理"，URL变为/devices
# 5. 点击"告警中心"，URL变为/alerts
# 6. 点击Sidebar底部按钮，能折叠/展开
```
