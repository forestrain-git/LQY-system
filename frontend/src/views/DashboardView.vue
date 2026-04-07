<!--
  总览看板页面 / Dashboard Overview Page

  提供系统整体运行状况的可视化展示
  Provides visual overview of system operation status

  Author: AI Sprint
  Date: 2026-04-07
-->
<template>
  <div class="dashboard-view">
    <!-- 欢迎栏 / Welcome Bar -->
    <div class="welcome-bar">
      <div class="welcome-content">
        <h1 class="welcome-title">总览看板</h1>
        <p class="welcome-subtitle">{{ currentDate }} · 系统运行正常</p>
      </div>
      <div class="welcome-actions">
        <button class="action-btn" @click="refreshData">
          <RefreshCw :class="{ 'spinning': isRefreshing }" />
          刷新
        </button>
        <button class="action-btn action-btn--primary" @click="exportReport">
          <Download />
          导出报告
        </button>
      </div>
    </div>

    <!-- 统计网格 / Statistics Grid -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in mainStats" :key="stat.label">
        <div class="stat-card__header">
          <component :is="stat.icon" class="stat-card__icon" />
          <span
            class="stat-card__trend"
            :class="stat.trend > 0 ? 'trend-up' : 'trend-down'"
          >
            {{ stat.trend > 0 ? '+' : '' }}{{ stat.trend }}%
          </span>
        </div>
        <div class="stat-card__value">{{ stat.value }}</div>
        <div class="stat-card__label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- 主内容网格 / Main Content Grid -->
    <div class="dashboard-grid">
      <!-- 实时状态 / Real-time Status -->
      <div class="dashboard-section section-large">
        <div class="section-header">
          <h2 class="section-title">
            <Activity class="section-icon" />
            实时运行状态
          </h2>
          <span class="live-indicator">
            <span class="live-dot"></span>
            实时监控
          </span>
        </div>
        <div class="section-body">
          <div class="status-grid">
            <div class="status-item">
              <div class="status-item__label">车辆调度</div>
              <div class="status-item__value status-item__value--success">
                {{ realtimeStatus.dispatch }}
              </div>
            </div>
            <div class="status-item">
              <div class="status-item__label">设备在线</div>
              <div class="status-item__value status-item__value--success">
                {{ realtimeStatus.equipment }}
              </div>
            </div>
            <div class="status-item">
              <div class="status-item__label">待处理工单</div>
              <div class="status-item__value" :class="realtimeStatus.workorders > 10 ? 'status-item__value--warning' : 'status-item__value--success'">
                {{ realtimeStatus.workorders }}
              </div>
            </div>
            <div class="status-item">
              <div class="status-item__label">活跃告警</div>
              <div class="status-item__value" :class="realtimeStatus.alerts > 0 ? 'status-item__value--danger' : 'status-item__value--success'">
                {{ realtimeStatus.alerts }}
              </div>
            </div>
          </div>

          <!-- 活动图表 / Activity Chart -->
          <div class="activity-chart">
            <div class="chart-header">
              <span class="chart-title">今日活动趋势</span>
              <div class="chart-legend">
                <span class="legend-item">
                  <span class="legend-dot legend-dot--primary"></span>
                  车辆
                </span>
                <span class="legend-item">
                  <span class="legend-dot legend-dot--secondary"></span>
                  工单
                </span>
              </div>
            </div>
            <div class="chart-body">
              <div
                v-for="(point, index) in activityData"
                :key="index"
                class="chart-bar"
              >
                <div class="chart-bar__stack">
                  <div
                    class="chart-bar__segment chart-bar__segment--primary"
                    :style="{ height: `${point.vehicles}%` }"
                  ></div>
                  <div
                    class="chart-bar__segment chart-bar__segment--secondary"
                    :style="{ height: `${point.workorders}%` }"
                  ></div>
                </div>
                <span class="chart-bar__label">{{ point.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速操作 / Quick Actions -->
      <div class="dashboard-section">
        <div class="section-header">
          <h2 class="section-title">
            <Zap class="section-icon" />
            快速操作
          </h2>
        </div>
        <div class="section-body">
          <div class="quick-actions">
            <button
              v-for="action in quickActions"
              :key="action.label"
              class="quick-action-card"
              @click="handleQuickAction(action)"
            >
              <component :is="action.icon" class="quick-action-card__icon" />
              <span class="quick-action-card__label">{{ action.label }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 最近活动 / Recent Activity -->
      <div class="dashboard-section">
        <div class="section-header">
          <h2 class="section-title">
            <Clock class="section-icon" />
            最近活动
          </h2>
        </div>
        <div class="section-body">
          <div class="activity-list">
            <div
              v-for="activity in recentActivities"
              :key="activity.id"
              class="activity-item"
            >
              <div class="activity-item__icon" :class="`activity-item__icon--${activity.type}`">
                <component :is="activity.icon" />
              </div>
              <div class="activity-item__content">
                <div class="activity-item__text">{{ activity.text }}</div>
                <div class="activity-item__time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 设备状态 / Equipment Status -->
      <div class="dashboard-section">
        <div class="section-header">
          <h2 class="section-title">
            <Wrench class="section-icon" />
            设备状态
          </h2>
        </div>
        <div class="section-body">
          <div class="equipment-status">
            <div
              v-for="equip in equipmentStatus"
              :key="equip.name"
              class="equipment-item"
            >
              <div class="equipment-item__info">
                <span class="equipment-item__name">{{ equip.name }}</span>
                <span
                  class="equipment-item__status"
                  :class="`equipment-item__status--${equip.status}`"
                >
                  {{ equip.statusText }}
                </span>
              </div>
              <div class="equipment-item__bar">
                <div
                  class="equipment-item__fill"
                  :class="`equipment-item__fill--${equip.status}`"
                  :style="{ width: `${equip.load}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI 洞察 / AI Insights -->
      <div class="dashboard-section section-wide">
        <div class="section-header">
          <h2 class="section-title">
            <Sparkles class="section-icon" />
            AI 智能洞察
          </h2>
          <button class="ask-ai-btn" @click="goToAI">
            <Bot />
            询问AI
          </button>
        </div>
        <div class="section-body">
          <div class="insights-grid">
            <div
              v-for="insight in aiInsights"
              :key="insight.id"
              class="insight-card"
              :class="`insight-card--${insight.type}`"
            >
              <div class="insight-card__header">
                <component :is="insight.icon" class="insight-card__icon" />
                <span class="insight-card__type">{{ insight.typeText }}</span>
              </div>
              <p class="insight-card__content">{{ insight.content }}</p>
              <div class="insight-card__footer">
                <span class="insight-card__confidence">
                  置信度 {{ insight.confidence }}%
                </span>
                <button class="insight-card__action" @click="applyInsight(insight)">
                  查看详情
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Activity, RefreshCw, Download, Zap, Clock, Wrench,
  Sparkles, Bot, Truck, FileText, AlertTriangle,
  TrendingUp, CheckCircle2, Info
} from 'lucide-vue-next'

const router = useRouter()

// 当前日期 / Current date
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 刷新状态 / Refresh status
const isRefreshing = ref(false)
const refreshData = () => {
  isRefreshing.value = true
  setTimeout(() => {
    isRefreshing.value = false
  }, 1000)
}

// 导出报告 / Export report
const exportReport = () => {
  alert('报告导出功能开发中...')
}

// 主要统计 / Main statistics
const mainStats = ref([
  { icon: Truck, value: '156', label: '今日车次', trend: 12 },
  { icon: CheckCircle2, value: '89%', label: '设备完好率', trend: 3 },
  { icon: FileText, value: '42', label: '处理工单', trend: -5 },
  { icon: TrendingUp, value: '98.5%', label: '清运效率', trend: 2 }
])

// 实时状态 / Realtime status
const realtimeStatus = ref({
  dispatch: '正常',
  equipment: '98%',
  workorders: 8,
  alerts: 2
})

// 活动数据 / Activity data
const activityData = ref([
  { time: '08:00', vehicles: 30, workorders: 20 },
  { time: '10:00', vehicles: 50, workorders: 35 },
  { time: '12:00', vehicles: 70, workorders: 45 },
  { time: '14:00', vehicles: 85, workorders: 60 },
  { time: '16:00', vehicles: 60, workorders: 40 },
  { time: '18:00', vehicles: 40, workorders: 25 }
])

// 快速操作 / Quick actions
const quickActions = [
  { icon: Truck, label: '调度车辆', route: '/dispatch' },
  { icon: FileText, label: '新建工单', route: '/workorders' },
  { icon: AlertTriangle, label: '处理告警', route: '/safety' },
  { icon: Bot, label: 'AI助手', route: '/ai-assistant' }
]

const handleQuickAction = (action: typeof quickActions[0]) => {
  router.push(action.route)
}

// 最近活动 / Recent activities
const recentActivities = ref([
  { id: 1, type: 'dispatch', icon: Truck, text: '车辆川A12345完成卸料', time: '5分钟前' },
  { id: 2, type: 'alert', icon: AlertTriangle, text: '1号压缩机温度异常警告', time: '15分钟前' },
  { id: 3, type: 'workorder', icon: FileText, text: '工单WO20260408001已完成', time: '30分钟前' },
  { id: 4, type: 'system', icon: CheckCircle2, text: '系统备份完成', time: '1小时前' }
])

// 设备状态 / Equipment status
const equipmentStatus = ref([
  { name: '1号压缩机', status: 'normal', statusText: '正常', load: 75 },
  { name: '2号压缩机', status: 'normal', statusText: '正常', load: 60 },
  { name: '输送带A', status: 'warning', statusText: '警告', load: 85 },
  { name: '地磅系统', status: 'normal', statusText: '正常', load: 45 }
])

// AI洞察 / AI insights
const aiInsights = ref([
  {
    id: 1,
    type: 'optimization',
    typeText: '优化建议',
    icon: TrendingUp,
    content: '下午2-4点车辆集中到达，建议增加B区泊位开放数量',
    confidence: 92
  },
  {
    id: 2,
    type: 'warning',
    typeText: '预测警告',
    icon: AlertTriangle,
    content: '1号压缩机运行时长接近维护周期，建议3天内安排保养',
    confidence: 88
  },
  {
    id: 3,
    type: 'info',
    typeText: '信息提示',
    icon: Info,
    content: '本周清运效率较上周提升12%，主要得益于路线优化',
    confidence: 95
  }
])

// 询问AI / Ask AI
const goToAI = () => {
  router.push('/ai-assistant')
}

// 应用洞察 / Apply insight
const applyInsight = (insight: typeof aiInsights.value[0]) => {
  alert(`应用洞察: ${insight.content}`)
}
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

/* 欢迎栏 / Welcome Bar */
.welcome-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
}

.welcome-title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-text-primary);
}

.welcome-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

.welcome-actions {
  display: flex;
  gap: var(--space-3);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background-color: var(--color-bg-tertiary);
}

.action-btn--primary {
  color: white;
  background-color: var(--color-primary-600);
  border-color: var(--color-primary-600);
}

.action-btn--primary:hover {
  background-color: var(--color-primary-700);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 统计网格 / Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.stat-card {
  padding: var(--space-5);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
}

.stat-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.stat-card__icon {
  width: 24px;
  height: 24px;
  color: var(--color-text-secondary);
}

.stat-card__trend {
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.trend-up {
  color: var(--color-accent-success);
  background-color: rgba(34, 197, 94, 0.1);
}

.trend-down {
  color: var(--color-accent-danger);
  background-color: rgba(239, 68, 68, 0.1);
}

.stat-card__value {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-card__label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

/* 仪表板网格 / Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-auto-rows: minmax(200px, auto);
  gap: var(--space-6);
}

.dashboard-section {
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.section-large {
  grid-column: span 2;
  grid-row: span 2;
}

.section-wide {
  grid-column: span 3;
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

.section-body {
  padding: var(--space-5);
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-accent-success);
}

.live-dot {
  width: 8px;
  height: 8px;
  background-color: var(--color-accent-success);
  border-radius: var(--radius-full);
  animation: pulse 2s infinite;
}

/* 状态网格 / Status Grid */
.status-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.status-item {
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.status-item__label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
}

.status-item__value {
  font-size: var(--text-xl);
  font-weight: 600;
}

.status-item__value--success {
  color: var(--color-accent-success);
}

.status-item__value--warning {
  color: var(--color-accent-warning);
}

.status-item__value--danger {
  color: var(--color-accent-danger);
}

/* 活动图表 / Activity Chart */
.activity-chart {
  margin-top: var(--space-6);
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}

.chart-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.chart-legend {
  display: flex;
  gap: var(--space-4);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.legend-dot--primary {
  background-color: var(--color-primary-500);
}

.legend-dot--secondary {
  background-color: var(--color-accent-info);
}

.chart-body {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 150px;
  gap: var(--space-2);
}

.chart-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.chart-bar__stack {
  width: 100%;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 2px;
}

.chart-bar__segment {
  width: 100%;
  border-radius: var(--radius-sm);
  transition: height var(--transition-base);
}

.chart-bar__segment--primary {
  background-color: var(--color-primary-500);
}

.chart-bar__segment--secondary {
  background-color: var(--color-accent-info);
}

.chart-bar__label {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

/* 快速操作 / Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.quick-action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-action-card:hover {
  background-color: var(--color-bg-tertiary);
  border-color: var(--color-primary-500);
}

.quick-action-card__icon {
  width: 24px;
  height: 24px;
  color: var(--color-primary-500);
}

.quick-action-card__label {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

/* 活动列表 / Activity List */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
}

.activity-item__icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.activity-item__icon--dispatch {
  background-color: var(--color-primary-50);
  color: var(--color-primary-600);
}

.activity-item__icon--alert {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-accent-danger);
}

.activity-item__icon--workorder {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-accent-info);
}

.activity-item__icon--system {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}

.activity-item__content {
  flex: 1;
}

.activity-item__text {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

.activity-item__time {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: 2px;
}

/* 设备状态 / Equipment Status */
.equipment-status {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.equipment-item__info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}

.equipment-item__name {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

.equipment-item__status {
  font-size: var(--text-xs);
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.equipment-item__status--normal {
  color: var(--color-accent-success);
  background-color: rgba(34, 197, 94, 0.1);
}

.equipment-item__status--warning {
  color: var(--color-accent-warning);
  background-color: rgba(217, 119, 6, 0.1);
}

.equipment-item__bar {
  height: 6px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.equipment-item__fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-base);
}

.equipment-item__fill--normal {
  background-color: var(--color-accent-success);
}

.equipment-item__fill--warning {
  background-color: var(--color-accent-warning);
}

/* AI 洞察 / AI Insights */
.ask-ai-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-primary-600);
  background-color: var(--color-primary-50);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.ask-ai-btn:hover {
  background-color: var(--color-primary-100);
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.insight-card {
  padding: var(--space-4);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  border-left: 4px solid;
}

.insight-card--optimization {
  border-left-color: var(--color-accent-success);
}

.insight-card--warning {
  border-left-color: var(--color-accent-warning);
}

.insight-card--info {
  border-left-color: var(--color-accent-info);
}

.insight-card__header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.insight-card__icon {
  width: 16px;
  height: 16px;
  color: var(--color-text-secondary);
}

.insight-card__type {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-secondary);
  text-transform: uppercase;
}

.insight-card__content {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  line-height: 1.6;
  margin-bottom: var(--space-3);
}

.insight-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.insight-card__confidence {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.insight-card__action {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-primary-600);
  background: none;
  border: none;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.insight-card__action:hover {
  color: var(--color-primary-700);
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .section-large,
  .section-wide {
    grid-column: span 2;
  }

  .insights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid,
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .section-large,
  .section-wide {
    grid-column: span 1;
  }

  .welcome-bar {
    flex-direction: column;
    gap: var(--space-4);
  }
}
</style>
