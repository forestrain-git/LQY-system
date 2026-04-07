<template>
  <div class="device-detail">
    <div class="page-header">
      <el-button text class="back-btn" @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1 class="page-title">设备详情</h1>
    </div>
    <p class="placeholder-text">设备详情将在这里显示</p>
  </div>
</template>

<style scoped>
.device-detail {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  color: var(--text-secondary);
  font-size: 14px;
}

.back-btn:hover {
  color: var(--color-primary);
}

.page-title {
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.placeholder-text {
  color: var(--text-secondary);
  text-align: center;
  padding: 40px;
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--divider);
}
</style>
