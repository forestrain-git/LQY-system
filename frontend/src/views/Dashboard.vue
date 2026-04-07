<template>
  <div class="dashboard">
    <h1 class="page-title">仪表盘</h1>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <StatCard
        title="设备总数"
        :value="18"
        icon="Monitor"
        icon-bg="rgba(62, 207, 142, 0.1)"
        icon-color="#3ECF8E"
        :trend="5"
      />
      <StatCard
        title="在线率"
        :value="66.7"
        icon="CircleCheck"
        icon-bg="rgba(189, 147, 249, 0.1)"
        icon-color="#BD93F9"
        value-color="#BD93F9"
        unit="%"
        :trend="-2"
      />
      <StatCard
        title="活跃告警"
        :value="3"
        icon="Bell"
        icon-bg="rgba(255, 121, 198, 0.1)"
        icon-color="#FF79C6"
        value-color="#FF79C6"
        :trend="-15"
      />
      <StatCard
        title="今日数据采集"
        :value="24567"
        icon="DataLine"
        icon-bg="rgba(255, 184, 108, 0.1)"
        icon-color="#FFB86C"
        value-color="#FFB86C"
        :trend="12"
      />
    </div>

    <!-- 图表区 -->
    <div class="charts-grid">
      <div class="chart-main">
        <RealtimeChart title="实时数据趋势" />
      </div>
      <div class="chart-side">
        <DeviceStatusChart />
      </div>
    </div>

    <!-- 最近告警 -->
    <div class="alerts-section">
      <RecentAlerts />
    </div>
  </div>
</template>

<script setup lang="ts">
import StatCard from '@/components/dashboard/StatCard.vue'
import RealtimeChart from '@/components/dashboard/RealtimeChart.vue'
import DeviceStatusChart from '@/components/dashboard/DeviceStatusChart.vue'
import RecentAlerts from '@/components/dashboard/RecentAlerts.vue'
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 24px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-main,
.chart-side {
  min-height: 400px;
}

.alerts-section {
  margin-top: 24px;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
