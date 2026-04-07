export enum AlertType {
  THRESHOLD = 'threshold',
  TREND = 'trend',
  PREDICTION = 'prediction',
  SYSTEM = 'system',
}

export enum AlertMetric {
  TEMPERATURE = 'temperature',
  VIBRATION = 'vibration',
  CURRENT = 'current',
  SYSTEM = 'system',
}

export enum AlertLevel {
  CRITICAL = 'critical',
  WARNING = 'warning',
  INFO = 'info',
}

export enum AlertStatus {
  ACTIVE = 'active',
  ACKNOWLEDGED = 'acknowledged',
  RESOLVED = 'resolved',
}

export interface Alert {
  id: number
  device_id: number
  device_name?: string
  alert_type: AlertType
  metric: AlertMetric
  message: string
  level: AlertLevel
  status: AlertStatus
  created_at: string
  acknowledged_at?: string
  resolved_at?: string
}

export interface AlertRule {
  id: number
  device_id?: number
  metric: AlertMetric
  operator: 'gt' | 'lt' | 'eq'
  threshold: number
  duration: number
  enabled: boolean
  description?: string
}

export interface AlertStats {
  total: number
  critical: number
  warning: number
  info: number
  by_metric: Record<AlertMetric, number>
}
