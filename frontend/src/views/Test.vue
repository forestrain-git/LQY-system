<template>
  <div style="padding: 20px;">
    <h1>测试页面</h1>
    <p>如果看到这个页面，说明路由正常工作</p>
    <button @click="goBack" style="padding: 10px 20px; margin-top: 20px; cursor: pointer;">
      返回仪表盘
    </button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.push('/')
}
</script>
