<!--
  安全管控页面 / Safety Control Page

  提供安全告警监控、风险分析、实时态势感知
  Provides safety alert monitoring, risk analysis, situational awareness

  Author: AI Sprint
  Date: 2026-04-07
-->
<template>
  <div class="safety-view">
    <!-- 统计卡片 / Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card stat-card--danger">
        <div class="stat-card__icon">
          <AlertTriangle />
        </div>
        <div class="stat-card__content">
          <div class="stat-card__value">{{ stats.activeAlerts }}</div>
          <div class="stat-card__label">活跃告警</div>
        </div>
      </div>

      <div class="stat-card stat-card--warning">
        <div class="stat-card__icon">
          <ShieldAlert />
        </div>
        <div class="stat-card__content">
          <div class="stat-card__value">{{ stats.todayAlerts }}</div>
          <div class="stat-card__label">今日告警</div>
        </div>
      </div>

      <div class="stat-card stat-card--info">
        <div class="stat-card__icon">
          <Activity />
        </div>
        <div class="stat-card__content">
          <div class="stat-card__value">{{ stats.riskLevel }}</div>
          <div class="stat-card__label">风险等级</div>
        </div>
      </div>

      <div class="stat-card stat-card--success">
        <div class="stat-card__icon">
          <CheckCircle2 />
        </div>
        <div class="stat-card__content">
          <div class="stat-card__value">{{ stats.resolvedThisWeek }}</div>
          <div class="stat-card__label">本周解决</div>
        </div>
      </div>
    </div>

    <!-- 主要内容区 / Main Content -->
    <div class="safety-grid">
      <!-- 告警列表 / Alert List -->
      <div class="safety-section">
        <div class="section-header">
          <h2 class="section-title">
            <Bell class="section-icon" />
            安全告警
          </h2>
          <div class="section-filters">
            <select v-model="filterStatus" class="filter-select">
              <option value="">全部状态</option>
              <option value="active">活跃</option>
              <option value="acknowledged">已确认</option>
              <option value="resolved">已解决</option>
            </select>
            <select v-model="filterLevel" class="filter-select">
              <option value="">全部级别</option>
              <option value="emergency">紧急</option>
              <option value="critical">严重</option>
              <option value="warning">警告</option>
              <option value="info">提示</option>
            </select>
          </div>
        </div>

        <div class="section-body">
          <div v-if="loading" class="loading-state">
            <RefreshCw class="spinning" />
            <p>加载中...</p>
          </div>

          <div v-else-if="filteredAlerts.length === 0" class="empty-state">
            <ShieldCheck class="empty-state__icon" />
            <p>暂无安全告警</p>
          </div>

          <div v-else class="alert-list">
            <div
              v-for="alert in filteredAlerts"
              :key="alert.id"
              class="alert-item"
              :class="`alert-item--${alert.level}`"
            >
              <div class="alert-item__indicator"></div>
              <div class="alert-item__content">
                <div class="alert-item__header">
                  <span class="alert-item__type">{{ getAlertTypeText(alert.alert_type) }}</span>
                  <span class="alert-item__time">{{ formatTime(alert.created_at) }}</span>
                </div>
                <div class="alert-item__title">{{ alert.title }}</div>
                <div class="alert-item__location">
                  <MapPin class="alert-item__location-icon" />
                  {{ alert.location }}
                </div>
              </div>
              <div class="alert-item__actions">
                <button
                  v-if="alert.status === 'active'"
                  class="alert-btn alert-btn--primary"
                  @click="acknowledgeAlert(alert.id)"
                  :disabled="processing[alert.id]"
                >
                  <RefreshCw v-if="processing[alert.id]" class="spinning" />
                  <span v-else>确认</span>
                </button>
                <button
                  v-if="alert.status !== 'resolved'"
                  class="alert-btn"
                  @click="resolveAlert(alert.id)"
                  :disabled="processing[alert.id]"
                >
                  <CheckCircle2 v-if="processing[alert.id]" class="spinning" />
                  <span v-else>解决</span>
                </button>
                <span v-else class="alert-item__resolved">
                  <CheckCircle2 class="alert-item__resolved-icon" />
                  已解决
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 风险分析 / Risk Analysis -->
      <div class="safety-section">
        <div class="section-header">
          <h2 class="section-title">
            <PieChart class="section-icon" />
            风险分布
          </h2>
        </div>

        <div class="section-body">
          <div v-if="loading" class="loading-state">
            <RefreshCw class="spinning" />
            <p>加载中...</p>
          </div>

          <div v-else class="risk-chart">
            <div
              v-for="(value, key) in riskDistribution"
              :key="key"
              class="risk-bar"
            >
              <div class="risk-bar__label">{{ getRiskLabel(key) }}</div>
              <div class="risk-bar__track">
                <div
                  class="risk-bar__fill"
                  :class="`risk-bar__fill--${key}`"
                  :style="{ width: `${value}%` }"
                ></div>
              </div>
              <div class="risk-bar__value">{{ value }}%</div>
            </div>
          </div>

          <div class="ai-recommendations">
            <h3 class="ai-recommendations__title">
              <Bot class="ai-recommendations__icon" />
              AI建议
            </h3>
            <ul v-if="recommendations && recommendations.length > 0" class="ai-recommendations__list">
              <li v-for="(rec, index) in recommendations" :key="index">
                {{ rec }}
              </li>
            </ul>
            <p v-else class="ai-recommendations__empty">暂无建议</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  AlertTriangle, ShieldAlert, Activity, CheckCircle2,
  Bell, ShieldCheck, MapPin, PieChart, Bot, RefreshCw
} from 'lucide-vue-next'
import {
  getSafetyAlerts,
  getActiveAlertsCount,
  getRiskDistribution,
  getSafetyRecommendations,
  acknowledgeAlert as apiAcknowledgeAlert,
  resolveAlert as apiResolveAlert,
  type SafetyAlert
} from '@/api/safety'
import { getSafetyStats } from '@/api/dashboard'

// 加载状态
const loading = ref(false)
const processing = ref<Record<number, boolean>>({})

// 统计数据
const stats = ref({
  activeAlerts: 0,
  todayAlerts: 0,
  riskLevel: '低',
  resolvedThisWeek: 24
})

// 过滤器
const filterStatus = ref('')
const filterLevel = ref('')

// 告警数据
const alerts = ref<SafetyAlert[]>([])
const riskDistribution = ref<Record<string, number>>({
  'electronic_fence': 35,
  'equipment_failure': 25,
  'personnel_safety': 20,
  'fire_risk': 15,
  'other': 5
})
const recommendations = ref<string[]>([])

// 过滤后的告警
const filteredAlerts = computed(() => {
  return alerts.value.filter(alert => {
    if (filterStatus.value && alert.status !== filterStatus.value) return false
    if (filterLevel.value && alert.level !== filterLevel.value) return false
    return true
  })
})

// 获取告警类型文本
const getAlertTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    'fence_violation': '电子围栏',
    'unauthorized_access': '未授权进入',
    'equipment_failure': '设备故障',
    'hazardous_material': '危险品泄漏',
    'fire_risk': '火灾风险',
    'ppe_violation': '安全装备',
    'vehicle_incident': '车辆事故',
    'emergency': '紧急情况'
  }
  return typeMap[type] || type
}

// 获取风险标签
const getRiskLabel = (key: string): string => {
  const labelMap: Record<string, string> = {
    'electronic_fence': '电子围栏',
    'equipment_failure': '设备故障',
    'personnel_safety': '人员安全',
    'fire_risk': '火灾风险',
    'other': '其他'
  }
  return labelMap[key] || key
}

// 格式化时间
const formatTime = (time: string): string => {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return date.toLocaleDateString('zh-CN')
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const activeCount = await getActiveAlertsCount()
    stats.value.activeAlerts = activeCount

    const safetyStats = await getSafetyStats()
    if (safetyStats) {
      stats.value.todayAlerts = safetyStats.today_alerts || 0
      stats.value.riskLevel = safetyStats.risk_level || '低'
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

// 获取告警列表
const fetchAlerts = async () => {
  loading.value = true
  try {
    const response = await getSafetyAlerts(1, 50)
    alerts.value = response.items || []
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
    ElMessage.error('获取告警列表失败')
  } finally {
    loading.value = false
  }
}

// 获取风险分布
const fetchRiskDistribution = async () => {
  try {
    const distribution = await getRiskDistribution()
    riskDistribution.value = distribution
  } catch (error) {
    console.error('Failed to fetch risk distribution:', error)
  }
}

// 获取AI建议
const fetchRecommendations = async () => {
  try {
    const recs = await getSafetyRecommendations()
    recommendations.value = recs
  } catch (error) {
    console.error('Failed to fetch recommendations:', error)
  }
}

// 确认告警
const acknowledgeAlert = async (id: number) => {
  processing.value[id] = true
  try {
    await apiAcknowledgeAlert(id)
    ElMessage.success('告警已确认')
    // 更新本地状态
    const alert = alerts.value.find(a => a.id === id)
    if (alert) {
      alert.status = 'acknowledged'
    }
    // 刷新统计
    await fetchStats()
  } catch (error) {
    console.error('Failed to acknowledge alert:', error)
    ElMessage.error('确认失败')
  } finally {
    processing.value[id] = false
  }
}

// 解决告警
const resolveAlert = async (id: number) => {
  processing.value[id] = true
  try {
    await apiResolveAlert(id)
    ElMessage.success('告警已解决')
    // 更新本地状态
    const alert = alerts.value.find(a => a.id === id)
    if (alert) {
      alert.status = 'resolved'
    }
    // 刷新统计
    await fetchStats()
  } catch (error) {
    console.error('Failed to resolve alert:', error)
    ElMessage.error('解决失败')
  } finally {
    processing.value[id] = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchStats()
  fetchAlerts()
  fetchRiskDistribution()
  fetchRecommendations()
})
</script>

<style scoped>
.safety-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

/* 统计卡片 / Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  border-left: 4px solid;
}

.stat-card--danger {
  border-left-color: var(--color-accent-danger);
}

.stat-card--warning {
  border-left-color: var(--color-accent-warning);
}

.stat-card--info {
  border-left-color: var(--color-accent-info);
}

.stat-card--success {
  border-left-color: var(--color-accent-success);
}

.stat-card__icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  color: white;
}

.stat-card--danger .stat-card__icon {
  background-color: var(--color-accent-danger);
}

.stat-card--warning .stat-card__icon {
  background-color: var(--color-accent-warning);
}

.stat-card--info .stat-card__icon {
  background-color: var(--color-accent-info);
}

.stat-card--success .stat-card__icon {
  background-color: var(--color-accent-success);
}

.stat-card__value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-card__label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-top: 2px;
}

/* 安全网格 / Safety Grid */
.safety-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-6);
}

.safety-section {
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border-secondary);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.section-icon {
  width: 18px;
  height: 18px;
  color: var(--color-text-secondary);
}

.section-filters {
  display: flex;
  gap: var(--space-2);
}

.filter-select {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
}

.section-body {
  padding: var(--space-4);
}

/* 加载状态 / Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  color: var(--color-text-tertiary);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 空状态 / Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  color: var(--color-text-tertiary);
}

.empty-state__icon {
  width: 48px;
  height: 48px;
  margin-bottom: var(--space-3);
  opacity: 0.5;
}

/* 告警列表 / Alert List */
.alert-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  border-left: 4px solid transparent;
}

.alert-item--emergency {
  border-left-color: #dc2626;
  background-color: rgba(220, 38, 38, 0.05);
}

.alert-item--critical {
  border-left-color: #ea580c;
  background-color: rgba(234, 88, 12, 0.05);
}

.alert-item--warning {
  border-left-color: #d97706;
  background-color: rgba(217, 119, 6, 0.05);
}

.alert-item--info {
  border-left-color: #2563eb;
}

.alert-item__indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  margin-top: var(--space-1);
}

.alert-item--emergency .alert-item__indicator {
  background-color: #dc2626;
  animation: pulse 2s infinite;
}

.alert-item--critical .alert-item__indicator {
  background-color: #ea580c;
}

.alert-item--warning .alert-item__indicator {
  background-color: #d97706;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.alert-item__content {
  flex: 1;
}

.alert-item__header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}

.alert-item__type {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-secondary);
  padding: 2px 8px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
}

.alert-item__time {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.alert-item__title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.alert-item__location {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.alert-item__location-icon {
  width: 12px;
  height: 12px;
}

.alert-item__actions {
  display: flex;
  gap: var(--space-2);
}

.alert-btn {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-secondary);
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.alert-btn:hover:not(:disabled) {
  background-color: var(--color-bg-secondary);
}

.alert-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.alert-btn--primary {
  color: white;
  background-color: var(--color-primary-600);
  border-color: var(--color-primary-600);
}

.alert-btn--primary:hover:not(:disabled) {
  background-color: var(--color-primary-700);
}

.alert-item__resolved {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--color-accent-success);
}

.alert-item__resolved-icon {
  width: 14px;
  height: 14px;
}

/* 风险图表 / Risk Chart */
.risk-chart {
  margin-bottom: var(--space-6);
}

.risk-bar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.risk-bar__label {
  width: 80px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  text-align: right;
}

.risk-bar__track {
  flex: 1;
  height: 8px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.risk-bar__fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-base);
}

.risk-bar__fill--electronic_fence {
  background-color: var(--color-accent-danger);
}

.risk-bar__fill--equipment_failure {
  background-color: var(--color-accent-warning);
}

.risk-bar__fill--personnel_safety {
  background-color: var(--color-accent-info);
}

.risk-bar__fill--fire_risk {
  background-color: #f59e0b;
}

.risk-bar__fill--other {
  background-color: var(--color-text-tertiary);
}

.risk-bar__value {
  width: 40px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

/* AI建议 / AI Recommendations */
.ai-recommendations {
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}

.ai-recommendations__title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-3);
}

.ai-recommendations__icon {
  width: 16px;
  height: 16px;
  color: var(--color-primary-500);
}

.ai-recommendations__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.ai-recommendations__list li {
  position: relative;
  padding-left: var(--space-4);
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.ai-recommendations__list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 6px;
  height: 6px;
  background-color: var(--color-primary-500);
  border-radius: var(--radius-full);
}

.ai-recommendations__empty {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  text-align: center;
  padding: var(--space-4);
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .safety-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>