import { ref, onUnmounted } from 'vue'

export interface WebSocketMessage {
  type: 'sensor_data' | 'new_alert' | 'alert_updated' | 'ping'
  timestamp: string
  data: any
}

export function useWebSocket(url: string) {
  const ws = ref<WebSocket | null>(null)
  const status = ref<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const lastMessage = ref<WebSocketMessage | null>(null)
  const reconnectCount = ref(0)

  const MAX_RECONNECT = 5
  const RECONNECT_INTERVAL = 5000

  let reconnectTimer: number | null = null

  const connect = () => {
    if (ws.value?.readyState === WebSocket.OPEN) return

    status.value = 'connecting'

    try {
      ws.value = new WebSocket(url)

      ws.value.onopen = () => {
        status.value = 'connected'
        reconnectCount.value = 0
      }

      ws.value.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          lastMessage.value = message
        } catch (e) {
          console.error('WebSocket parse error:', e)
        }
      }

      ws.value.onclose = () => {
        status.value = 'disconnected'
        tryReconnect()
      }

      ws.value.onerror = (error) => {
        console.error('WebSocket error:', error)
        status.value = 'disconnected'
      }
    } catch (e) {
      console.error('WebSocket connection error:', e)
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
      console.error('Max reconnect attempts reached')
      return
    }

    reconnectCount.value++
    reconnectTimer = window.setTimeout(() => {
      connect()
    }, RECONNECT_INTERVAL)
  }

  const sendMessage = (data: any) => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    status,
    lastMessage,
    reconnectCount,
    connect,
    disconnect,
    sendMessage,
  }
}
