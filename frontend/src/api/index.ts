import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: (import.meta as any).env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('auth-token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    const data = response.data as ApiResponse<any>
    if (data.code !== 0) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    return response
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '网络错误'

    // 处理401未授权
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-token')
      window.location.href = '/login'
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default apiClient

// 导出所有API服务（排除重复类型）
export * from './dashboard'
export {
  getSafetyAlerts,
  getActiveAlertsCount,
  getRiskDistribution,
  getSafetyRecommendations,
  acknowledgeAlert,
  resolveAlert,
  type SafetyAlert
} from './safety'
export {
  getVehicles,
  getAvailableBerths,
  getDispatchQueue,
  createSchedule,
  updateScheduleStatus,
  type Vehicle,
  type Berth,
  type Schedule
} from './dispatch'
export {
  getWorkOrders,
  getPendingWorkOrdersCount,
  getWorkOrder,
  createWorkOrder,
  updateWorkOrderStatus,
  assignWorkOrder,
  type WorkOrder
} from './workorder'