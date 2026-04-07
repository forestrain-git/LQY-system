<template>
  <div class="stat-card" :class="{ 'has-trend': trend !== undefined }">
    <div class="stat-icon" :style="{ background: iconBg }">
      <el-icon :size="24" :color="iconColor">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-content">
      <div class="stat-title">{{ title }}</div>
      <div class="stat-value" :style="{ color: valueColor }">{{ formattedValue }}</div>
      <div v-if="trend !== undefined" class="stat-trend" :class="trendClass">
        <el-icon size="14">
          <ArrowUp v-if="trend > 0" />
          <ArrowDown v-else-if="trend < 0" />
          <Minus v-else />
        </el-icon>
        <span>{{ Math.abs(trend) }}%</span>
        <span class="trend-label">vs 昨日</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: number | string
  icon: string
  iconBg?: string
  iconColor?: string
  valueColor?: string
  trend?: number // 正数表示上升，负数表示下降
  unit?: string
}

const props = withDefaults(defineProps<Props>(), {
  iconBg: 'rgba(62, 207, 142, 0.1)',
  iconColor: '#3ECF8E',
  valueColor: '#F8F8F2',
  unit: ''
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString() + props.unit
  }
  return props.value + props.unit
})

const trendClass = computed(() => {
  if (props.trend === undefined) return ''
  if (props.trend > 0) return 'up'
  if (props.trend < 0) return 'down'
  return 'neutral'
})
</script>

<style scoped>
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-color: var(--color-primary);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-title {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: 8px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend.up {
  color: #FF79C6;
}

.stat-trend.down {
  color: #3ECF8E;
}

.stat-trend.neutral {
  color: var(--text-muted);
}

.trend-label {
  color: var(--text-muted);
  font-weight: normal;
  margin-left: 4px;
}
</style>
