// 通用类型定义
export * from './alert'
export * from './device'
export * from './sensor'

export interface PaginationParams {
  page: number
  size: number
}

export interface PaginationResult {
  page: number
  size: number
  total: number
  pages: number
}

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  pagination?: PaginationResult
}
