<template>
  <div class="alert-list">
    <div class="page-header">
      <h1 class="page-title">告警中心</h1>
      <div class="header-actions">
        <el-button @click="refreshAlerts">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-item critical">
        <div class="stat-value">{{ criticalCount }}</div>
        <div class="stat-label">紧急告警</div>
      </div>
      <div class="stat-item warning">
        <div class="stat-value">{{ warningCount }}</div>
        <div class="stat-label">警告</div>
      </div>
      <div class="stat-item info">
        <div class="stat-value">{{ infoCount }}</div>
        <div class="stat-label">提示</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ totalCount }}</div>
        <div class="stat-label">告警总数</div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-radio-group v-model="filterStatus" size="default">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="active">未处理</el-radio-button>
        <el-radio-button label="acknowledged">已确认</el-radio-button>
        <el-radio-button label="resolved">已解决</el-radio-button>
      </el-radio-group>

      <div class="filter-right">
        <el-select v-model="filterLevel" placeholder="告警级别" clearable style="width: 120px">
          <el-option label="紧急" value="critical" />
          <el-option label="警告" value="warning" />
          <el-option label="提示" value="info" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px"
        />
      </div>
    </div>

    <!-- 告警表格 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 60px">
              <input type="checkbox" @change="toggleSelectAll" :checked="isAllSelected" />
            </th>
            <th style="width: 80px">级别</th>
            <th>告警内容</th>
            <th style="width: 150px">设备</th>
            <th style="width: 160px">时间</th>
            <th style="width: 100px">状态</th>
            <th style="width: 200px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="alert in paginatedAlerts" :key="alert.id">
            <td>
              <input type="checkbox" :checked="selectedAlerts.includes(alert)" @change="toggleSelect(alert)" />
            </td>
            <td>
              <div class="level-cell">
                <el-icon :size="20" :color="getLevelColor(alert.level)">
                  <WarningFilled v-if="alert.level === 'critical'" />
                  <Warning v-else-if="alert.level === 'warning'" />
                  <InfoFilled v-else />
                </el-icon>
              </div>
            </td>
            <td>
              <div class="alert-message">
                <div class="message-text">{{ alert.message }}</div>
                <div class="message-meta">
                  <span class="metric-tag" :class="alert.metric">{{ metricText(alert.metric) }}</span>
                  <span class="alert-type">{{ typeText(alert.alert_type) }}</span>
                </div>
              </div>
            </td>
            <td>{{ alert.device_name }}</td>
            <td>{{ formatTime(alert.created_at) }}</td>
            <td>
              <span class="status-badge" :class="alert.status">{{ statusText(alert.status) }}</span>
            </td>
            <td>
              <div class="actions">
                <el-button
                  v-if="alert.status === 'active'"
                  link
                  type="primary"
                  @click="acknowledgeAlert(alert)"
                >
                  确认
                </el-button>
                <el-button
                  v-if="alert.status !== 'resolved'"
                  link
                  type="success"
                  @click="resolveAlert(alert)"
                >
                  解决
                </el-button>
                <el-button link @click="viewDetail(alert)">详情</el-button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalCount"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
      />
    </div>

    <!-- 批量操作栏 -->
    <div v-if="selectedAlerts.length > 0" class="batch-actions">
      <span class="batch-text">已选择 {{ selectedAlerts.length }} 项</span>
      <el-button type="primary" size="small" @click="batchAcknowledge">
        批量确认
      </el-button>
      <el-button type="success" size="small" @click="batchResolve">
        批量解决
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const filterStatus = ref('')
const filterLevel = ref('')
const dateRange = ref(null)
const selectedAlerts = ref<any[]>([])

// 模拟告警数据
const alerts = ref([
  { id: 1, device_id: 1, device_name: '压缩机-A01', message: '温度过高 (85°C)', level: 'critical', metric: 'temperature', alert_type: 'threshold', status: 'active', created_at: new Date(Date.now() - 5 * 60000).toISOString() },
  { id: 2, device_id: 2, device_name: '泵机-B02', message: '振动异常 (6.5 mm/s)', level: 'warning', metric: 'vibration', alert_type: 'threshold', status: 'active', created_at: new Date(Date.now() - 15 * 60000).toISOString() },
  { id: 3, device_id: 3, device_name: '风机-C03', message: '电流波动超过阈值', level: 'warning', metric: 'current', alert_type: 'trend', status: 'acknowledged', created_at: new Date(Date.now() - 32 * 60000).toISOString() },
  { id: 4, device_id: 1, device_name: '压缩机-A01', message: '设备离线超过10分钟', level: 'critical', metric: 'system', alert_type: 'system', status: 'resolved', created_at: new Date(Date.now() - 60 * 60000).toISOString() },
  { id: 5, device_id: 4, device_name: '输送机-D04', message: '温度趋势上升', level: 'info', metric: 'temperature', alert_type: 'trend', status: 'active', created_at: new Date(Date.now() - 90 * 60000).toISOString() }
])

// 统计
const criticalCount = computed(() => alerts.value.filter(a => a.level === 'critical' && a.status === 'active').length)
const warningCount = computed(() => alerts.value.filter(a => a.level === 'warning' && a.status === 'active').length)
const infoCount = computed(() => alerts.value.filter(a => a.level === 'info' && a.status === 'active').length)
const totalCount = computed(() => filteredAlerts.value.length)

// 筛选
const filteredAlerts = computed(() => {
  let result = alerts.value
  if (filterStatus.value) {
    result = result.filter(a => a.status === filterStatus.value)
  }
  if (filterLevel.value) {
    result = result.filter(a => a.level === filterLevel.value)
  }
  return result
})

// 分页
const paginatedAlerts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAlerts.value.slice(start, end)
})

// 选择功能
const isAllSelected = computed(() => {
  return paginatedAlerts.value.length > 0 && paginatedAlerts.value.every(alert => selectedAlerts.value.includes(alert))
})

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedAlerts.value = []
  } else {
    selectedAlerts.value = [...paginatedAlerts.value]
  }
}

const toggleSelect = (alert: any) => {
  const index = selectedAlerts.value.indexOf(alert)
  if (index > -1) {
    selectedAlerts.value.splice(index, 1)
  } else {
    selectedAlerts.value.push(alert)
  }
}

// 辅助函数
const getLevelColor = (level: string) => {
  const colors: Record<string, string> = {
    critical: '#FF79C6',
    warning: '#FFB86C',
    info: '#3ECF8E'
  }
  return colors[level] || '#666'
}

const getMetricType = (metric: string) => {
  const types: Record<string, string> = {
    temperature: 'danger',
    vibration: 'warning',
    current: 'success',
    system: 'info'
  }
  return types[metric] || ''
}

const metricText = (metric: string) => {
  const texts: Record<string, string> = {
    temperature: '温度',
    vibration: '振动',
    current: '电流',
    system: '系统'
  }
  return texts[metric] || metric
}

const typeText = (type: string) => {
  const texts: Record<string, string> = {
    threshold: '阈值告警',
    trend: '趋势告警',
    prediction: '预测告警',
    system: '系统告警'
  }
  return texts[type] || type
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    active: 'danger',
    acknowledged: 'warning',
    resolved: 'success'
  }
  return types[status] || ''
}

const statusText = (status: string) => {
  const texts: Record<string, string> = {
    active: '未处理',
    acknowledged: '已确认',
    resolved: '已解决'
  }
  return texts[status] || status
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 操作
const refreshAlerts = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 500)
}

const acknowledgeAlert = (alert: any) => {
  alert.status = 'acknowledged'
}

const resolveAlert = (alert: any) => {
  alert.status = 'resolved'
}

const viewDetail = (alert: any) => {
  console.log('查看告警详情:', alert)
}

const handleSelectionChange = (selection: any[]) => {
  selectedAlerts.value = selection
}

const batchAcknowledge = () => {
  selectedAlerts.value.forEach((alert: any) => {
    alert.status = 'acknowledged'
  })
  selectedAlerts.value = []
}

const batchResolve = () => {
  selectedAlerts.value.forEach((alert: any) => {
    alert.status = 'resolved'
  })
  selectedAlerts.value = []
}

onMounted(() => {
})
</script>

<style scoped>
.alert-list {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.stat-item.critical {
  border-color: rgba(255, 121, 198, 0.3);
}

.stat-item.warning {
  border-color: rgba(255, 184, 108, 0.3);
}

.stat-item.info {
  border-color: rgba(62, 207, 142, 0.3);
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-item.critical .stat-value {
  color: #FF79C6;
}

.stat-item.warning .stat-value {
  color: #FFB86C;
}

.stat-item.info .stat-value {
  color: #3ECF8E;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-right {
  display: flex;
  gap: 12px;
}

.table-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.data-table th {
  background: rgba(255, 255, 255, 0.02);
  font-weight: 600;
  color: var(--text-secondary);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.metric-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
}

.metric-tag.temperature {
  background: rgba(255, 121, 198, 0.1);
  color: #FF79C6;
}

.metric-tag.vibration {
  background: rgba(189, 147, 249, 0.1);
  color: #BD93F9;
}

.metric-tag.current {
  background: rgba(62, 207, 142, 0.1);
  color: #3ECF8E;
}

.metric-tag.system {
  background: rgba(255, 184, 108, 0.1);
  color: #FFB86C;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
}

.status-badge.active {
  background: rgba(255, 121, 198, 0.1);
  color: #FF79C6;
}

.status-badge.acknowledged {
  background: rgba(255, 184, 108, 0.1);
  color: #FFB86C;
}

.status-badge.resolved {
  background: rgba(62, 207, 142, 0.1);
  color: #3ECF8E;
}

.actions {
  display: flex;
  gap: 8px;
}

/* 表格操作按钮 - 深色背景 */
.actions .el-button {
  background-color: #21262d !important;
  border-color: #30363d !important;
  color: #c9d1d9 !important;
  padding: 4px 12px !important;
  font-size: 13px !important;
}

.actions .el-button--primary {
  background-color: #238636 !important;
  border-color: #238636 !important;
  color: #ffffff !important;
}

.actions .el-button--success {
  background-color: #1f6feb !important;
  border-color: #1f6feb !important;
  color: #ffffff !important;
}

.actions .el-button:hover {
  background-color: #30363d !important;
  border-color: #8b949e !important;
  color: #ffffff !important;
}

.level-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.alert-message {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-text {
  font-size: 14px;
  color: var(--text-primary);
}

.message-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.alert-type {
  font-size: 12px;
  color: var(--text-muted);
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.batch-text {
  color: var(--text-secondary);
  font-size: 14px;
}

/* 超强力按钮覆盖 - 批量操作栏 */
.batch-actions .el-button,
.batch-actions .el-button.is-link,
.batch-actions button[class*="el-button"] {
  background-color: #21262d !important;
  border: 1px solid #30363d !important;
  color: #ffffff !important;
  padding: 8px 16px !important;
  font-size: 14px !important;
  border-radius: 6px !important;
}

.batch-actions .el-button--primary,
.batch-actions .el-button--primary.is-link {
  background-color: #238636 !important;
  border-color: #238636 !important;
  color: #ffffff !important;
}

.batch-actions .el-button--success,
.batch-actions .el-button--success.is-link {
  background-color: #1f6feb !important;
  border-color: #1f6feb !important;
  color: #ffffff !important;
}

/* 表格中的按钮 - 超强力覆盖 */
.actions .el-button,
.actions .el-button.is-link,
.actions button[class*="el-button"] {
  background-color: #21262d !important;
  border: 1px solid #30363d !important;
  color: #c9d1d9 !important;
  padding: 6px 12px !important;
  font-size: 13px !important;
  border-radius: 4px !important;
  margin: 0 4px !important;
}

.actions .el-button--primary {
  background-color: #238636 !important;
  border-color: #238636 !important;
  color: #ffffff !important;
}

.actions .el-button--success {
  background-color: #1f6feb !important;
  border-color: #1f6feb !important;
  color: #ffffff !important;
}

.actions .el-button:hover {
  background-color: #30363d !important;
  border-color: #8b949e !important;
  color: #ffffff !important;
}
</style>
