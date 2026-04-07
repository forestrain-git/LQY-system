<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside
      width="220px"
      class="sidebar"
      :class="{ collapsed: layoutStore.sidebarCollapsed }"
    >
      <div class="sidebar-header">
        <div v-if="!layoutStore.sidebarCollapsed" class="logo">
          <el-icon :size="32" color="#3ECF8E"><Monitor /></el-icon>
          <span class="logo-text">LQY系统</span>
        </div>
        <el-icon v-else :size="32" color="#3ECF8E"><Monitor /></el-icon>
      </div>

      <SidebarMenu />

      <div class="sidebar-footer">
        <el-button
          text
          class="collapse-btn"
          @click="layoutStore.toggleSidebar()"
        >
          <el-icon v-if="!layoutStore.sidebarCollapsed"><Fold /></el-icon>
          <el-icon v-else><Expand /></el-icon>
        </el-button>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <el-header class="header">
        <AppHeader />
      </el-header>

      <el-main class="main-content">
        <BreadcrumbNav class="breadcrumb" />
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>

      <el-footer class="footer">
        <div class="copyright">
          © 2026 龙泉驿环卫智能体 v1.0
        </div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useLayoutStore } from '@/stores/layout'
import SidebarMenu from './SidebarMenu.vue'
import AppHeader from './AppHeader.vue'
import BreadcrumbNav from './BreadcrumbNav.vue'

const layoutStore = useLayoutStore()
</script>

<style scoped>
.main-layout {
  height: 100vh;
  background: var(--bg-primary);
}

.sidebar {
  background: var(--bg-primary);
  border-right: 1px solid var(--divider);
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed {
  width: 64px !important;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--divider);
  padding: 0 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, #3ECF8E 0%, #BD93F9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-footer {
  margin-top: auto;
  padding: 16px;
  border-top: 1px solid var(--divider);
}

.collapse-btn {
  width: 100%;
  color: var(--text-secondary);
}

.collapse-btn:hover {
  color: var(--color-primary);
}

.main-container {
  background: var(--bg-primary);
}

.header {
  height: 64px;
  padding: 0;
  background: rgba(15, 15, 15, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--divider);
}

.main-content {
  padding: 20px;
  background: var(--bg-primary);
  overflow-y: auto;
}

.breadcrumb {
  margin-bottom: 20px;
}

.footer {
  height: 48px;
  background: var(--bg-primary);
  border-top: 1px solid var(--divider);
  display: flex;
  align-items: center;
  justify-content: center;
}

.copyright {
  color: var(--text-muted);
  font-size: 12px;
}

/* 页面切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
