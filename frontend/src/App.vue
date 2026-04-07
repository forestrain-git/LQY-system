<template>
  <MainLayout />
</template>

<script setup lang="ts">
import MainLayout from './components/layout/MainLayout.vue'
</script>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  background: #0F0F0F;
  color: #F8F8F2;
  width: 100%;
  height: 100%;
}

#app {
  min-height: 100vh;
  background: #0F0F0F;
}
</style>