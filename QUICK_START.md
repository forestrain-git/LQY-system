# 龙泉驿环卫智能体 - 快速启动指南

## 环境要求
- Node.js 18+
- Python 3.10+ (如需运行后端)
- Google Chrome (推荐)

## 前端启动

```bash
cd frontend
npm install  # 如未安装依赖
npm run dev
```

访问: http://localhost:5173/login

## 登录凭证

### 演示模式（当前可用）
- 用户名: `admin`
- 密码: `admin123`
- 或
- 用户名: `operator`
- 密码: `operator123`

## 项目结构

```
frontend/
├── src/
│   ├── style.css                 # 高对比度主题主文件
│   ├── styles/
│   │   ├── high-contrast-theme.css   # 主题变量系统
│   │   └── global-fix.css            # 全局样式修复
│   ├── views/
│   │   ├── LoginView.vue         # 登录页面（演示模式）
│   │   ├── DashboardView.vue     # 仪表板
│   │   └── AIAssistantView.vue   # AI助手
│   └── router/
│       └── index.ts              # 路由配置
└── vite.config.ts                # Vite配置
```

## 关键功能

### 1. 高对比度主题
- 亮蓝灰背景 (#1e293b)
- 纯白文字 (#ffffff)
- 鲜艳按钮 (#3b82f6)
- 清晰边框和阴影

### 2. 演示模式
- 无需后端即可登录
- 完整前端界面体验
- 模拟数据展示

### 3. 响应式设计
- 适配桌面端
- 移动端基础适配

## 常见问题

### 字体显示问题
已添加Microsoft YaHei, PingFang SC字体回退

### 登录失败
- 检查网络连接
- 使用演示模式账号
- 查看浏览器控制台

### 样式不生效
- 清除浏览器缓存
- 重启Vite服务器
- 检查控制台错误

## 开发计划

1. **短期**
   - 连接后端API
   - 完善数据交互
   - 优化移动端

2. **中期**
   - 主题切换功能
   - 用户偏好设置
   - 性能优化

3. **长期**
   - PWA支持
   - 离线功能
   - 多语言支持

## 联系信息

项目地址: https://github.com/forestrain-git/LQY-system
