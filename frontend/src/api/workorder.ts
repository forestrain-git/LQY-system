/**
 * 工单管理API服务 / WorkOrder API Service
 *
 * 提供工单创建、查询、更新相关接口
 * Provides work order CRUD interfaces
 */

import apiClient from './index'

// 工单
export interface WorkOrder {
  id: number
  order_no: string
  title: string
  description?: string
  type: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: 'pending' | 'processing' | 'completed' | 'cancelled'
  creator_id: number
  assignee_id?: number
  equipment_id?: number
  due_date?: string
  completed_at?: string
  created_at: string
  updated_at: string
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
 * 获取工单列表
 */
export async function getWorkOrders(
  page = 1,
  size = 20,
  status?: string,
  priority?: string
): Promise<PaginatedResponse<WorkOrder>> {
  const params = new URLSearchParams()
  params.append('page', page.toString())
  params.append('size', size.toString())
  if (status) params.append('status', status)
  if (priority) params.append('priority', priority)

  const response = await apiClient.get(`/api/v1/workflow/work-orders?${params.toString()}`)
  return response.data.data
}

/**
 * 获取待处理工单数量
 */
export async function getPendingWorkOrdersCount(): Promise<number> {
  try {
    const response = await apiClient.get('/api/v1/workflow/work-orders?status=pending&size=1')
    return response.data.data?.total || 0
  } catch {
    return 0
  }
}

/**
 * 获取工单详情
 */
export async function getWorkOrder(orderId: number): Promise<WorkOrder> {
  const response = await apiClient.get(`/api/v1/workflow/work-orders/${orderId}`)
  return response.data.data
}

/**
 * 创建工单
 */
export async function createWorkOrder(data: {
  title: string
  description?: string
  type: string
  priority: string
  equipment_id?: number
  due_date?: string
}): Promise<WorkOrder> {
  const response = await apiClient.post('/api/v1/workflow/work-orders', data)
  return response.data.data
}

/**
 * 更新工单状态
 */
export async function updateWorkOrderStatus(
  orderId: number,
  status: string
): Promise<void> {
  await apiClient.patch(`/api/v1/workflow/work-orders/${orderId}`, { status })
}

/**
 * 分配工单
 */
export async function assignWorkOrder(
  orderId: number,
  assigneeId: number
): Promise<void> {
  await apiClient.patch(`/api/v1/workflow/work-orders/${orderId}`, {
    assignee_id: assigneeId
  })
}
