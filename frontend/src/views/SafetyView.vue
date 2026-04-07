<template>
  <div class="safety-view">
    <h1 class="page-title">安全管控</h1>
    <div class="placeholder">
      <Shield class="placeholder__icon" />
      <p>安全管控功能开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Shield } from 'lucide-vue-next'
</script>

<style scoped>
.safety-view {
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
