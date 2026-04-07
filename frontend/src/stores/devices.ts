import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Device, DeviceCreate, DeviceUpdate, DeviceStats } from '@/types'

export const useDevicesStore = defineStore('devices', () => {
  // State
  const deviceList = ref<Device[]>([])
  const currentDevice = ref<Device | null>(null)
  const deviceStats = ref<DeviceStats | null>(null)
  const loading = ref(false)

  // Actions
  const setDeviceList = (devices: Device[]) => {
    deviceList.value = devices
  }

  const setCurrentDevice = (device: Device | null) => {
    currentDevice.value = device
  }

  const setDeviceStats = (stats: DeviceStats) => {
    deviceStats.value = stats
  }

  const updateDeviceInList = (device: Device) => {
    const index = deviceList.value.findIndex(d => d.id === device.id)
    if (index !== -1) {
      deviceList.value[index] = device
    }
  }

  return {
    deviceList,
    currentDevice,
    deviceStats,
    loading,
    setDeviceList,
    setCurrentDevice,
    setDeviceStats,
    updateDeviceInList,
  }
})
