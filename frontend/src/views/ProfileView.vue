<template>
  <div class="profile-view">
    <h1 class="page-title">个人中心</h1>
    <div class="placeholder">
      <User class="placeholder__icon" />
      <p>个人中心功能开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User } from 'lucide-vue-next'
</script>

<style scoped>
.profile-view {
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
