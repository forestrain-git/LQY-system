<template>
  <div class="realtime-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-actions">
        <el-radio-group v-model="selectedMetric" size="small">
          <el-radio-button label="temperature">温度</el-radio-button>
          <el-radio-button label="vibration">振动</el-radio-button>
          <el-radio-button label="current">电流</el-radio-button>
        </el-radio-group>
      </div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface Props {
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '实时数据趋势'
})

const chartRef = ref<HTMLElement>()
const selectedMetric = ref('temperature')
let chart: echarts.ECharts | null = null

// 模拟实时数据
const dataPoints = ref<Array<{ timestamp: number; value: number }>>([])
const maxDataPoints = 50

// 生成初始数据
const generateInitialData = () => {
  const now = Date.now()
  for (let i = maxDataPoints - 1; i >= 0; i--) {
    dataPoints.value.push({
      timestamp: now - i * 1000,
      value: generateValue(selectedMetric.value)
    })
  }
}

// 生成随机值
const generateValue = (metric: string) => {
  switch (metric) {
    case 'temperature': return 50 + Math.random() * 30 // 50-80°C
    case 'vibration': return 2 + Math.random() * 5 // 2-7 mm/s
    case 'current': return 10 + Math.random() * 15 // 10-25 A
    default: return Math.random() * 100
  }
}

// 获取单位
const getUnit = (metric: string) => {
  switch (metric) {
    case 'temperature': return '°C'
    case 'vibration': return 'mm/s'
    case 'current': return 'A'
    default: return ''
  }
}

// 获取颜色
const getColor = (metric: string) => {
  switch (metric) {
    case 'temperature': return '#FF79C6'
    case 'vibration': return '#BD93F9'
    case 'current': return '#3ECF8E'
    default: return '#3ECF8E'
  }
}

// 更新图表
const updateChart = () => {
  if (!chart) return

  const xData = dataPoints.value.map(p =>
    new Date(p.timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  )
  const yData = dataPoints.value.map(p => p.value)

  const option: EChartsOption = {
    backgroundColor: 'transparent',
    grid: {
      left: 60,
      right: 20,
      top: 20,
      bottom: 40
    },
    xAxis: {
      type: 'category',
      data: xData,
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#666', fontSize: 10 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      name: getUnit(selectedMetric.value),
      nameTextStyle: { color: '#999' },
      axisLine: { show: false },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#222', type: 'dashed' } }
    },
    series: [{
      data: yData,
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: {
        color: getColor(selectedMetric.value),
        width: 2
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: getColor(selectedMetric.value) + '40' },
          { offset: 1, color: getColor(selectedMetric.value) + '00' }
        ])
      }
    }],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(28, 28, 28, 0.9)',
      borderColor: '#333',
      textStyle: { color: '#F8F8F2' },
      formatter: (params: any) => {
        const p = params[0]
        return `${p.name}<br/>${p.value.toFixed(2)} ${getUnit(selectedMetric.value)}`
      }
    }
  }

  chart.setOption(option)
}

// 定时更新数据
let updateTimer: number | null = null

const startRealtimeUpdate = () => {
  updateTimer = window.setInterval(() => {
    const now = Date.now()
    const newValue = generateValue(selectedMetric.value)

    dataPoints.value.push({
      timestamp: now,
      value: newValue
    })

    if (dataPoints.value.length > maxDataPoints) {
      dataPoints.value.shift()
    }

    updateChart()
  }, 1000)
}

const stopRealtimeUpdate = () => {
  if (updateTimer) {
    clearInterval(updateTimer)
    updateTimer = null
  }
}

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    generateInitialData()
    updateChart()
    startRealtimeUpdate()

    window.addEventListener('resize', () => {
      chart?.resize()
    })
  }
})

onUnmounted(() => {
  stopRealtimeUpdate()
  chart?.dispose()
})

watch(selectedMetric, () => {
  dataPoints.value = []
  generateInitialData()
  updateChart()
})
</script>

<style scoped>
.realtime-chart {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-container {
  height: 300px;
}
</style>
