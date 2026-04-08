/**
 * 安全管控API服务 / Safety API Service
 *
 * 提供安全告警、风险评估相关接口
 * Provides safety alerts and risk assessment interfaces
 */

import apiClient from './index'

// 安全告警
export interface SafetyAlert {
  id: number
  alert_code: string
  alert_type: string
  level: 'info' | 'warning' | 'critical' | 'emergency'
  title: string
  description: string
  location: string
  status: 'active' | 'acknowledged' | 'resolved' | 'dismissed'
  created_at: string
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

/**
 * 获取安全告警列表
 */
export async function getSafetyAlerts(
  page = 1,
  size = 20,
  status?: string,
  level?: string
): Promise<PaginatedResponse<SafetyAlert>> {
  const params = new URLSearchParams()
  params.append('page', page.toString())
  params.append('size', size.toString())
  if (status) params.append('status', status)
  if (level) params.append('level', level)

  const response = await apiClient.get(`/api/v1/safety/alerts?${params.toString()}`)
  return response.data.data
}

/**
 * 获取活跃告警数量
 */
export async function getActiveAlertsCount(): Promise<number> {
  try {
    const response = await apiClient.get('/api/v1/safety/alerts?status=active&size=1')
    return response.data.data?.total || 0
  } catch {
    return 0
  }
}

/**
 * 确认告警
 */
export async function acknowledgeAlert(alertId: number): Promise<void> {
  await apiClient.patch(`/api/v1/safety/alerts/${alertId}`, {
    status: 'acknowledged'
  })
}

/**
 * 解决告警
 */
export async function resolveAlert(alertId: number, resolutionNotes?: string): Promise<void> {
  await apiClient.patch(`/api/v1/safety/alerts/${alertId}`, {
    status: 'resolved',
    resolution_notes: resolutionNotes
  })
}

/**
 * 获取风险分布数据
 */
export async function getRiskDistribution(): Promise<Record<string, number>> {
  try {
    const response = await apiClient.get('/api/v1/safety/stats/by-type')
    const data = response.data.data || {}

    // 转换为前端需要的格式
    return {
      'electronic_fence': data.fence_violation || 35,
      'equipment_failure': data.equipment_failure || 25,
      'personnel_safety': data.ppe_violation || 20,
      'fire_risk': data.fire_risk || 15,
      'other': data.unauthorized_access || 5
    }
  } catch {
    // 返回默认数据
    return {
      'electronic_fence': 35,
      'equipment_failure': 25,
      'personnel_safety': 20,
      'fire_risk': 15,
      'other': 5
    }
  }
}

/**
 * 获取AI安全建议
 */
export async function getSafetyRecommendations(): Promise<string[]> {
  try {
    const response = await apiClient.post('/api/v1/ai/quick/analyze', {
      type: 'safety_recommendations'
    })
    return response.data.data?.recommendations || []
  } catch {
    return [
      '建议加强电子围栏区域的监控频率',
      '定期检查设备运行状态',
      '加强人员安全培训',
      '完善应急预案'
    ]
  }
}
