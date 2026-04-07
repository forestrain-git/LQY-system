<!--
  工单管理页面 / Work Order Management Page
  Author: AI Sprint
  Date: 2026-04-07
-->
<template>
  <div class="workorder-view">
    <div class="page-header">
      <h1 class="page-title">工单管理</h1>
      <button class="btn btn--primary">
        <Plus class="btn__icon" />
        新建工单
      </button>
    </div>
    <div class="placeholder">
      <ClipboardList class="placeholder__icon" />
      <p>工单管理功能开发中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Plus, ClipboardList } from 'lucide-vue-next'
</script>

<style scoped>
.workorder-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-text-primary);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: 500;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn--primary {
  background-color: var(--color-primary-600);
  color: white;
  border: none;
}

.btn--primary:hover {
  background-color: var(--color-primary-700);
}

.btn__icon {
  width: 16px;
  height: 16px;
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
