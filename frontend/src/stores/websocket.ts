import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SensorData, Alert } from '@/types'

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected'

export const useWebSocketStore = defineStore('websocket', () => {
  // State
  const ws = ref<WebSocket | null>(null)
  const status = ref<ConnectionStatus>('disconnected')
  const lastMessage = ref<any>(null)
  const reconnectCount = ref(0)
  const lastSensorData = ref<SensorData | null>(null)
  const unreadAlerts = ref<Alert[]>([])
  
  // Getters
  const isConnected = computed(() => status.value === 'connected')
  const connectionStatus = computed(() => {
    switch (status.value) {
      case 'connected': return 'online'
      case 'connecting': return 'connecting'
      case 'disconnected': return 'offline'
      default: return 'offline'
    }
  })
  
  // 配置
  const MAX_RECONNECT = 5
  const RECONNECT_INTERVAL = 5000
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
  
  let reconnectTimer: number | null = null
  
  // Actions
  const connect = () => {
    if (ws.value?.readyState === WebSocket.OPEN) return
    
    status.value = 'connecting'
    console.log('[WebSocket] Connecting to:', WS_URL)
    
    try {
      ws.value = new WebSocket(WS_URL)
      
      ws.value.onopen = () => {
        status.value = 'connected'
        reconnectCount.value = 0
        console.log('[WebSocket] Connected')
      }
      
      ws.value.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          lastMessage.value = message
          
          // 处理消息
          if (message.type === 'sensor_data') {
            lastSensorData.value = message.data
          } else if (message.type === 'new_alert') {
            unreadAlerts.value.push(message.data)
          }
        } catch (e) {
          console.error('[WebSocket] Parse error:', e)
        }
      }
      
      ws.value.onclose = () => {
        status.value = 'disconnected'
        console.log('[WebSocket] Disconnected')
        tryReconnect()
      }
      
      ws.value.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        status.value = 'disconnected'
      }
    } catch (e) {
      console.error('[WebSocket] Connection error:', e)
      status.value = 'disconnected'
      tryReconnect()
    }
  }
  
  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
  }
  
  const tryReconnect = () => {
    if (reconnectCount.value >= MAX_RECONNECT) {
      console.error('[WebSocket] Max reconnect attempts reached')
      return
    }
    
    reconnectCount.value++
    console.log(`[WebSocket] Reconnecting in ${RECONNECT_INTERVAL}ms (attempt ${reconnectCount.value})`)
    
    reconnectTimer = window.setTimeout(() => {
      connect()
    }, RECONNECT_INTERVAL)
  }
  
  const clearUnreadAlerts = () => {
    unreadAlerts.value = []
  }
  
  return {
    status,
    lastMessage,
    reconnectCount,
    lastSensorData,
    unreadAlerts,
    isConnected,
    connectionStatus,
    connect,
    disconnect,
    clearUnreadAlerts,
  }
})
