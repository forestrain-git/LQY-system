<template>
  <el-menu
    :default-active="$route.path"
    router
    :collapse="layoutStore.sidebarCollapsed"
    :collapse-transition="false"
    background-color="#0F0F0F"
    text-color="#B0B0B0"
    active-text-color="#3ECF8E"
  >
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <template #title>
        <span>仪表盘</span>
      </template>
    </el-menu-item>

    <el-menu-item index="/devices">
      <el-icon><Monitor /></el-icon>
      <template #title>
        <span>设备管理</span>
      </template>
    </el-menu-item>

    <el-menu-item index="/alerts">
      <el-icon><Bell /></el-icon>
      <template #title>
        <span>告警中心</span>
        <el-badge
          v-if="alertsStore.unreadAlerts.length > 0 && !layoutStore.sidebarCollapsed"
          :value="alertsStore.unreadAlerts.length"
          class="menu-badge"
          type="danger"
        />
      </template>
    </el-menu-item>

    <el-menu-item index="/settings">
      <el-icon><Setting /></el-icon>
      <template #title>
        <span>系统设置</span>
      </template>
    </el-menu-item>

    <el-menu-item index="/test">
      <el-icon><CircleCheck /></el-icon>
      <template #title>
        <span>测试页面</span>
      </template>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useLayoutStore } from '@/stores/layout'
import { useAlertsStore } from '@/stores/alerts'

const $route = useRoute()
const layoutStore = useLayoutStore()
const alertsStore = useAlertsStore()
</script>

<style scoped>
.el-menu {
  border-right: none;
  flex: 1;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 8px;
}

.el-menu-item:hover {
  background-color: #1C1C1C !important;
  color: #F8F8F2 !important;
}

.el-menu-item.is-active {
  background-color: #252525 !important;
  border-left: 3px solid #3ECF8E;
}

.menu-badge {
  margin-left: 8px;
}

:deep(.el-badge__content) {
  background-color: #FF79C6;
  border: none;
}
</style>
