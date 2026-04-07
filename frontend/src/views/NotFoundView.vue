<template>
  <div class="not-found">
    <div class="not-found__content">
      <h1 class="not-found__code">404</h1>
      <p class="not-found__text">页面不存在</p>
      <router-link to="/" class="not-found__link">
        返回首页
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-secondary);
}

.not-found__content {
  text-align: center;
}

.not-found__code {
  font-size: 120px;
  font-weight: 700;
  color: var(--color-primary-500);
  line-height: 1;
}

.not-found__text {
  font-size: var(--text-xl);
  color: var(--color-text-secondary);
  margin: var(--space-4) 0;
}

.not-found__link {
  display: inline-block;
  padding: var(--space-3) var(--space-6);
  color: white;
  background-color: var(--color-primary-600);
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: background-color var(--transition-fast);
}

.not-found__link:hover {
  background-color: var(--color-primary-700);
}
</style>
