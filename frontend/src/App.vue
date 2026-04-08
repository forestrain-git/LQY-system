<template>
  <router-view />
</template>

<script setup lang="ts">
// App.vue 只负责渲染路由视图，布局由路由配置决定
</script>

<style>
/* 全局样式 - 高对比度主题支持 */
html, body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-base, #1e293b);
  color: var(--text-primary, #ffffff);
  width: 100%;
  height: 100%;
  font-family: 'Microsoft YaHei', 'SimHei', 'PingFang SC', sans-serif;
}

#app {
  min-height: 100vh;
  background-color: var(--bg-base, #1e293b);
  font-family: 'Microsoft YaHei', 'SimHei', 'PingFang SC', sans-serif;
}

/* 强制所有元素使用Windows系统字体 */
* {
  font-family: 'Microsoft YaHei', 'SimHei', sans-serif !important;
}

/* 图标例外 */
.el-icon, [class*="icon"] {
  font-family: 'element-icons', sans-serif !important;
}
</style>