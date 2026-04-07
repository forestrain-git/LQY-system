# Supabase + Raycast 混合配色方案

## 设计灵感

### Supabase 特点
- ** emerald 绿色主调**：#3ECF8E（充满活力、技术感）
- **深灰背景**：#1C1C1C（专业、沉稳）
- **高对比文字**：纯白 + 灰色层级
- **现代感**：圆角、阴影、渐变

### Raycast 特点
- **深黑背景**：#0F0F0F（沉浸式、专注）
- **紫罗兰强调**：#BD93F9（优雅、高级）
- **粉紫辅助**：#FF79C6（活力、醒目）
- **毛玻璃效果**：半透明、模糊背景

### 混合策略
- **背景**：Raycast 的深黑 (#0F0F0F) 为主，Supabase 的深灰 (#1C1C1C) 为卡片
- **主色**：Supabase 绿 (#3ECF8E) - 用于成功、在线、运行状态
- **强调**：Raycast 紫 (#BD93F9) - 用于告警、通知、按钮
- **渐变**：绿→紫 渐变用于标题、特殊强调
- **文字**：Raycast 的浅色文字体系（F8F8F2 + 6272A4）

---

## 配色规范

### 背景色层级
| Token | 值 | 用途 |
|-------|-----|------|
| `--bg-primary` | #0F0F0F | 页面主背景（Raycast黑） |
| `--bg-secondary` | #1C1C1C | 卡片、面板（Supabase灰） |
| `--bg-tertiary` | #252525 | 悬浮、下拉菜单 |
| `--bg-hover` | #2A2A2A | 悬停状态 |
| `--bg-active` | #323232 | 激活状态 |

### 主题色
| Token | 值 | 用途 |
|-------|-----|------|
| `--color-primary` | #3ECF8E | Supabase绿，主要操作 |
| `--color-secondary` | #BD93F9 | Raycast紫，强调、告警 |
| `--color-accent` | #FF79C6 | Raycast粉，通知、Badge |
| `--color-gradient-start` | #3ECF8E | 渐变起点（绿） |
| `--color-gradient-end` | #BD93F9 | 渐变终点（紫） |

### 状态色
| Token | 值 | 用途 |
|-------|-----|------|
| `--success` | #3ECF8E | 成功、在线（Supabase绿） |
| `--warning` | #FFB86C | 警告（Raycast橙） |
| `--danger` | #FF79C6 | 危险、Critical（Raycast粉） |
| `--info` | #8BE9FD | 信息（Raycast青） |

### 文字色
| Token | 值 | 用途 |
|-------|-----|------|
| `--text-primary` | #F8F8F2 | 主要文字（Raycast白） |
| `--text-secondary` | #B0B0B0 | 次要文字（Supabase灰） |
| `--text-muted` | #6272A4 | 禁用、提示（Raycast灰蓝） |
| `--text-inverse` | #0F0F0F | 反色（深色背景上的文字） |

### 边框与分隔
| Token | 值 | 用途 |
|-------|-----|------|
| `--border` | #333333 | 边框 |
| `--divider` | #252525 | 分隔线 |
| `--shadow` | rgba(0,0,0,0.5) | 阴影 |

---

## 组件样式规范

### Sidebar（左侧导航）
```css
background: #0F0F0F;
border-right: 1px solid #252525;
/* 菜单项 */
.menu-item {
  color: #B0B0B0;
  hover: {
    background: #1C1C1C;
    color: #F8F8F2;
  }
  active: {
    background: #252525;
    color: #3ECF8E; /* Supabase绿 */
    border-left: 3px solid #3ECF8E;
  }
}
/* 当前菜单指示器 */
.active-indicator {
  background: linear-gradient(180deg, #3ECF8E 0%, #BD93F9 100%);
}
```

### Header（顶部栏）
```css
background: rgba(15, 15, 15, 0.9); /* Raycast黑 + 透明 */
backdrop-filter: blur(10px); /* 毛玻璃效果 */
border-bottom: 1px solid #252525;
/* WebSocket状态指示器 */
.status-online {
  background: #3ECF8E; /* Supabase绿 */
  box-shadow: 0 0 10px rgba(62, 207, 142, 0.4);
}
.status-offline {
  background: #FF79C6; /* Raycast粉 */
}
```

### 统计卡片（Dashboard Stats Card）
```css
background: #1C1C1C; /* Supabase灰 */
border: 1px solid #252525;
border-radius: 12px;
box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
/* 悬停效果 */
hover: {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(62, 207, 142, 0.15); /* 绿色微光 */
  border-color: #3ECF8E20;
}
/* 数值文字 */
.stat-value {
  background: linear-gradient(135deg, #3ECF8E 0%, #BD93F9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}
```

### 按钮样式
```css
/* 主要按钮（Primary） */
.btn-primary {
  background: linear-gradient(135deg, #3ECF8E 0%, #2EB87C 100%);
  color: #0F0F0F;
  border: none;
  border-radius: 8px;
  font-weight: 600;
}

/* 强调按钮（Secondary） */
.btn-secondary {
  background: linear-gradient(135deg, #BD93F9 0%, #9A6DE0 100%);
  color: #0F0F0F;
}

/* 危险按钮（Danger） */
.btn-danger {
  background: linear-gradient(135deg, #FF79C6 0%, #E05A9F 100%);
  color: #0F0F0F;
}

/* 幽灵按钮（Ghost） */
.btn-ghost {
  background: transparent;
  border: 1px solid #333333;
  color: #F8F8F2;
  hover: {
    border-color: #BD93F9;
    color: #BD93F9;
  }
}
```

### 表格样式
```css
/* 表头 */
.table-header {
  background: #1C1C1C;
  color: #B0B0B0;
  font-weight: 600;
  border-bottom: 2px solid #3ECF8E40;
}

/* 表身 */
.table-row {
  background: #0F0F0F;
  border-bottom: 1px solid #252525;
  color: #F8F8F2;
  
  hover: {
    background: #1C1C1C;
  }
  
  &.active {
    background: #252525;
    border-left: 3px solid #BD93F9;
  }
}

/* 告警级别标签 */
.tag-critical {
  background: rgba(255, 121, 198, 0.15);
  color: #FF79C6;
  border: 1px solid #FF79C640;
}

.tag-warning {
  background: rgba(255, 184, 108, 0.15);
  color: #FFB86C;
  border: 1px solid #FFB86C40;
}

.tag-info {
  background: rgba(139, 233, 253, 0.15);
  color: #8BE9FD;
  border: 1px solid #8BE9FD40;
}
```

### 图表配色（ECharts）
```javascript
// 主题配置
const supabaseRaycastTheme = {
  backgroundColor: 'transparent',
  // 色板：绿→紫→粉→青→黄
  color: ['#3ECF8E', '#BD93F9', '#FF79C6', '#8BE9FD', '#FFB86C', '#50FA7B'],
  
  // 坐标轴
  categoryAxis: {
    axisLine: { lineStyle: { color: '#333333' } },
    axisLabel: { color: '#B0B0B0' },
    splitLine: { lineStyle: { color: '#252525' } }
  },
  
  // 数值轴
  valueAxis: {
    axisLine: { lineStyle: { color: '#333333' } },
    axisLabel: { color: '#B0B0B0' },
    splitLine: { lineStyle: { color: '#252525', type: 'dashed' } }
  },
  
  // 提示框
  tooltip: {
    backgroundColor: 'rgba(28, 28, 28, 0.95)',
    borderColor: '#333333',
    textStyle: { color: '#F8F8F2' },
    extraCssText: 'backdrop-filter: blur(4px);'
  }
};

// 温度曲线渐变
const temperatureLineGradient = {
  type: 'linear',
  x: 0, y: 0, x2: 1, y2: 0,
  colorStops: [
    { offset: 0, color: '#3ECF8E' },   // 绿色（正常）
    { offset: 0.5, color: '#FFB86C' }, // 橙色（警告）
    { offset: 1, color: '#FF79C6' }    // 粉色（危险）
  ]
};
```

### 通知/Toast样式
```css
/* 成功通知 */
.notification-success {
  background: rgba(62, 207, 142, 0.15);
  border: 1px solid #3ECF8E40;
  color: #3ECF8E;
  backdrop-filter: blur(10px);
}

/* 告警通知 */
.notification-warning {
  background: rgba(255, 121, 198, 0.15);
  border: 1px solid #FF79C640;
  color: #FF79C6;
  backdrop-filter: blur(10px);
}
```

### 滚动条样式
```css
/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #0F0F0F;
}

::-webkit-scrollbar-thumb {
  background: #333333;
  border-radius: 4px;
  
  &:hover {
    background: #3ECF8E;
  }
}
```

---

## 特殊效果

### 1. 毛玻璃卡片（Glassmorphism）
```css
.glass-card {
  background: rgba(28, 28, 28, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

### 2. 发光效果（Glow）
```css
/* Supabase绿发光 */
.glow-green {
  box-shadow: 0 0 20px rgba(62, 207, 142, 0.3);
}

/* Raycast紫发光 */
.glow-purple {
  box-shadow: 0 0 20px rgba(189, 147, 249, 0.3);
}
```

### 3. 渐变文字
```css
.gradient-text {
  background: linear-gradient(135deg, #3ECF8E 0%, #BD93F9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}
```

### 4. 动态渐变边框
```css
.animated-border {
  position: relative;
  background: #1C1C1C;
  border-radius: 12px;
  
  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 14px;
    background: linear-gradient(45deg, #3ECF8E, #BD93F9, #FF79C6, #3ECF8E);
    background-size: 400% 400%;
    z-index: -1;
    animation: gradient-rotate 3s ease infinite;
  }
}

@keyframes gradient-rotate {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
```

---

## 应用场景对照

| 场景 | 使用的配色 | 效果 |
|------|-----------|------|
| 在线状态 | #3ECF8E (Supabase绿) | 活力、安全 |
| 离线状态 | #FF79C6 (Raycast粉) | 警告、注意 |
| 告警Critical | #FF79C6 + 发光效果 | 醒目、紧急 |
| 告警Warning | #FFB86C (Raycast橙) | 温和提醒 |
| 数据图表 | 绿→紫 渐变 | 科技感、美观 |
| 按钮主要 | Supabase绿渐变 | 操作引导 |
| 按钮强调 | Raycast紫渐变 | 特殊功能 |
| 背景层级 | Raycast黑 + Supabase灰 | 深度感 |

---

## Element Plus 主题配置

```typescript
// element-plus-theme.ts
export const supabaseRaycastTheme = {
  colors: {
    primary: '#3ECF8E',      // Supabase绿
    success: '#3ECF8E',      // 成功
    warning: '#FFB86C',      // 警告
    danger: '#FF79C6',       // 危险
    info: '#8BE9FD',         // 信息
    background: '#0F0F0F',   // 背景
    'bg-secondary': '#1C1C1C', // 卡片
    text: '#F8F8F2',         // 文字
    'text-secondary': '#B0B0B0', // 次要文字
    border: '#333333',       // 边框
  },
  
  // 组件特定配置
  components: {
    Button: {
      'bg-color': '#3ECF8E',
      'text-color': '#0F0F0F',
      'border-color': '#3ECF8E',
    },
    Card: {
      'bg-color': '#1C1C1C',
      'border-color': '#252525',
    },
    Table: {
      'bg-color': '#0F0F0F',
      'header-bg-color': '#1C1C1C',
      'border-color': '#252525',
    },
    Input: {
      'bg-color': '#1C1C1C',
      'border-color': '#333333',
      'text-color': '#F8F8F2',
    },
    Tag: {
      'bg-color': 'rgba(62, 207, 142, 0.15)',
      'text-color': '#3ECF8E',
    }
  }
};
```

---

## 文件更新清单

使用此配色方案需要更新以下文件：

1. `src/style.css` - 全局CSS变量
2. `src/main.ts` - Element Plus 主题配置
3. `src/components/charts/*` - ECharts主题配置
4. `src/App.vue` - 全局背景色

---

## 对比原设计

| 方面 | 原设计（Element Plus默认） | Supabase+Raycast混合 |
|------|---------------------------|---------------------|
| 背景 | 白色/light | 深色（#0F0F0F） |
| 主色 | 蓝色 (#409EFF) | 绿色 (#3ECF8E) |
| 强调色 | 橙色/红色 | 紫色/粉色 |
| 风格 | 传统后台 | 现代开发工具 |
| 特色 | 简洁 | 科技感+沉浸式 |

此配色方案更适合展示实时数据，营造专业、现代的IoT平台氛围。
