<template>
  <div class="recent-alerts">
    <div class="alerts-header">
      <h3 class="chart-title">最近告警</h3>
      <el-button text type="primary" size="small" @click="$router.push('/alerts')">
        查看全部
        <el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
    </div>

    <div class="alerts-list">
      <div
        v-for="alert in recentAlerts"
        :key="alert.id"
        class="alert-item"
        :class="`level-${alert.level}`"
      >
        <div class="alert-icon">
          <el-icon :size="20">
            <Warning v-if="alert.level === 'critical'" />
            <Bell v-else-if="alert.level === 'warning'" />
            <InfoFilled v-else />
          </el-icon>
        </div>
        <div class="alert-content">
          <div class="alert-title">{{ alert.message }}</div>
          <div class="alert-meta">
            <span class="device-name">{{ alert.device_name }}</span>
            <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
          </div>
        </div>
        <div class="alert-level" :class="`level-${alert.level}`">
          {{ levelText(alert.level) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Alert {
  id: number
  device_id: number
  device_name: string
  message: string
  level: 'critical' | 'warning' | 'info'
  created_at: string
}

// 模拟最近告警数据
const recentAlerts = ref<Alert[]>([
  {
    id: 1,
    device_id: 1,
    device_name: '压缩机-A01',
    message: '温度过高 (85°C)',
    level: 'critical',
    created_at: new Date(Date.now() - 5 * 60000).toISOString()
  },
  {
    id: 2,
    device_id: 2,
    device_name: '泵机-B02',
    message: '振动异常 (6.5 mm/s)',
    level: 'warning',
    created_at: new Date(Date.now() - 15 * 60000).toISOString()
  },
  {
    id: 3,
    device_id: 3,
    device_name: '风机-C03',
    message: '电流波动超过阈值',
    level: 'warning',
    created_at: new Date(Date.now() - 32 * 60000).toISOString()
  },
  {
    id: 4,
    device_id: 1,
    device_name: '压缩机-A01',
    message: '设备重启完成',
    level: 'info',
    created_at: new Date(Date.now() - 60 * 60000).toISOString()
  }
])

const levelText = (level: string) => {
  const map: Record<string, string> = {
    critical: '紧急',
    warning: '警告',
    info: '提示'
  }
  return map[level] || level
}

const formatTime = (time: string) => {
  const date = new Date(time)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 60000)

  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}分钟前`
  if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.recent-alerts {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.alerts-header {
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

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border-left: 3px solid transparent;
  transition: all 0.3s ease;
}

.alert-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.alert-item.level-critical {
  border-left-color: #FF79C6;
}

.alert-item.level-warning {
  border-left-color: #FFB86C;
}

.alert-item.level-info {
  border-left-color: #3ECF8E;
}

.alert-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
}

.level-critical .alert-icon {
  color: #FF79C6;
}

.level-warning .alert-icon {
  color: #FFB86C;
}

.level-info .alert-icon {
  color: #3ECF8E;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alert-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.device-name {
  color: var(--color-secondary);
}

.alert-level {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.alert-level.level-critical {
  background: rgba(255, 121, 198, 0.1);
  color: #FF79C6;
}

.alert-level.level-warning {
  background: rgba(255, 184, 108, 0.1);
  color: #FFB86C;
}

.alert-level.level-info {
  background: rgba(62, 207, 142, 0.1);
  color: #3ECF8E;
}
</style>