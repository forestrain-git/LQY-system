<template>
  <div class="theme-switcher">
    <el-dropdown trigger="click" @command="handleThemeChange">
      <div class="theme-preview" :style="previewStyle">
        <el-icon><Brush /></el-icon>
        <span class="theme-name">{{ currentThemeLabel }}</span>
        <el-icon class="arrow-icon"><ArrowDown /></el-icon>
      </div>
      <template #dropdown>
        <el-dropdown-menu class="theme-dropdown">
          <div class="dropdown-header">选择主题</div>
          <el-dropdown-item
            v-for="theme in availableThemes"
            :key="theme.name"
            :command="theme.name"
            :class="{ active: currentTheme === theme.name }"
          >
            <div class="theme-option">
              <div class="color-dot" :style="getDotStyle(theme)"></div>
              <span class="theme-label">{{ theme.label }}</span>
              <span v-if="theme.isDark" class="dark-badge">深色</span>
              <span v-else class="light-badge">浅色</span>
              <el-icon v-if="currentTheme === theme.name" class="check-icon"><Check /></el-icon>
            </div>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Brush, ArrowDown, Check } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'
import type { DesignTheme } from '@/styles/awesome-design-themes'

const themeStore = useThemeStore()

const currentTheme = computed(() => themeStore.currentTheme.name)
const currentThemeLabel = computed(() => themeStore.currentTheme.label)
const availableThemes = computed(() => themeStore.availableThemes)

const previewStyle = computed(() => ({
  background: themeStore.themeColors.bgCard,
  borderColor: themeStore.themeColors.borderColor,
  color: themeStore.themeColors.textPrimary
}))

const getDotStyle = (theme: DesignTheme) => ({
  background: theme.colors.primary,
  boxShadow: `0 0 0 2px ${theme.colors.bgPrimary}, 0 0 0 4px ${theme.colors.borderColor}`
})

const handleThemeChange = (themeName: string) => {
  themeStore.setTheme(themeName)
}
</script>

<style scoped>
.theme-switcher {
  display: inline-flex;
}

.theme-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  font-weight: 500;
}

.theme-preview:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

.theme-name {
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow-icon {
  font-size: 12px;
  opacity: 0.6;
}

.dropdown-header {
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 4px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 180px;
  padding: 4px 0;
}

.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
}

.theme-label {
  flex: 1;
  font-size: 14px;
}

.dark-badge,
.light-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.dark-badge {
  background: #1f2937;
  color: #9ca3af;
}

.light-badge {
  background: #f3f4f6;
  color: #6b7280;
}

.check-icon {
  color: var(--color-primary);
  font-size: 14px;
}

:deep(.theme-dropdown) {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
  padding: 4px;
}

:deep(.theme-dropdown .el-dropdown-menu__item) {
  color: var(--text-primary) !important;
  border-radius: 6px;
  margin: 2px 0;
}

:deep(.theme-dropdown .el-dropdown-menu__item:hover) {
  background: var(--bg-hover) !important;
}

:deep(.theme-dropdown .el-dropdown-menu__item.active) {
  background: rgba(88, 166, 255, 0.1) !important;
}
</style>
