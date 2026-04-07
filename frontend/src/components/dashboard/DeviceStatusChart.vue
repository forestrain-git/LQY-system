<template>
  <div class="device-status-chart">
    <h3 class="chart-title">设备状态分布</h3>
    <div ref="chartRef" class="chart-container"></div>
    <div class="status-legend">
      <div v-for="item in statusData" :key="item.name" class="legend-item">
        <div class="legend-dot" :style="{ background: item.color }"></div>
        <span class="legend-name">{{ item.name }}</span>
        <span class="legend-value">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface StatusData {
  name: string
  value: number
  color: string
}

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

// 模拟设备状态数据
const statusData = ref<StatusData[]>([
  { name: '在线', value: 12, color: '#3ECF8E' },
  { name: '离线', value: 3, color: '#FF79C6' },
  { name: '维护中', value: 2, color: '#FFB86C' },
  { name: '已禁用', value: 1, color: '#6272A4' }
])

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)

    const option: EChartsOption = {
      backgroundColor: 'transparent',
      series: [{
        type: 'pie',
        radius: ['50%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#1C1C1C',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
            color: '#F8F8F2'
          }
        },
        labelLine: {
          show: false
        },
        data: statusData.value.map(item => ({
          value: item.value,
          name: item.name,
          itemStyle: { color: item.color }
        }))
      }]
    }

    chart.setOption(option)

    window.addEventListener('resize', () => {
      chart?.resize()
    })
  }
})
</script>

<style scoped>
.device-status-chart {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.chart-container {
  flex: 1;
  min-height: 200px;
}

.status-legend {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-name {
  font-size: 12px;
  color: var(--text-secondary);
  flex: 1;
}

.legend-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
</style>
