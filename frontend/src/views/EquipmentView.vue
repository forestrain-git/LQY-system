<template>
  <div class="equipment-view">
    <h1 class="page-title">设备管理</h1>
    <div class="placeholder">
      <Wrench class="placeholder__icon" />
      <p>设备管理功能开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Wrench } from 'lucide-vue-next'
</script>

<style scoped>
.equipment-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-text-primary);
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-20);
  color: var(--color-text-tertiary);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
}

.placeholder__icon {
  width: 64px;
  height: 64px;
  margin-bottom: var(--space-4);
  opacity: 0.5;
}
</style>
