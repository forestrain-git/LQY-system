// 设备类型映射
export const DEVICE_TYPE_MAP: Record<string, string> = {
  compressor: '压缩机',
  pump: '泵',
  fan: '风机',
  conveyor: '传送带',
  other: '其他',
}

// 设备状态映射
export const DEVICE_STATUS_MAP: Record<string, { label: string; type: string }> = {
  online: { label: '在线', type: 'success' },
  offline: { label: '离线', type: 'danger' },
  maintenance: { label: '维护中', type: 'warning' },
  disabled: { label: '已禁用', type: 'info' },
}

// 告警级别映射
export const ALERT_LEVEL_MAP: Record<string, { label: string; type: string }> = {
  critical: { label: '严重', type: 'danger' },
  warning: { label: '警告', type: 'warning' },
  info: { label: '提示', type: 'info' },
}

// 告警状态映射
export const ALERT_STATUS_MAP: Record<string, { label: string; type: string }> = {
  active: { label: '未处理', type: 'danger' },
  acknowledged: { label: '已确认', type: 'warning' },
  resolved: { label: '已解决', type: 'success' },
}

// 告警指标映射
export const ALERT_METRIC_MAP: Record<string, string> = {
  temperature: '温度',
  vibration: '振动',
  current: '电流',
  system: '系统',
}
