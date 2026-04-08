<template>
  <div class="app-header">
    <div class="logo">
      <span class="title">龙泉驿环卫智能体</span>
    </div>
    <div class="actions">
      <!-- 未读告警 Badge -->
      <el-badge
        :value="alertsStore.unreadAlerts.length"
        :hidden="alertsStore.unreadAlerts.length === 0"
        class="alert-badge"
        type="danger"
      >
        <el-button text class="action-btn" @click="$router.push('/alerts')">
          <el-icon :size="20"><Bell /></el-icon>
        </el-button>
      </el-badge>

      <!-- 当前时间 -->
      <div class="current-time">
        <el-icon><Clock /></el-icon>
        <span>{{ currentTime }}</span>
      </div>

      <ConnectionStatus />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAlertsStore } from '@/stores/alerts'
import { Bell, Clock } from '@element-plus/icons-vue'
import ConnectionStatus from '@/components/common/ConnectionStatus.vue'

const alertsStore = useAlertsStore()

// 当前时间
const currentTime = ref('')
let timeInterval: number | null = null

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  updateTime()
  timeInterval = window.setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, #3ECF8E 0%, #BD93F9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  color: var(--text-secondary);
  font-size: 20px;
}

.action-btn:hover {
  color: var(--color-primary);
}

.alert-badge :deep(.el-badge__content) {
  background-color: #FF79C6;
  border: none;
}

.current-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-family: 'Courier New', monospace;
}

.current-time .el-icon {
  color: var(--color-primary);
}
</style>
