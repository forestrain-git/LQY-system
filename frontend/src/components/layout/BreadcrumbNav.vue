<template>
  <el-breadcrumb separator="/" class="breadcrumb">
    <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
    <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index" :to="item.path">
      {{ item.title }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const $route = useRoute()

// 路由名称映射
const routeNameMap: Record<string, string> = {
  'Dashboard': '仪表盘',
  'DeviceList': '设备管理',
  'DeviceDetail': '设备详情',
  'AlertList': '告警中心',
  'AlertRules': '告警规则',
  'Settings': '系统设置'
}

const breadcrumbs = computed(() => {
  const items: Array<{ title: string; path?: string }> = []

  if ($route.name) {
    // 如果是详情页，添加列表页
    if ($route.name === 'DeviceDetail') {
      items.push({ title: '设备管理', path: '/devices' })
      items.push({ title: '设备详情' })
    } else if ($route.name === 'AlertRules') {
      items.push({ title: '告警中心', path: '/alerts' })
      items.push({ title: '告警规则' })
    } else {
      items.push({
        title: routeNameMap[$route.name as string] || $route.name as string
      })
    }
  }

  return items
})
</script>

<style scoped>
.breadcrumb {
  margin-bottom: 20px;
}

:deep(.el-breadcrumb__item) {
  color: var(--text-muted);
}

:deep(.el-breadcrumb__inner) {
  color: var(--text-secondary);
  font-weight: 500;
}

:deep(.el-breadcrumb__inner.is-link:hover) {
  color: var(--color-primary);
}

:deep(.el-breadcrumb__separator) {
  color: var(--text-muted);
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--text-primary);
  font-weight: 600;
}
</style>
