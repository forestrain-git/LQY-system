export interface SensorData {
  id: number
  device_id: number
  device_name?: string
  temperature: number
  vibration: number
  current: number
  timestamp: string
  anomaly?: boolean
}

export interface SensorDataQuery {
  device_id?: number
  start?: string
  end?: string
  page?: number
  size?: number
}

export interface RealtimeDataPoint {
  timestamp: string
  value: number
  deviceId: number
}
