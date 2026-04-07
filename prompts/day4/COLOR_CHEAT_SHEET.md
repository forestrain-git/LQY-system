# Supabase + Raycast 配色方案速查表

## 核心色值

| 颜色 | Hex | RGBA | 用途 |
|------|-----|------|------|
| **Supabase绿** | `#3ECF8E` | `rgba(62, 207, 142, 1)` | 主色、成功、在线 |
| **Raycast紫** | `#BD93F9` | `rgba(189, 147, 249, 1)` | 强调、按钮、高亮 |
| **Raycast粉** | `#FF79C6` | `rgba(255, 121, 198, 1)` | 危险、Critical、告警 |
| **Raycast橙** | `#FFB86C` | `rgba(255, 184, 108, 1)` | 警告、Warning |
| **Raycast青** | `#8BE9FD` | `rgba(139, 233, 253, 1)` | 信息、Info |
| **Raycast灰蓝** | `#6272A4` | `rgba(98, 114, 164, 1)` | 禁用、次要文字 |

## 背景色层级

```css
--bg-primary: #0F0F0F     /* Raycast黑 - 页面主背景 */
--bg-secondary: #1C1C1C   /* Supabase灰 - 卡片、面板 */
--bg-tertiary: #252525    /* 悬浮、下拉菜单 */
--bg-hover: #2A2A2A       /* 悬停状态 */
--bg-active: #323232      /* 激活状态 */
```

## 文字颜色

```css
--text-primary: #F8F8F2     /* Raycast白 - 主要文字 */
--text-secondary: #B0B0B0   /* Supabase灰 - 次要文字 */
--text-muted: #6272A4       /* Raycast灰蓝 - 禁用、提示 */
--text-inverse: #0F0F0F     /* 反色 - 按钮上的文字 */
```

## 边框与分隔

```css
--border: #333333       /* 边框 */
--divider: #252525      /* 分隔线 */
--shadow: rgba(0, 0, 0, 0.5)  /* 阴影 */
```

## 组件速查

### Button 按钮

```css
/* 主要按钮 - Supabase绿 */
.btn-primary {
  background: linear-gradient(135deg, #3ECF8E 0%, #2EB87C 100%);
  color: #0F0F0F;
}

/* 强调按钮 - Raycast紫 */
.btn-secondary {
  background: linear-gradient(135deg, #BD93F9 0%, #9A6DE0 100%);
  color: #0F0F0F;
}

/* 危险按钮 - Raycast粉 */
.btn-danger {
  background: linear-gradient(135deg, #FF79C6 0%, #E05A9F 100%);
  color: #0F0F0F;
}

/* 幽灵按钮 */
.btn-ghost {
  background: transparent;
  border: 1px solid #333333;
  color: #F8F8F2;
}
.btn-ghost:hover {
  border-color: #BD93F9;
  color: #BD93F9;
}
```

### Card 卡片

```css
.card {
  background: #1C1C1C;
  border: 1px solid #252525;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(62, 207, 142, 0.15); /* 绿色微光 */
  border-color: rgba(62, 207, 142, 0.2);
}
```

### Tag 标签

```css
/* Critical */
.tag-critical {
  background: rgba(255, 121, 198, 0.15);
  color: #FF79C6;
  border: 1px solid rgba(255, 121, 198, 0.4);
}

/* Warning */
.tag-warning {
  background: rgba(255, 184, 108, 0.15);
  color: #FFB86C;
  border: 1px solid rgba(255, 184, 108, 0.4);
}

/* Success */
.tag-success {
  background: rgba(62, 207, 142, 0.15);
  color: #3ECF8E;
  border: 1px solid rgba(62, 207, 142, 0.4);
}

/* Info */
.tag-info {
  background: rgba(139, 233, 253, 0.15);
  color: #8BE9FD;
  border: 1px solid rgba(139, 233, 253, 0.4);
}
```

### Table 表格

```css
.table-header {
  background: #1C1C1C;
  color: #B0B0B0;
  font-weight: 600;
  border-bottom: 2px solid rgba(62, 207, 142, 0.3); /* 绿色微光 */
}

.table-row {
  background: #0F0F0F;
  color: #F8F8F2;
  border-bottom: 1px solid #252525;
}

.table-row:hover {
  background: #1C1C1C;
}

.table-row.active {
  background: #252525;
  border-left: 3px solid #BD93F9; /* Raycast紫 */
}
```

## ECharts 图表配色

### 色板

```javascript
const colorPalette = [
  '#3ECF8E',  // Supabase绿
  '#BD93F9',  // Raycast紫
  '#FF79C6',  // Raycast粉
  '#8BE9FD',  // Raycast青
  '#FFB86C',  // Raycast橙
  '#50FA7B',  // 亮绿
];
```

### 温度曲线渐变

```javascript
const temperatureGradient = {
  type: 'linear',
  x: 0, y: 0, x2: 1, y2: 0,
  colorStops: [
    { offset: 0, color: '#3ECF8E' },    // 绿色（正常）
    { offset: 0.5, color: '#FFB86C' },  // 橙色（警告）
    { offset: 1, color: '#FF79C6' }     // 粉色（危险）
  ]
};
```

### 坐标轴样式

```javascript
const axisStyle = {
  axisLine: { lineStyle: { color: '#333333' } },
  axisLabel: { color: '#B0B0B0' },
  splitLine: { lineStyle: { color: '#252525', type: 'dashed' } }
};
```

### 提示框样式

```javascript
const tooltipStyle = {
  backgroundColor: 'rgba(28, 28, 28, 0.95)',
  borderColor: '#333333',
  textStyle: { color: '#F8F8F2' },
  extraCssText: 'backdrop-filter: blur(4px);'
};
```

## 特殊效果

### 毛玻璃效果

```css
.glass {
  background: rgba(28, 28, 28, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### 绿色发光

```css
.glow-green {
  box-shadow: 0 0 20px rgba(62, 207, 142, 0.3);
}
```

### 粉色发光

```css
.glow-pink {
  box-shadow: 0 0 20px rgba(255, 121, 198, 0.3);
}
```

### 渐变文字

```css
.gradient-text {
  background: linear-gradient(135deg, #3ECF8E 0%, #BD93F9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}
```

## 场景对照表

| 场景 | 使用的配色 | 效果 |
|------|-----------|------|
| 在线状态 | `#3ECF8E` (Supabase绿) | 活力、安全 |
| 离线状态 | `#FF79C6` (Raycast粉) | 警告、注意 |
| 告警Critical | `#FF79C6` + 发光效果 | 醒目、紧急 |
| 告警Warning | `#FFB86C` (Raycast橙) | 温和提醒 |
| 数据图表 | 绿→紫 渐变 | 科技感、美观 |
| 按钮主要 | Supabase绿渐变 | 操作引导 |
| 按钮强调 | Raycast紫渐变 | 特殊功能 |
| 背景层级 | Raycast黑 + Supabase灰 | 深度感 |

## Element Plus 主题覆盖

```typescript
// element-plus.ts
export const theme = {
  colors: {
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
};
```

## VSCode 片段

```json
{
  "Supabase Green": {
    "prefix": "sg",
    "body": ["#3ECF8E"],
    "description": "Supabase Green"
  },
  "Raycast Purple": {
    "prefix": "rp",
    "body": ["#BD93F9"],
    "description": "Raycast Purple"
  },
  "Raycast Pink": {
    "prefix": "rf",
    "body": ["#FF79C6"],
    "description": "Raycast Pink"
  }
}
```

## 设计原则

1. **深色优先**：所有背景使用 Raycast 黑 (#0F0F0F) 或 Supabase 灰 (#1C1C1C)
2. **绿色为主**：操作成功、在线状态使用 Supabase 绿
3. **紫色强调**：特殊功能、高亮使用 Raycast 紫
4. **粉色告警**：危险、Critical 使用 Raycast 粉
5. **玻璃效果**：弹出层、提示框使用毛玻璃效果
6. **渐变点缀**：标题、数值使用绿→紫渐变增加视觉冲击力
