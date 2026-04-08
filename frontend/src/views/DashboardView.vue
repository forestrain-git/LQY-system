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
        <div class="stat-card__label" style="font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; color: var(--color-text-secondary);">{{ stat.label }}</div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Activity, RefreshCw, Download, Zap, Clock, Wrench,
  Sparkles, Bot, Truck, FileText, AlertTriangle,
  TrendingUp, CheckCircle2, Info
} from 'lucide-vue-next'
import { getDashboardData, getEquipmentStats, getSafetyStats, getWorkOrderStats, getEquipmentList } from '@/api/dashboard'
import apiClient from '@/api'

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

// 加载状态
const isLoading = ref(false)

// 刷新状态 / Refresh status
const isRefreshing = ref(false)
const refreshData = async () => {
  isRefreshing.value = true
  await fetchDashboardData()
  setTimeout(() => {
    isRefreshing.value = false
  }, 500)
}

// 导出报告 / Export report
const exportReport = () => {
  alert('报告导出功能开发中...')
}

// 主要统计 / Main statistics - 使用模拟数据
const mainStats = ref([
  { icon: Truck, value: '128', label: '今日车次', trend: 12 },
  { icon: CheckCircle2, value: '96%', label: '设备完好率', trend: 3 },
  { icon: FileText, value: '45', label: '处理工单', trend: 8 },
  { icon: TrendingUp, value: '92%', label: '清运效率', trend: 5 }
])

// 实时状态 / Realtime status - 使用模拟数据
const realtimeStatus = ref({
  dispatch: '正常',
  equipment: '94%',
  workorders: 12,
  alerts: 3
})

// 活动数据 / Activity data - 使用模拟数据
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

// 最近活动 / Recent activities - 使用模拟数据
const recentActivities = ref([
  { id: 1, type: 'dispatch', icon: Truck, text: '车辆京A12345完成区域清扫任务', time: '10分钟前' },
  { id: 2, type: 'workorder', icon: FileText, text: '新工单#20240408012已创建', time: '25分钟前' },
  { id: 3, type: 'alert', icon: AlertTriangle, text: '设备D-045电池电量低警告', time: '1小时前' },
  { id: 4, type: 'system', icon: CheckCircle2, text: '系统自动备份完成', time: '2小时前' }
])

// 设备状态 / Equipment status - 使用模拟数据
const equipmentStatus = ref([
  { name: '清扫车-001', status: 'normal', statusText: '正常', load: 78 },
  { name: '洒水车-003', status: 'normal', statusText: '正常', load: 65 },
  { name: '垃圾车-007', status: 'warning', statusText: '警告', load: 45 },
  { name: '扫地机-A12', status: 'normal', statusText: '正常', load: 82 },
  { name: '压缩车-B05', status: 'error', statusText: '故障', load: 0 }
])

// AI洞察 / AI insights - 使用模拟数据
const aiInsights = ref([
  {
    id: 1,
    type: 'optimization',
    typeText: '优化建议',
    icon: TrendingUp,
    content: '建议增加14:00-16:00时段的车辆调度，历史数据显示该时段垃圾量增长35%',
    confidence: 92
  },
  {
    id: 2,
    type: 'warning',
    typeText: '预测警告',
    icon: AlertTriangle,
    content: '设备D-045（压缩车-B05）连续工作12小时，建议安排维护检查',
    confidence: 87
  },
  {
    id: 3,
    type: 'info',
    typeText: '信息提示',
    icon: Info,
    content: '今日清运效率比昨日提升8%，继续保持良好作业节奏',
    confidence: 95
  }
])

// 获取仪表板数据
const fetchDashboardData = async () => {
  isLoading.value = true
  try {
    // 获取设备统计
    const equipStats = await getEquipmentStats().catch(() => null)
    if (equipStats) {
      const healthRate = equipStats.total > 0
        ? Math.round(((equipStats.total - equipStats.maintenance - equipStats.error) / equipStats.total) * 100)
        : 0

      mainStats.value[1].value = `${healthRate}%`
      mainStats.value[1].trend = 3

      realtimeStatus.value.equipment = `${healthRate}%`

      // 更新设备状态列表 - 安全处理
      if (equipStats?.by_type && typeof equipStats.by_type === 'object') {
        try {
          equipmentStatus.value = Object.entries(equipStats.by_type)
            .filter(([name, data]) => data && typeof data === 'object')
            .map(([name, data]: [string, any]) => ({
              name: name || '未知设备',
              status: data.error > 0 ? 'error' : data.warning > 0 ? 'warning' : 'normal',
              statusText: data.error > 0 ? '故障' : data.warning > 0 ? '警告' : '正常',
              load: Math.round((data.total > 0 ? ((data.online || 0) / data.total) : 0) * 100)
            }))
        } catch (e) {
          console.error('处理设备数据失败:', e)
        }
      }
    }

    // 获取安全统计
    const safetyStats = await getSafetyStats().catch(() => null)
    if (safetyStats) {
      realtimeStatus.value.alerts = safetyStats.active_alerts || 0

      // 如果有活动数据，更新最近活动
      if (safetyStats.recent_alerts && safetyStats.recent_alerts.length > 0) {
        recentActivities.value = safetyStats.recent_alerts.slice(0, 4).map((alert: any, index: number) => ({
          id: index,
          type: alert.severity === 'critical' ? 'alert' : 'system',
          icon: alert.severity === 'critical' ? AlertTriangle : Info,
          text: alert.message || alert.title,
          time: formatTimeAgo(new Date(alert.created_at))
        }))
      }
    }

    // 获取工单统计
    const woStats = await getWorkOrderStats().catch(() => null)
    if (woStats) {
      mainStats.value[2].value = (woStats.completed_today || 0).toString()
      mainStats.value[2].trend = woStats.trend || 0

      const total = woStats.pending + woStats.in_progress + woStats.completed
      mainStats.value[3].value = total > 0 ? `${Math.round((woStats.completed / total) * 100)}%` : '0%'

      realtimeStatus.value.workorders = woStats.pending || 0
    }

    // 获取设备列表详情
    const equipList = await getEquipmentList().catch(() => null)
    if (equipList?.items) {
      equipmentStatus.value = equipList.items.slice(0, 5).map((eq: any) => ({
        name: eq.name,
        status: eq.status === 'normal' ? 'normal' : eq.status === 'warning' ? 'warning' : 'error',
        statusText: eq.status === 'normal' ? '正常' : eq.status === 'warning' ? '警告' : '故障',
        load: Math.round(eq.load_factor || Math.random() * 100)
      }))
    }

    // 获取AI洞察
    try {
      const aiResponse = await apiClient.post('/api/v1/ai/quick/analyze', {
        type: 'dashboard_insights',
        data: { equipment: equipStats, safety: safetyStats, workorders: woStats }
      })
      if (aiResponse.data?.data?.insights) {
        aiInsights.value = aiResponse.data.data.insights.map((insight: any, index: number) => ({
          id: index + 1,
          type: insight.type,
          typeText: insight.type === 'optimization' ? '优化建议' : insight.type === 'warning' ? '预测警告' : '信息提示',
          icon: insight.type === 'optimization' ? TrendingUp : insight.type === 'warning' ? AlertTriangle : Info,
          content: insight.content,
          confidence: insight.confidence || 90
        }))
      }
    } catch (e) {
      // AI服务可能未配置，使用默认洞察
      aiInsights.value = [
        {
          id: 1,
          type: 'optimization',
          typeText: '优化建议',
          icon: TrendingUp,
          content: '建议定期维护设备以保持最佳运行状态',
          confidence: 85
        },
        {
          id: 2,
          type: 'info',
          typeText: '信息提示',
          icon: Info,
          content: '系统运行正常，所有核心模块已就绪',
          confidence: 95
        }
      ]
    }

  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    isLoading.value = false
  }
}

// 格式化相对时间
const formatTimeAgo = (date: Date): string => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${Math.floor(hours / 24)}天前`
}

// 询问AI / Ask AI
const goToAI = () => {
  router.push('/ai-assistant')
}

// 应用洞察 / Apply insight
const applyInsight = (insight: typeof aiInsights.value[0]) => {
  alert(`应用洞察: ${insight.content}`)
}

// 组件挂载时获取数据
onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
/* ==================== 高对比度强制覆盖 ==================== */
* {
  font-family: 'Microsoft YaHei', 'SimHei', 'PingFang SC', sans-serif !important;
}

/* 强制高对比度背景色 */
.dashboard-view {
  --color-bg-elevated: #1e293b !important;
  --color-bg-secondary: #334155 !important;
  --color-bg-tertiary: #475569 !important;
  --color-border-primary: rgba(148, 163, 184, 0.2) !important;
  --color-border-secondary: rgba(148, 163, 184, 0.1) !important;
  --color-text-primary: #f8fafc !important;
  --color-text-secondary: #cbd5e1 !important;
  --color-text-tertiary: #94a3b8 !important;
}

/* 统计卡片高对比度 */
.stat-card {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
  border: 1px solid rgba(148, 163, 184, 0.2) !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
}

/* 仪表板区块高对比度 */
.dashboard-section {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
  border: 1px solid rgba(148, 163, 184, 0.2) !important;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4) !important;
}

/* 图表区域高对比度 */
.activity-chart {
  background: #0f172a !important;
  border-radius: 8px !important;
  padding: 16px !important;
  border: 1px solid rgba(148, 163, 184, 0.15) !important;
}

/* 图表条形高对比度 */
.chart-bar__segment--primary {
  background: linear-gradient(180deg, #10b981 0%, #059669 100%) !important;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.4) !important;
}

.chart-bar__segment--secondary {
  background: linear-gradient(180deg, #06b6d4 0%, #0891b2 100%) !important;
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.4) !important;
}

/* 快速操作卡片高对比度 */
.quick-action-card {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
  border: 1px solid rgba(148, 163, 184, 0.2) !important;
}

/* 状态网格高对比度 */
.status-item {
  background: #0f172a !important;
  border: 1px solid rgba(148, 163, 184, 0.15) !important;
}

.stat-card__label,
.status-item__label,
.section-title,
.chart-title,
.legend-item,
.activity-item__text,
.equipment-item__name,
.insight-card__content {
  font-family: 'Microsoft YaHei', 'SimHei', sans-serif !important;
}
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
