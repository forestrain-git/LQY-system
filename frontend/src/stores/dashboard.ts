import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SensorData } from '@/types'

export interface DataPoint {
  timestamp: string
  value: number
  deviceId: number
}

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const temperatureHistory = ref<DataPoint[]>([])
  const deviceStats = ref({
    total: 0,
    online: 0,
    offline: 0,
    maintenance: 0,
  })
  const alertStats = ref({
    total: 0,
    critical: 0,
    warning: 0,
    info: 0,
  })
  const dataRate = ref(0)
  const latestSensorData = ref<SensorData[]>([])

  // Getters
  const avgTemperature = computed(() => {
    if (temperatureHistory.value.length === 0) return 0
    const sum = temperatureHistory.value.reduce((acc, cur) => acc + cur.value, 0)
    return Number((sum / temperatureHistory.value.length).toFixed(1))
  })

  const onlineDeviceCount = computed(() => deviceStats.value.online)
  const todayAlertCount = computed(() => alertStats.value.total)

  // Actions
  const appendTemperatureData = (point: DataPoint) => {
    temperatureHistory.value.push(point)
    if (temperatureHistory.value.length > 30) {
      temperatureHistory.value.shift()
    }
  }

  const appendRealtimeData = (data: SensorData) => {
    latestSensorData.value.unshift(data)
    if (latestSensorData.value.length > 10) {
      latestSensorData.value.pop()
    }
  }

  const updateDeviceStats = (stats: typeof deviceStats.value) => {
    deviceStats.value = stats
  }

  const updateAlertStats = (stats: typeof alertStats.value) => {
    alertStats.value = stats
  }

  const setDataRate = (rate: number) => {
    dataRate.value = rate
  }

  return {
    temperatureHistory,
    deviceStats,
    alertStats,
    dataRate,
    latestSensorData,
    avgTemperature,
    onlineDeviceCount,
    todayAlertCount,
    appendTemperatureData,
    appendRealtimeData,
    updateDeviceStats,
    updateAlertStats,
    setDataRate,
  }
})
