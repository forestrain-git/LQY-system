# Day 4 - Prompt 3: WebSocket实时数据集成

**时机**：仪表盘图表完成后执行
**预期耗时**：Claude生成20分钟，你Review 10分钟
**人工决策**：确认实时推送正常工作，连接稳定

---

## 输入Prompt

```text
请实现WebSocket实时数据集成，让前端能接收后端的实时推送。

【WebSocket组合式函数】（src/composables/useWebSocket.ts）

封装完整的WebSocket管理：

```typescript
import { ref, onUnmounted } from 'vue'

export interface WebSocketMessage {
  type: 'sensor_data' | 'new_alert' | 'alert_updated' | 'ping'
  timestamp: string
  data: any
}

export function useWebSocket(url: string) {
  // 状态
  const ws = ref<WebSocket | null>(null)
  const status = ref<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const lastMessage = ref<WebSocketMessage | null>(null)
  const reconnectCount = ref(0)
  const messageHistory = ref<WebSocketMessage[]>([])
  
  // 配置
  const MAX_RECONNECT = 5
  const RECONNECT_INTERVAL = 5000
  const HEARTBEAT_INTERVAL = 30000
  
  let reconnectTimer: number | null = null
  let heartbeatTimer: number | null = null
  
  // 连接
  const connect = () => {
    if (ws.value?.readyState === WebSocket.OPEN) return
    
    status.value = 'connecting'
    console.log('[WebSocket] Connecting to:', url)
    
    try {
      ws.value = new WebSocket(url)
      
      ws.value.onopen = () => {
        status.value = 'connected'
        reconnectCount.value = 0
        console.log('[WebSocket] Connected')
        
        // 启动心跳
        startHeartbeat()
        
        // 订阅主题
        sendMessage({
          action: 'subscribe',
          topics: ['sensors', 'alerts']
        })
      }
      
      ws.value.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          lastMessage.value = message
          messageHistory.value.push(message)
          
          // 只保留最近100条
          if (messageHistory.value.length > 100) {
            messageHistory.value.shift()
          }
          
          // 处理消息
          handleMessage(message)
        } catch (e) {
          console.error('[WebSocket] Parse error:', e)
        }
      }
      
      ws.value.onclose = () => {
        status.value = 'disconnected'
        console.log('[WebSocket] Disconnected')
        stopHeartbeat()
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
  
  // 断开连接
  const disconnect = () => {
    stopHeartbeat()
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
  }
  
  // 重连机制
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
  
  // 心跳保活
  const startHeartbeat = () => {
    heartbeatTimer = window.setInterval(() => {
      if (ws.value?.readyState === WebSocket.OPEN) {
        sendMessage({ type: 'ping', timestamp: new Date().toISOString() })
      }
    }, HEARTBEAT_INTERVAL)
  }
  
  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }
  
  // 发送消息
  const sendMessage = (data: any) => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
    }
  }
  
  // 消息处理（可被子类覆盖）
  const handleMessage = (message: WebSocketMessage) => {
    // 默认处理，外部可通过watch lastMessage来响应
  }
  
  // 组件卸载时清理
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    status,
    lastMessage,
    messageHistory,
    reconnectCount,
    connect,
    disconnect,
    sendMessage,
  }
}
```

【WebSocket Store集成】（src/stores/websocket.ts）

全局管理WebSocket状态和消息分发：

```typescript
export const useWebSocketStore = defineStore('websocket', () => {
  // State
  const isConnected = ref(false)
  const connectionStatus = ref<'online' | 'offline' | 'connecting'>('offline')
  const lastSensorData = ref<SensorData | null>(null)
  const unreadAlerts = ref<Alert[]>([])
  
  // Actions
  const connect = () => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
    // 初始化WebSocket连接
  }
  
  const handleNewSensorData = (data: SensorData) => {
    lastSensorData.value = data
    // 分发到dashboard store
    const dashboardStore = useDashboardStore()
    dashboardStore.appendRealtimeData(data)
  }
  
  const handleNewAlert = (alert: Alert) => {
    unreadAlerts.value.push(alert)
    // 显示通知
    ElNotification({
      title: `${alert.level === 'critical' ? '【严重】' : '【警告】'}设备告警`,
      message: `${alert.device_name}: ${alert.message}`,
      type: alert.level === 'critical' ? 'error' : 'warning',
      duration: 0,  // 不自动关闭
    })
  }
  
  return {
    isConnected,
    connectionStatus,
    lastSensorData,
    unreadAlerts,
    connect,
    handleNewSensorData,
    handleNewAlert,
  }
})
```

【实时数据Hook增强】（更新src/composables/useRealtimeData.ts）

添加WebSocket数据监听：

```typescript
export function useRealtimeData() {
  const websocketStore = useWebSocketStore()
  const dashboardStore = useDashboardStore()
  
  // 监听WebSocket消息
  watch(() => websocketStore.lastSensorData, (newData) => {
    if (newData) {
      // 更新实时数据
      dashboardStore.appendRealtimeData(newData)
      
      // 更新温度历史
      dashboardStore.appendTemperatureData({
        timestamp: newData.timestamp,
        value: newData.temperature,
        deviceId: newData.device_id,
      })
    }
  }, { immediate: true })
  
  // 原有HTTP轮询作为fallback
  // ...
  
  return {
    // ...
  }
}
```

【连接状态组件】（更新src/components/common/ConnectionStatus.vue）

完整实现：

```vue
<template>
  <div class="connection-status" @click="handleClick">
    <el-tooltip :content="tooltipText" placement="bottom">
      <div class="status-wrapper">
        <div class="status-dot" :class="statusClass"></div>
        <span class="status-text">{{ statusText }}</span>
        <el-icon v-if="status === 'disconnected'" class="retry-icon">
          <RefreshRight />
        </el-icon>
      </div>
    </el-tooltip>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWebSocketStore } from '@/stores/websocket'

const wsStore = useWebSocketStore()

const statusClass = computed(() => ({
  'status-online': wsStore.connectionStatus === 'online',
  'status-offline': wsStore.connectionStatus === 'offline',
  'status-connecting': wsStore.connectionStatus === 'connecting',
}))

const statusText = computed(() => {
  switch (wsStore.connectionStatus) {
    case 'online': return '已连接'
    case 'offline': return '已断开'
    case 'connecting': return '连接中...'
    default: return '未知'
  }
})

const tooltipText = computed(() => {
  if (wsStore.connectionStatus === 'offline') {
    return '点击重新连接'
  }
  return `WebSocket${statusText.value}`
})

const handleClick = () => {
  if (wsStore.connectionStatus === 'offline') {
    wsStore.connect()
  }
}
</script>

<style scoped>
.connection-status {
  cursor: pointer;
  user-select: none;
}

.status-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: all 0.3s;
}

.status-online {
  background-color: #67c23a;
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.3);
}

.status-offline {
  background-color: #f56c6c;
}

.status-connecting {
  background-color: #e6a23c;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.retry-icon {
  font-size: 14px;
  color: #909399;
}
</style>
```

【全局消息通知】（src/utils/notification.ts）

封装告警通知：

```typescript
import { ElNotification } from 'element-plus'

export function showAlertNotification(alert: Alert) {
  const typeMap = {
    critical: 'error',
    warning: 'warning',
    info: 'info',
  }
  
  const titleMap = {
    critical: '【严重告警】',
    warning: '【警告】',
    info: '【提示】',
  }
  
  ElNotification({
    title: `${titleMap[alert.level]}${alert.device_name}`,
    message: alert.message,
    type: typeMap[alert.level] as any,
    duration: alert.level === 'critical' ? 0 : 5000,
    position: 'top-right',
  })
}

export function showConnectionNotification(status: 'connected' | 'disconnected') {
  if (status === 'connected') {
    ElNotification.success({
      title: '连接恢复',
      message: 'WebSocket连接已恢复',
      duration: 3000,
    })
  } else {
    ElNotification.error({
      title: '连接断开',
      message: 'WebSocket连接已断开，正在重试...',
      duration: 5000,
    })
  }
}
```

【App.vue集成】（src/App.vue）

全局初始化WebSocket：

```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useWebSocketStore } from '@/stores/websocket'

const wsStore = useWebSocketStore()

onMounted(() => {
  // 应用启动时连接WebSocket
  wsStore.connect()
})
</script>
```

【消息调试面板】（可选，src/components/debug/WebSocketDebug.vue）

开发调试用，显示最近20条WebSocket消息：
- 消息类型
- 时间戳
- 数据预览（可展开）
- 清空按钮

【降级策略】

当WebSocket不可用时：
1. 自动切换到HTTP轮询（5秒间隔）
2. 提示用户"实时推送不可用，使用轮询模式"
3. 继续尝试重连WebSocket

在useRealtimeData中实现：
```typescript
const startHttpFallback = () => {
  // 启动HTTP轮询
  useIntervalFn(fetchLatestData, 5000)
}

// WebSocket断开时启动fallback
watch(() => wsStore.connectionStatus, (status) => {
  if (status === 'offline') {
    startHttpFallback()
  }
})
```

【测试验证】

1. 正常连接测试：
   - 启动后端和前端
   - 观察Header状态指示器变为绿色
   - 运行模拟器，观察数据实时更新

2. 断开重连测试：
   - 停止后端服务
   - 观察状态变为红色，显示"已断开"
   - 重新启动后端
   - 观察自动重连成功（状态变绿）

3. 告警通知测试：
   - 运行模拟器产生异常数据
   - 观察浏览器右上角弹出告警通知
   - 点击通知可跳转到告警详情页

4. 性能测试：
   - 模拟器10台设备，10秒间隔
   - 前端运行30分钟
   - 观察内存占用是否稳定增长
   - 观察是否有内存泄漏
```

---

## 预期输出

```
生成/更新文件：
- src/composables/useWebSocket.ts [创建]
- src/stores/websocket.ts [创建]
- src/components/common/ConnectionStatus.vue [更新]
- src/utils/notification.ts [创建]
- src/App.vue [更新]
- src/composables/useRealtimeData.ts [更新]

功能效果：
- Header显示WebSocket连接状态（绿/红/黄）
- 模拟器数据实时推送到前端（无需轮询）
- 新告警弹出Element Plus通知
- 断线自动重连（最多5次）
- 心跳保活机制
```

---

## 你的决策

- [ ] WebSocket推送正常 → 继续Prompt 4（告警管理界面）
- [ ] 连接不稳定 → 调整重连策略或心跳间隔
- [ ] 需要消息历史 → 添加调试面板

---

## 手工验证

```bash
# 1. 启动后端
cd backend && docker-compose up -d

# 2. 启动前端
cd frontend && npm run dev

# 3. 访问 http://localhost:5173
# 检查Header状态指示器（应该变绿色）

# 4. 启动模拟器
cd simulator && python3 device_simulator.py

# 5. 验证：
# - 状态指示器：绿色
# - 温度曲线：实时更新（无需刷新页面）
# - 模拟器产生异常时，弹出告警通知

# 6. 测试断线重连：
# - 停止后端：docker-compose stop backend
# - 观察状态变红色
# - 重新启动后端
# - 观察状态自动恢复绿色
```
