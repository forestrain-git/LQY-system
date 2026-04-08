<template>
  <div class="equipment-view">
    <div class="page-header">
      <h1 class="page-title">设备管理</h1>
      <p class="page-subtitle">管理所有环卫设备，监控设备状态和性能</p>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-icon" :class="stat.iconClass">
          <component :is="stat.icon" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <div class="equipment-list">
      <div class="list-header">
        <h2>设备列表</h2>
        <button class="btn-primary">+ 添加设备</button>
      </div>
      
      <div class="list-content">
        <div class="equipment-item" v-for="item in equipmentList" :key="item.id">
          <div class="item-info">
            <div class="item-name">{{ item.name }}</div>
            <div class="item-meta">编号: {{ item.code }} | 类型: {{ item.type }}</div>
          </div>
          <div class="item-status" :class="'status-' + item.status">
            {{ item.statusText }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Monitor, CheckCircle, AlertTriangle, Settings } from 'lucide-vue-next'

const stats = ref([
  { icon: Monitor, iconClass: 'icon-blue', value: '24', label: '设备总数' },
  { icon: CheckCircle, iconClass: 'icon-green', value: '22', label: '正常运行' },
  { icon: AlertTriangle, iconClass: 'icon-orange', value: '1', label: '需要维护' },
  { icon: Settings, iconClass: 'icon-purple', value: '1', label: '维修中' }
])

const equipmentList = ref([
  { id: 1, name: '清扫车-001', code: 'SC-001', type: '清扫车', status: 'normal', statusText: '正常运行' },
  { id: 2, name: '洒水车-003', code: 'SS-003', type: '洒水车', status: 'normal', statusText: '正常运行' },
  { id: 3, name: '垃圾压缩车-007', code: 'YS-007', type: '压缩车', status: 'warning', statusText: '需要维护' },
  { id: 4, name: '扫地机器人-A12', code: 'RB-A12', type: '机器人', status: 'normal', statusText: '正常运行' },
  { id: 5, name: '垃圾收集车-B05', code: 'SJ-B05', type: '收集车', status: 'error', statusText: '维修中' }
])
</script>

<style scoped>
/* 高对比度强制样式 */
.equipment-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
  padding: 24px;
  color: #f8fafc;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #f8fafc !important;
  margin-bottom: 8px;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
}

.page-subtitle {
  font-size: 14px;
  color: #94a3b8 !important;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
  border: 1px solid rgba(148, 163, 184, 0.2) !important;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.icon-blue { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); }
.icon-green { background: linear-gradient(135deg, #22c55e 0%, #15803d 100%); }
.icon-orange { background: linear-gradient(135deg, #f97316 0%, #c2410c 100%); }
.icon-purple { background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); }

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #f8fafc !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.stat-label {
  font-size: 14px;
  color: #94a3b8 !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.equipment-list {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
  border: 1px solid rgba(148, 163, 184, 0.2) !important;
  border-radius: 12px;
  padding: 24px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h2 {
  font-size: 20px;
  color: #f8fafc !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.btn-primary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
  color: white !important;
  border: none !important;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.equipment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(15, 23, 42, 0.5) !important;
  border: 1px solid rgba(148, 163, 184, 0.1) !important;
  border-radius: 8px;
  margin-bottom: 12px;
}

.item-name {
  font-size: 16px;
  font-weight: 600;
  color: #f8fafc !important;
  margin-bottom: 4px;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.item-meta {
  font-size: 13px;
  color: #64748b !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.item-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.status-normal {
  background: rgba(34, 197, 94, 0.2) !important;
  color: #22c55e !important;
}

.status-warning {
  background: rgba(249, 115, 22, 0.2) !important;
  color: #f97316 !important;
}

.status-error {
  background: rgba(239, 68, 68, 0.2) !important;
  color: #ef4444 !important;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
