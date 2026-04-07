<template>
  <div class="device-list">
    <div class="page-header">
      <h1 class="page-title">设备管理</h1>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索设备名称/位置"
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>
          添加设备
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-value online">{{ onlineCount }}</div>
        <div class="stat-label">在线设备</div>
      </div>
      <div class="stat-item">
        <div class="stat-value offline">{{ offlineCount }}</div>
        <div class="stat-label">离线设备</div>
      </div>
      <div class="stat-item">
        <div class="stat-value warning">{{ maintenanceCount }}</div>
        <div class="stat-label">维护中</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ totalCount }}</div>
        <div class="stat-label">设备总数</div>
      </div>
    </div>

    <!-- 设备表格 -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>设备名称</th>
            <th>类型</th>
            <th>位置</th>
            <th>状态</th>
            <th>最新数据</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="device in paginatedDevices" :key="device.id">
            <td>{{ device.id }}</td>
            <td>
              <div class="device-name">
                <el-icon :size="18" :color="getStatusColor(device.status)">
                  <Monitor />
                </el-icon>
                <span>{{ device.name }}</span>
              </div>
            </td>
            <td>
              <span class="type-tag" :class="device.type">
                {{ deviceTypeText(device.type) }}
              </span>
            </td>
            <td>{{ device.location }}</td>
            <td>
              <span class="status-badge" :class="device.status">
                {{ statusText(device.status) }}
              </span>
            </td>
            <td>
              <div v-if="device.latest_sensor_data" class="sensor-data">
                <span class="sensor-item temp">
                  {{ device.latest_sensor_data.temperature.toFixed(1) }}°C
                </span>
                <span class="sensor-item vibration">
                  {{ device.latest_sensor_data.vibration.toFixed(2) }}mm/s
                </span>
                <span class="sensor-item current">
                  {{ device.latest_sensor_data.current.toFixed(1) }}A
                </span>
              </div>
              <span v-else class="no-data">暂无数据</span>
            </td>
            <td>
              <div class="actions">
                <el-button link type="primary" @click="viewDevice(device)">查看</el-button>
                <el-button link type="primary" @click="editDevice(device)">编辑</el-button>
                <el-button link type="danger" @click="deleteDevice(device)">删除</el-button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="filteredDevices.length"
        :page-sizes="[5, 10, 20]"
        layout="total, sizes, prev, pager, next"
      />
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑设备' : '添加设备'"
      width="500px"
      destroy-on-close
    >
      <el-form :model="deviceForm" label-width="80px">
        <el-form-item label="设备名称">
          <el-input v-model="deviceForm.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="deviceForm.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="压缩机" value="compressor" />
            <el-option label="泵机" value="pump" />
            <el-option label="风机" value="fan" />
            <el-option label="输送机" value="conveyor" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="deviceForm.location" placeholder="请输入设备位置" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="deviceForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
            <el-option label="维护中" value="maintenance" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDevice">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 数据
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const isEdit = ref(false)

const deviceForm = ref({
  id: 0,
  name: '',
  type: 'compressor',
  location: '',
  status: 'online'
})

// 模拟设备数据
const devices = ref([
  { id: 1, name: '压缩机-A01', type: 'compressor', location: 'A区-车间1', status: 'online', latest_sensor_data: { temperature: 65.2, vibration: 3.5, current: 15.3 } },
  { id: 2, name: '泵机-B02', type: 'pump', location: 'B区-水泵房', status: 'online', latest_sensor_data: { temperature: 52.1, vibration: 2.1, current: 12.8 } },
  { id: 3, name: '风机-C03', type: 'fan', location: 'C区-通风系统', status: 'warning', latest_sensor_data: { temperature: 78.5, vibration: 5.8, current: 18.2 } },
  { id: 4, name: '输送机-D04', type: 'conveyor', location: 'D区-包装线', status: 'offline', latest_sensor_data: null },
  { id: 5, name: '压缩机-A02', type: 'compressor', location: 'A区-车间2', status: 'online', latest_sensor_data: { temperature: 58.3, vibration: 2.8, current: 14.1 } },
  { id: 6, name: '泵机-B03', type: 'pump', location: 'B区-循环水', status: 'maintenance', latest_sensor_data: { temperature: 45.2, vibration: 1.9, current: 10.5 } },
  { id: 7, name: '风机-C04', type: 'fan', location: 'C区-排风系统', status: 'online', latest_sensor_data: { temperature: 62.1, vibration: 3.2, current: 13.5 } },
  { id: 8, name: '输送机-D05', type: 'conveyor', location: 'D区-输送线', status: 'online', latest_sensor_data: { temperature: 55.4, vibration: 2.5, current: 11.8 } }
])

// 统计计算
const onlineCount = computed(() => devices.value.filter(d => d.status === 'online').length)
const offlineCount = computed(() => devices.value.filter(d => d.status === 'offline').length)
const maintenanceCount = computed(() => devices.value.filter(d => d.status === 'maintenance').length)
const totalCount = computed(() => devices.value.length)

// 筛选和分页
const filteredDevices = computed(() => {
  let result = devices.value
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(d =>
      d.name.toLowerCase().includes(query) ||
      d.location.toLowerCase().includes(query)
    )
  }
  return result
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

// 辅助函数
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    online: '#3ECF8E',
    offline: '#FF79C6',
    maintenance: '#FFB86C'
  }
  return colors[status] || '#666'
}

const deviceTypeText = (type: string) => {
  const texts: Record<string, string> = {
    compressor: '压缩机', pump: '泵机', fan: '风机',
    conveyor: '输送机', other: '其他'
  }
  return texts[type] || type
}

const statusText = (status: string) => {
  const texts: Record<string, string> = {
    online: '在线', offline: '离线', maintenance: '维护中'
  }
  return texts[status] || status
}

// 操作
const openAddDialog = () => {
  isEdit.value = false
  deviceForm.value = { id: 0, name: '', type: 'compressor', location: '', status: 'online' }
  dialogVisible.value = true
}

const editDevice = (device: any) => {
  isEdit.value = true
  deviceForm.value = { ...device }
  dialogVisible.value = true
}

const saveDevice = () => {
  if (isEdit.value) {
    const index = devices.value.findIndex(d => d.id === deviceForm.value.id)
    if (index > -1) {
      devices.value[index] = { ...devices.value[index], ...deviceForm.value }
    }
  } else {
    const newId = Math.max(...devices.value.map(d => d.id)) + 1
    devices.value.push({
      ...deviceForm.value,
      id: newId,
      latest_sensor_data: null
    })
  }
  dialogVisible.value = false
}

const deleteDevice = (device: any) => {
  devices.value = devices.value.filter(d => d.id !== device.id)
}

const viewDevice = (device: any) => {
  router.push(`/devices/${device.id}`)
}
</script>

<style scoped>
.device-list {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 280px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-value.online { color: #3ECF8E; }
.stat-value.offline { color: #FF79C6; }
.stat-value.warning { color: #FFB86C; }

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.table-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.data-table th {
  background: rgba(255, 255, 255, 0.02);
  font-weight: 600;
  color: var(--text-secondary);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.device-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-tag {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  background: rgba(62, 207, 142, 0.1);
  color: #3ECF8E;
}

.type-tag.pump {
  background: rgba(189, 147, 249, 0.1);
  color: #BD93F9;
}

.type-tag.fan {
  background: rgba(255, 184, 108, 0.1);
  color: #FFB86C;
}

.type-tag.conveyor {
  background: rgba(98, 114, 164, 0.1);
  color: #6272A4;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
}

.status-badge.online {
  background: rgba(62, 207, 142, 0.1);
  color: #3ECF8E;
}

.status-badge.offline {
  background: rgba(255, 121, 198, 0.1);
  color: #FF79C6;
}

.status-badge.maintenance {
  background: rgba(255, 184, 108, 0.1);
  color: #FFB86C;
}

.sensor-data {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.sensor-item {
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
}

.sensor-item.temp { color: #FF79C6; }
.sensor-item.vibration { color: #BD93F9; }
.sensor-item.current { color: #3ECF8E; }

.no-data {
  color: var(--text-muted);
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
}
</style>
