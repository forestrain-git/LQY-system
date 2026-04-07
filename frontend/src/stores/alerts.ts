import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Alert, AlertRule } from '@/types'

export interface AlertFilters {
  level: string[]
  status: string[]
  metric: string[]
  deviceId?: number
  startTime?: string
  endTime?: string
}

export const useAlertsStore = defineStore('alerts', () => {
  // State
  const alertList = ref<Alert[]>([])
  const alertRules = ref<AlertRule[]>([])
  const pagination = ref({
    page: 1,
    size: 20,
    total: 0,
  })
  const filters = ref<AlertFilters>({
    level: [],
    status: [],
    metric: [],
  })
  const selectedAlerts = ref<number[]>([])
  const loading = ref(false)

  // Getters
  const unreadAlerts = computed(() => {
    return alertList.value.filter(alert => alert.status === 'active')
  })

  // Actions
  const setAlertList = (alerts: Alert[]) => {
    alertList.value = alerts
  }

  const setAlertRules = (rules: AlertRule[]) => {
    alertRules.value = rules
  }

  const updateAlert = (alert: Alert) => {
    const index = alertList.value.findIndex(a => a.id === alert.id)
    if (index !== -1) {
      alertList.value[index] = alert
    }
  }

  const setSelectedAlerts = (ids: number[]) => {
    selectedAlerts.value = ids
  }

  const clearSelectedAlerts = () => {
    selectedAlerts.value = []
  }

  return {
    alertList,
    alertRules,
    pagination,
    filters,
    selectedAlerts,
    loading,
    unreadAlerts,
    setAlertList,
    setAlertRules,
    updateAlert,
    setSelectedAlerts,
    clearSelectedAlerts,
  }
})
