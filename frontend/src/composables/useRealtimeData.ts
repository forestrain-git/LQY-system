import { ref, watch } from 'vue'
import { useWebSocketStore } from '@/stores/websocket'
import { useDashboardStore } from '@/stores/dashboard'

export function useRealtimeData() {
  const wsStore = useWebSocketStore()
  const dashboardStore = useDashboardStore()

  // 监听WebSocket消息
  watch(
    () => wsStore.lastSensorData,
    (newData) => {
      if (newData) {
        dashboardStore.appendRealtimeData(newData)
        dashboardStore.appendTemperatureData({
          timestamp: newData.timestamp,
          value: newData.temperature,
          deviceId: newData.device_id,
        })
      }
    },
    { immediate: true }
  )

  return {
    lastSensorData: wsStore.lastSensorData,
    unreadAlerts: wsStore.unreadAlerts,
  }
}
