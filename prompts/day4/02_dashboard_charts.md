# Day 4 - Prompt 2: 仪表盘实时图表

**时机**：布局框架完成后执行
**预期耗时**：Claude生成25分钟，你Review 15分钟
**人工决策**：确认图表设计，实时数据流正常工作

---

## 输入Prompt

```text
请实现仪表盘页面，包含实时跳动的数据图表。

【仪表盘页面】（src/views/Dashboard.vue）

整体布局（从上往下）：
1. 统计概览卡片行（4列）
2. 实时趋势图（温度曲线，占据整行高度300px）
3. 设备状态分布 + 告警统计（左右两列）
4. 实时数据表格（最近10条传感器数据）

【统计概览卡片】（src/components/dashboard/StatCard.vue）

4个卡片（Supabase+Raycast配色）：
- 在线设备数（图标：Monitor，颜色：#3ECF8E - Supabase绿）
- 今日告警数（图标：Warning，颜色：#FF79C6 - Raycast粉）
- 平均温度（图标：Temperature，颜色：#FFB86C - Raycast橙）
- 数据接收速率（图标：DataLine，颜色：#BD93F9 - Raycast紫）

每个卡片样式（深色主题）：
- 背景：#1C1C1C（Supabase灰）
- 边框：1px solid #252525
- 圆角：12px
- 阴影：0 4px 20px rgba(0, 0, 0, 0.3)
- 大字号显示数值（font-size: 32px，渐变文字：绿→紫）
- 下方显示标签（font-size: 14px，#B0B0B0）
- 右侧显示图标（font-size: 48px，透明度0.1）
- hover效果：
  * transform: translateY(-2px)
  * box-shadow: 0 8px 30px rgba(62, 207, 142, 0.15)（绿色微光）
  * border-color: rgba(62, 207, 142, 0.2)
- 数值变化时有动画（数字滚动）

数据从dashboardStore获取，每5秒更新一次

【实时温度趋势图】（src/components/charts/RealtimeTemperatureChart.vue）

使用ECharts的line chart（深色主题适配）：
- X轴：时间（HH:mm:ss格式）
- Y轴：温度（℃）
- 3条线：平均温度、最高温度、最低温度
- 数据点：最近5分钟，每10秒一个点（最多30个点）
- 自动滚动（新数据从右侧推入，旧数据从左侧移出）

ECharts配色方案（Supabase+Raycast）：
```javascript
const chartOption = {
  backgroundColor: 'transparent',
  // 线条颜色：绿、紫、青
  color: ['#3ECF8E', '#BD93F9', '#8BE9FD'],
  
  xAxis: {
    axisLine: { lineStyle: { color: '#333333' } },
    axisLabel: { color: '#B0B0B0' },
    splitLine: { show: false }
  },
  
  yAxis: {
    axisLine: { lineStyle: { color: '#333333' } },
    axisLabel: { color: '#B0B0B0' },
    splitLine: { lineStyle: { color: '#252525', type: 'dashed' } }
  },
  
  // 温度线使用渐变
  series: [{
    lineStyle: {
      width: 3,
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [
          { offset: 0, color: '#3ECF8E' },   // 绿色（正常）
          { offset: 0.5, color: '#FFB86C' }, // 橙色（警告）
          { offset: 1, color: '#FF79C6' }    // 粉色（危险）
        ]
      }
    },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(62, 207, 142, 0.3)' },
          { offset: 1, color: 'rgba(62, 207, 142, 0.05)' }
        ]
      }
    }
  }],
  
  // 提示框样式
  tooltip: {
    backgroundColor: 'rgba(28, 28, 28, 0.95)',
    borderColor: '#333333',
    textStyle: { color: '#F8F8F2' },
    extraCssText: 'backdrop-filter: blur(4px);'
  }
}
```

技术细节：
- 使用ECharts的appendData或setOption更新
- 曲线平滑（smooth: true）
- 区域填充（areaStyle，渐变填充）
- 提示框显示具体数值（毛玻璃效果）
- 图例可点击隐藏/显示线条
- 网格线使用虚线，颜色#252525

数据更新频率：每10秒（与模拟器同步）

【仪表盘图表】（src/components/charts/DeviceGaugeChart.vue）

显示当前平均温度仪表盘（深色主题）：
- 范围：0-100℃
- 分段颜色（Supabase+Raycast配色）：
  * 0-50℃：#3ECF8E（Supabase绿，正常）
  * 50-80℃：#FFB86C（Raycast橙，警告）
  * 80-100℃：#FF79C6（Raycast粉，危险）
- 指针指向当前值
- 中心显示数值（大字体，渐变文字：绿→紫）
- 背景透明，坐标轴文字#B0B0B0
- 刻度线颜色#333333

【设备状态分布】（src/components/charts/DeviceStatusChart.vue）

使用ECharts的pie chart（深色主题配色）：
- 展示设备状态分布
- 配色方案（Supabase+Raycast）：
  * 在线：#3ECF8E（Supabase绿）
  * 离线：#FF79C6（Raycast粉）
  * 维护：#FFB86C（Raycast橙）
  * 禁用：#6272A4（Raycast灰蓝）
- 中心显示设备总数（渐变文字：绿→紫）
- 标签文字颜色：#B0B0B0
- 点击扇形可筛选设备列表（预留交互）

【告警级别统计】（src/components/charts/AlertLevelChart.vue）

使用ECharts的bar chart（深色主题）：
- X轴：critical / warning / info
- Y轴：数量
- 颜色区分（Supabase+Raycast）：
  * critical：#FF79C6（Raycast粉）
  * warning：#FFB86C（Raycast橙）
  * info：#8BE9FD（Raycast青）
- 柱状图圆角：borderRadius: [4, 4, 0, 0]
- 坐标轴颜色：#333333
- 标签文字：#B0B0B0
- 显示今日各级别告警数量

【实时数据表格】（src/components/dashboard/RealtimeDataTable.vue）

展示最近10条传感器数据（深色主题表格）：
- 列：时间、设备名称、温度、振动、电流、状态
- 表头样式：
  * 背景：#1C1C1C（Supabase灰）
  * 文字：#B0B0B0，粗体
  * 底部边框：2px solid rgba(62, 207, 142, 0.3)（绿色微光）
- 表身样式：
  * 背景：#0F0F0F（Raycast黑）
  * 文字：#F8F8F2
  * 行底部边框：1px solid #252525
  * 悬停背景：#1C1C1C
- 状态列用Tag显示（Supabase+Raycast配色）：
  * 正常：背景rgba(62, 207, 142, 0.15)，文字#3ECF8E（Supabase绿）
  * 异常：背景rgba(255, 121, 198, 0.15)，文字#FF79C6（Raycast粉）
- 数据实时更新（新数据置顶，旧数据移除）
- 行高亮动画（新加入的行闪烁提示，使用绿色微光）

表格列定义：
```typescript
interface TableColumn {
  prop: string
  label: string
  width?: number
  formatter?: (row: any) => string
}

const columns: TableColumn[] = [
  { prop: 'timestamp', label: '时间', width: 180, formatter: formatDateTime },
  { prop: 'device_name', label: '设备', width: 150 },
  { prop: 'temperature', label: '温度(℃)', width: 100 },
  { prop: 'vibration', label: '振动(mm/s)', width: 120 },
  { prop: 'current', label: '电流(A)', width: 100 },
  { prop: 'status', label: '状态' },
]
```

【实时数据组合式函数】（src/composables/useRealtimeData.ts）

封装实时数据获取逻辑：
```typescript
export function useRealtimeData() {
  // 状态
  const temperatureHistory = ref<DataPoint[]>([])  // 温度历史
  const latestSensorData = ref<SensorData[]>([])   // 最新10条数据
  const deviceStats = ref<DeviceStats>({           // 设备统计
    total: 0,
    online: 0,
    offline: 0,
    maintenance: 0,
  })
  const alertStats = ref<AlertStats>({             // 告警统计
    total: 0,
    critical: 0,
    warning: 0,
    info: 0,
  })

  // 方法
  const fetchDeviceStats = async () => { }
  const fetchAlertStats = async () => { }
  const processNewSensorData = (data: SensorData) => { }
  
  // 定时刷新（5秒）
  useIntervalFn(fetchDeviceStats, 5000)
  useIntervalFn(fetchAlertStats, 5000)

  return {
    temperatureHistory,
    latestSensorData,
    deviceStats,
    alertStats,
  }
}
```

【仪表盘Store】（src/stores/dashboard.ts）

```typescript
export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const temperatureHistory = ref<DataPoint[]>([])
  const deviceStats = ref({ total: 0, online: 0, offline: 0, maintenance: 0 })
  const alertStats = ref({ total: 0, critical: 0, warning: 0, info: 0 })
  const dataRate = ref(0)  // 每秒数据条数
  
  // Getters
  const avgTemperature = computed(() => {
    if (temperatureHistory.value.length === 0) return 0
    const sum = temperatureHistory.value.reduce((acc, cur) => acc + cur.value, 0)
    return (sum / temperatureHistory.value.length).toFixed(1)
  })
  
  // Actions
  const appendTemperatureData = (point: DataPoint) => {
    temperatureHistory.value.push(point)
    if (temperatureHistory.value.length > 30) {
      temperatureHistory.value.shift()  // 保持最多30个点
    }
  }
  
  const updateStats = async () => {
    // 调用API获取最新统计
  }
  
  return {
    temperatureHistory,
    deviceStats,
    alertStats,
    dataRate,
    avgTemperature,
    appendTemperatureData,
    updateStats,
  }
})
```

【ECharts封装】（src/composables/useECharts.ts）

封装ECharts初始化和响应式处理：
```typescript
export function useECharts(chartRef: Ref<HTMLElement | null>) {
  let chartInstance: echarts.ECharts | null = null
  
  const initChart = (options: echarts.EChartsOption) => {
    if (chartRef.value) {
      chartInstance = echarts.init(chartRef.value)
      chartInstance.setOption(options)
    }
  }
  
  const updateChart = (options: echarts.EChartsOption) => {
    chartInstance?.setOption(options)
  }
  
  const resizeChart = () => {
    chartInstance?.resize()
  }
  
  // 监听窗口大小变化
  useEventListener(window, 'resize', resizeChart)
  
  // 组件卸载时销毁
  onUnmounted(() => {
    chartInstance?.dispose()
  })
  
  return {
    initChart,
    updateChart,
    resizeChart,
  }
}
```

【样式优化 - 深色主题】

1. 卡片样式（Supabase+Raycast）：
   - 背景：#1C1C1C（Supabase灰）
   - 边框：1px solid #252525
   - 圆角：12px
   - 阴影：0 4px 20px rgba(0, 0, 0, 0.3)
   - 内边距：20px
   - 悬停效果：translateY(-2px) + 绿色微光阴影

2. 图表容器：
   - 高度固定（Temperature: 300px, Gauge: 250px）
   - 背景：transparent（透出页面背景#0F0F0F）
   - 标题：16px粗体，#F8F8F2，底部16px边距
   - 副标题/标签：#B0B0B0

3. 响应式：
   - lg: 4列统计卡片 → 2列
   - md: 2列统计卡片 → 1列，图表堆叠
   - sm: 单列布局

【数据流测试】

验证实时数据流：
1. 启动后端服务（docker-compose up）
2. 启动设备模拟器（python3 device_simulator.py）
3. 前端页面应该：
   - 每10秒更新温度曲线（右侧推入新点）
   - 统计卡片数值变化
   - 实时表格追加新行
   - 数据速率显示不为0

【性能优化】

- ECharts使用appendData增量更新（而非全量setOption）
- 表格使用虚拟滚动（如数据量大）
- 使用shallowRef存储大数据对象（避免深层响应式）
- 使用requestAnimationFrame优化动画
```

---

## 预期输出

```
生成文件：
- src/views/Dashboard.vue [完成]
- src/components/dashboard/StatCard.vue [完成]
- src/components/dashboard/RealtimeDataTable.vue [完成]
- src/components/charts/RealtimeTemperatureChart.vue [完成]
- src/components/charts/DeviceGaugeChart.vue [完成]
- src/components/charts/DeviceStatusChart.vue [完成]
- src/components/charts/AlertLevelChart.vue [完成]
- src/composables/useRealtimeData.ts [完成]
- src/composables/useECharts.ts [完成]
- src/stores/dashboard.ts [完成]

界面效果：
- 顶部4个统计卡片，显示在线设备、告警数、温度、数据速率
- 中间温度曲线图，每10秒右侧推入新数据点
- 下方左侧仪表盘，右侧柱状图
- 底部实时数据表格，显示最近10条数据
- 所有数据每5-10秒自动刷新
```

---

## 你的决策

- [ ] 图表能正常显示和更新 → 继续Prompt 3（WebSocket集成）
- [ ] 颜色方案想调整 → 提供新的ECharts配色
- [ ] 需要更多图表类型 → 告诉Claude添加

---

## 手工验证

```bash
# 1. 启动后端
cd backend && docker-compose up -d

# 2. 启动模拟器
cd simulator && python3 device_simulator.py --count 5

# 3. 启动前端
cd frontend && npm run dev

# 4. 访问 http://localhost:5173
# 验证：
# - 温度曲线每10秒更新
# - 统计卡片数值变化
# - 实时表格追加数据
```

## 调试技巧

```typescript
// 在Dashboard.vue中添加调试信息
onMounted(() => {
  console.log('Dashboard mounted')
  // 模拟数据更新
  setInterval(() => {
    console.log('Temperature history:', temperatureHistory.value)
  }, 5000)
})
```
