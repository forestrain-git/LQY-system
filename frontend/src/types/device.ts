import type { SensorData } from './sensor'
export { SensorData }

export enum DeviceType {
  COMPRESSOR = 'compressor',
  PUMP = 'pump',
  FAN = 'fan',
  CONVEYOR = 'conveyor',
  OTHER = 'other',
}

export enum DeviceStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  MAINTENANCE = 'maintenance',
  DISABLED = 'disabled',
}

export interface Device {
  id: number
  name: string
  type: DeviceType
  location?: string
  status: DeviceStatus
  created_at: string
  updated_at: string
  latest_sensor_data?: SensorData
}

export interface DeviceCreate {
  name: string
  type: DeviceType
  location?: string
  status?: DeviceStatus
}

export interface DeviceUpdate {
  name?: string
  type?: DeviceType
  location?: string
  status?: DeviceStatus
}

export interface DeviceStats {
  total_records: number
  avg_temperature?: number
  avg_vibration?: number
  avg_current?: number
  latest_timestamp?: string
}
