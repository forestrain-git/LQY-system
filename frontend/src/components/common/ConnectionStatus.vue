<template>
  <div class="connection-status">
    <div class="status-wrapper" @click="handleClick">
      <div class="status-dot" :class="statusClass"></div>
      <span class="status-text">{{ statusText }}</span>
    </div>
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

const handleClick = () => {
  if (wsStore.connectionStatus === 'offline') {
    wsStore.connect()
  }
}
</script>

<style scoped>
.connection-status {
  cursor: pointer;
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
  background-color: #3ECF8E;
  box-shadow: 0 0 10px rgba(62, 207, 142, 0.4);
}

.status-offline {
  background-color: #FF79C6;
}

.status-connecting {
  background-color: #FFB86C;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 12px;
  color: #B0B0B0;
}
</style>
