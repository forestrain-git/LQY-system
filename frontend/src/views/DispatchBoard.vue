<!--
  调度看板页面 / Dispatch Board Page

  实时展示车辆调度、泊位状态、队列信息
  Real-time display of vehicle dispatch, berth status, queue info

  Author: AI Sprint
  Date: 2026-04-07
-->
<template>
  <div class="dispatch-board">
    <!-- 统计卡片 / Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--blue">
          <Truck />
        </div>
        <div class="stat-card__content">
          <div class="stat-card__value">{{ stats.totalVehicles }}</div>
          <div class="stat-card__label">在场车辆</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--green">
          <CheckCircle2 />
        </div>
        <div class="stat-card__content">
          <div class="stat-card__value">{{ stats.availableBerths }}</div>
          <div class="stat-card__label">空闲泊位</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--orange">
          <Clock />
        </div>
        <div class="stat-card__content">
          <div class="stat-card__value">{{ stats.queueCount }}</div>
          <div class="stat-card__label">排队车辆</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--purple">
          <Activity />
        </div>
        <div class="stat-card__content">
          <div class="stat-card__value">{{ stats.avgWaitTime }}分</div>
          <div class="stat-card__label">平均等待</div>
        </div>
      </div>
    </div>

    <!-- 主要内容区 / Main Content -->
    <div class="board-grid">
      <!-- 车辆队列 / Vehicle Queue -->
      <div class="board-section">
        <div class="section-header">
          <h2 class="section-title">
            <List class="section-icon" />
            车辆队列
          </h2>
          <span class="badge">{{ queue.length }}</span>
        </div>
        <div class="section-body">
          <div v-if="queue.length === 0" class="empty-state">
            <Inbox class="empty-state__icon" />
            <p>暂无排队车辆</p>
          </div>
          <div v-else class="queue-list">
            <div
              v-for="item in queue"
              :key="item.id"
              class="queue-item"
            >
              <div class="queue-item__rank">{{ item.queueNumber }}</div>
              <div class="queue-item__info">
                <div class="queue-item__plate">{{ item.vehiclePlate }}</div>
                <div class="queue-item__type">{{ item.wasteType }}</div>
              </div>
              <div class="queue-item__wait">{{ item.waitTime }}分</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 泊位状态 / Berth Status -->
      <div class="board-section">
        <div class="section-header">
          <h2 class="section-title">
            <MapPin class="section-icon" />
            泊位状态
          </h2>
          <span class="badge">{{ berths.length }}</span>
        </div>
        <div class="section-body">
          <div class="berth-grid">
            <div
              v-for="berth in berths"
              :key="berth.id"
              class="berth-card"
              :class="`berth-card--${berth.status}`"
            >
              <div class="berth-card__header">
                <span class="berth-card__code">{{ berth.code }}</span>
                <span class="berth-card__type">{{ berth.type }}</span>
              </div>
              <div class="berth-card__body">
                <div v-if="berth.currentVehicle" class="berth-card__vehicle">
                  <Truck class="berth-card__vehicle-icon" />
                  <span>{{ berth.currentVehicle }}</span>
                </div>
                <div v-else class="berth-card__empty">
                  空闲
                </div>
              </div>
              <div class="berth-card__footer">
                <span class="berth-card__capacity">{{ berth.capacity }}吨</span>
                <span
                  class="berth-card__status"
                  :class="`berth-card__status--${berth.status}`"
                >
                  {{ berth.statusText }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Truck, CheckCircle2, Clock, Activity,
  List, MapPin, Inbox
} from 'lucide-vue-next'

// 统计数据 / Statistics
const stats = ref({
  totalVehicles: 12,
  availableBerths: 5,
  queueCount: 3,
  avgWaitTime: 8
})

// 队列数据 / Queue data
const queue = ref([
  { id: 1, queueNumber: 1, vehiclePlate: '川A12345', wasteType: '生活垃圾', waitTime: 5 },
  { id: 2, queueNumber: 2, vehiclePlate: '川A67890', wasteType: '厨余垃圾', waitTime: 12 },
  { id: 3, queueNumber: 3, vehiclePlate: '川A11111', wasteType: '可回收物', waitTime: 18 },
])

// 泊位数据 / Berth data
const berths = ref([
  { id: 1, code: 'A01', type: '生活垃圾', status: 'occupied', statusText: '占用', capacity: 10, currentVehicle: '川A54321' },
  { id: 2, code: 'A02', type: '生活垃圾', status: 'available', statusText: '空闲', capacity: 10, currentVehicle: null },
  { id: 3, code: 'B01', type: '厨余垃圾', status: 'occupied', statusText: '占用', capacity: 8, currentVehicle: '川A98765' },
  { id: 4, code: 'B02', type: '厨余垃圾', status: 'available', statusText: '空闲', capacity: 8, currentVehicle: null },
  { id: 5, code: 'C01', type: '可回收物', status: 'available', statusText: '空闲', capacity: 5, currentVehicle: null },
  { id: 6, code: 'D01', type: '有害垃圾', status: 'maintenance', statusText: '维护', capacity: 3, currentVehicle: null },
])

onMounted(() => {
  // TODO: 从API获取数据 / Fetch data from API
})
</script>

<style scoped>
.dispatch-board {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

/* 统计卡片 / Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
}

.stat-card__icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
}

.stat-card__icon--blue {
  background-color: var(--color-accent-info);
  color: white;
}

.stat-card__icon--green {
  background-color: var(--color-accent-success);
  color: white;
}

.stat-card__icon--orange {
  background-color: var(--color-accent-warning);
  color: white;
}

.stat-card__icon--purple {
  background-color: var(--color-primary-500);
  color: white;
}

.stat-card__value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-card__label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-top: 2px;
}

/* 看板网格 / Board Grid */
.board-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--space-6);
}

.board-section {
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border-secondary);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.section-icon {
  width: 18px;
  height: 18px;
  color: var(--color-text-secondary);
}

.badge {
  padding: 2px 10px;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
}

.section-body {
  padding: var(--space-4);
}

/* 空状态 / Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  color: var(--color-text-tertiary);
}

.empty-state__icon {
  width: 48px;
  height: 48px;
  margin-bottom: var(--space-3);
  opacity: 0.5;
}

/* 队列列表 / Queue List */
.queue-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.queue-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.queue-item__rank {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-primary-600);
  background-color: var(--color-primary-50);
  border-radius: var(--radius-full);
}

.queue-item__info {
  flex: 1;
}

.queue-item__plate {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.queue-item__type {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.queue-item__wait {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-accent-warning);
}

/* 泊位网格 / Berth Grid */
.berth-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.berth-card {
  padding: var(--space-4);
  border: 2px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.berth-card--available {
  border-color: var(--color-accent-success);
  background-color: rgba(34, 197, 94, 0.05);
}

.berth-card--occupied {
  border-color: var(--color-accent-warning);
  background-color: rgba(249, 115, 22, 0.05);
}

.berth-card--maintenance {
  border-color: var(--color-accent-danger);
  background-color: rgba(239, 68, 68, 0.05);
}

.berth-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.berth-card__code {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text-primary);
}

.berth-card__type {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.berth-card__body {
  min-height: 40px;
  display: flex;
  align-items: center;
}

.berth-card__vehicle {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

.berth-card__vehicle-icon {
  width: 16px;
  height: 16px;
  color: var(--color-accent-warning);
}

.berth-card__empty {
  font-size: var(--text-sm);
  color: var(--color-accent-success);
}

.berth-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-secondary);
}

.berth-card__capacity {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.berth-card__status {
  padding: 2px 8px;
  font-size: var(--text-xs);
  font-weight: 500;
  border-radius: var(--radius-full);
}

.berth-card__status--available {
  color: var(--color-accent-success);
  background-color: rgba(34, 197, 94, 0.1);
}

.berth-card__status--occupied {
  color: var(--color-accent-warning);
  background-color: rgba(249, 115, 22, 0.1);
}

.berth-card__status--maintenance {
  color: var(--color-accent-danger);
  background-color: rgba(239, 68, 68, 0.1);
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .board-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .berth-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
