import { ref, onUnmounted, onMounted } from 'vue'
import * as echarts from 'echarts'

export function useECharts(chartRef: ref<HTMLElement | null>) {
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

  onMounted(() => {
    window.addEventListener('resize', resizeChart)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', resizeChart)
    chartInstance?.dispose()
  })

  return {
    initChart,
    updateChart,
    resizeChart,
  }
}
