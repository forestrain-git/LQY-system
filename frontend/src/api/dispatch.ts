/**
 * 智慧调度API服务 / Dispatch API Service
 *
 * 提供车辆调度、泊位管理相关接口
 * Provides vehicle dispatch and berth management interfaces
 */

import apiClient from './index'

// 车辆
export interface Vehicle {
  id: number
  plate_number: string
  vehicle_type: string
  status: string
  driver_name: string
  driver_phone: string
  gps_device_id: string
  current_location?: string
}

// 泊位
export interface Berth {
  id: number
  berth_code: string
  berth_type: string
  status: string
  capacity: number
}

// 调度任务
export interface Schedule {
  id: number
  schedule_no: string
  vehicle_id: number
  vehicle?: Vehicle
  berth_id: number
  berth?: Berth
  status: string
  estimated_arrival: string
  unloading_started_at?: string
  unloading_completed_at?: string
}

/**
 * 获取车辆列表
 */
export async function getVehicles(status?: string): Promise<Vehicle[]> {
  const params = new URLSearchParams()
  if (status) params.append('status', status)

  const response = await apiClient.get(`/api/v1/dispatch/vehicles?${params.toString()}`)
  return response.data.data?.items || []
}

/**
 * 获取可用泊位列表
 */
export async function getAvailableBerths(): Promise<Berth[]> {
  const response = await apiClient.get('/api/v1/dispatch/berths?status=available')
  return response.data.data?.items || []
}

/**
 * 获取当前调度队列
 */
export async function getDispatchQueue(): Promise<Schedule[]> {
  const response = await apiClient.get('/api/v1/dispatch/schedules?status=pending')
  return response.data.data?.items || []
}

/**
 * 创建调度任务
 */
export async function createSchedule(data: {
  vehicle_id: number
  berth_id: number
  estimated_arrival?: string
}): Promise<Schedule> {
  const response = await apiClient.post('/api/v1/dispatch/schedules', data)
  return response.data.data
}

/**
 * 更新调度状态
 */
export async function updateScheduleStatus(
  scheduleId: number,
  status: string
): Promise<void> {
  await apiClient.patch(`/api/v1/dispatch/schedules/${scheduleId}`, { status })
}
