/**
 * 仪表板API服务 / Dashboard API Service
 *
 * 提供总览看板所需的数据接口
 * Provides data interfaces for dashboard overview
 */

import apiClient from './index'

// 统计概览接口
export interface DashboardStats {
  todayVehicles: number
  vehicleTrend: number
  equipmentHealthRate: number
  equipmentTrend: number
  pendingWorkOrders: number
  workOrderTrend: number
  cleanupEfficiency: number
  efficiencyTrend: number
}

// 实时状态接口
export interface RealtimeStatus {
  dispatch: string
  equipment: string
  workorders: number
  alerts: number
}

// 活动数据点
export interface ActivityPoint {
  time: string
  vehicles: number
  workorders: number
}

// 设备状态
export interface EquipmentStatusItem {
  name: string
  status: 'normal' | 'warning' | 'error'
  statusText: string
  load: number
}

// AI洞察
export interface AIInsight {
  id: number
  type: 'optimization' | 'warning' | 'info'
  typeText: string
  content: string
  confidence: number
}

// 最近活动
export interface RecentActivity {
  id: number
  type: 'dispatch' | 'alert' | 'workorder' | 'system'
  text: string
  time: string
}

/**
 * 获取设备统计概览
 */
export async function getEquipmentStats() {
  const response = await apiClient.get('/api/v1/equipment/stats/overview')
  return response.data.data
}

/**
 * 获取安全告警统计
 */
export async function getSafetyStats() {
  const response = await apiClient.get('/api/v1/safety/stats/overview')
  return response.data.data
}

/**
 * 获取工单统计
 */
export async function getWorkOrderStats() {
  const response = await apiClient.get('/api/v1/workflow/work-orders/stats/overview')
  return response.data.data
}

/**
 * 获取设备列表
 */
export async function getEquipmentList() {
  const response = await apiClient.get('/api/v1/equipment')
  return response.data.data
}

/**
 * 获取AI洞察
 */
export async function getAIInsights() {
  // 使用AI快速分析端点
  const response = await apiClient.post('/api/v1/ai/quick/analyze', {
    type: 'dashboard_insights'
  })
  return response.data.data
}

/**
 * 获取实时活动数据
 */
export async function getActivityData(): Promise<ActivityPoint[]> {
  // 获取传感器数据来生成活动趋势
  const response = await apiClient.get('/api/v1/sensor-data?limit=100')
  const sensorData = response.data.data?.items || []

  // 按小时聚合数据
  const hourlyData: Record<string, { vehicles: number; workorders: number }> = {}

  sensorData.forEach((item: any) => {
    const hour = new Date(item.timestamp).getHours()
    const timeKey = `${hour.toString().padStart(2, '0')}:00`

    if (!hourlyData[timeKey]) {
      hourlyData[timeKey] = { vehicles: 0, workorders: 0 }
    }

    if (item.device_type === 'gps_tracker') {
      hourlyData[timeKey].vehicles++
    } else {
      hourlyData[timeKey].workorders++
    }
  })

  // 转换为图表数据格式 (0-100的百分比)
  const maxVehicles = Math.max(...Object.values(hourlyData).map(d => d.vehicles), 1)
  const maxWorkorders = Math.max(...Object.values(hourlyData).map(d => d.workorders), 1)

  return Object.entries(hourlyData).map(([time, data]) => ({
    time,
    vehicles: Math.round((data.vehicles / maxVehicles) * 100),
    workorders: Math.round((data.workorders / maxWorkorders) * 100)
  })).slice(-6) // 最近6个时间点
}

/**
 * 获取完整仪表板数据
 */
export async function getDashboardData() {
  try {
    const [equipmentStats, safetyStats, workOrderStats, equipmentList] = await Promise.all([
      getEquipmentStats().catch(() => null),
      getSafetyStats().catch(() => null),
      getWorkOrderStats().catch(() => null),
      getEquipmentList().catch(() => null)
    ])

    return {
      equipmentStats,
      safetyStats,
      workOrderStats,
      equipmentList
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
    return null
  }
}
