<!--
  主题切换组件 / Theme Switcher Component

  允许用户在 Cursor/Linear/Kraken 三套主题间切换
  Allows users to switch between Cursor/Linear/Kraken themes

  Author: AI Sprint
  Date: 2026-04-07
-->
<template>
  <div class="theme-switcher">
    <!-- 触发按钮 / Trigger button -->
    <button
      class="theme-switcher__trigger"
      @click="isOpen = !isOpen"
      :title="'切换主题'"
    >
      <component :is="currentIcon" class="theme-switcher__icon" />
      <span class="theme-switcher__label">{{ themeConfig.label }}</span>
      <ChevronDown class="theme-switcher__arrow" :class="{ 'is-open': isOpen }" />
    </button>

    <!-- 下拉菜单 / Dropdown -->
    <Transition name="dropdown">
      <div v-if="isOpen" class="theme-switcher__dropdown" v-click-outside="close">
        <div class="theme-switcher__header">
          选择主题
        </div>

        <div class="theme-switcher__options">
          <button
            v-for="t in themes"
            :key="t.name"
            class="theme-switcher__option"
            :class="{ 'is-active': theme === t.name }"
            @click="selectTheme(t.name)"
          >
            <div
              class="theme-switcher__preview"
              :style="{ background: t.colors.background }"
            >
              <div
                class="theme-switcher__preview-dot"
                :style="{ background: t.colors.primary }"
              />
            </div>

            <div class="theme-switcher__info">
              <div class="theme-switcher__name">{{ t.label }}</div>
              <div class="theme-switcher__desc">{{ t.description }}</div>
            </div>

            <Check
              v-if="theme === t.name"
              class="theme-switcher__check"
            />
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Code, Layout, TrendingUp, ChevronDown, Check } from 'lucide-vue-next'
import { useTheme, THEMES, type Theme } from '@/composables/useTheme'
import { vClickOutside } from '@/directives/clickOutside'

// 使用主题 / Use theme
const { theme, themeConfig, themes, setTheme } = useTheme()

// 下拉状态 / Dropdown state
const isOpen = ref(false)

// 当前图标 / Current icon
const currentIcon = computed(() => {
  switch (theme.value) {
    case 'cursor': return Code
    case 'linear': return Layout
    case 'kraken': return TrendingUp
    default: return Code
  }
})

// 选择主题 / Select theme
const selectTheme = (newTheme: Theme): void => {
  setTheme(newTheme)
  isOpen.value = false
}

// 关闭下拉 / Close dropdown
const close = (): void => {
  isOpen.value = false
}
</script>

<style scoped>
.theme-switcher {
  position: relative;
  display: inline-block;
}

.theme-switcher__trigger {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.theme-switcher__trigger:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.theme-switcher__icon {
  width: 16px;
  height: 16px;
}

.theme-switcher__label {
  font-weight: 500;
}

.theme-switcher__arrow {
  width: 14px;
  height: 14px;
  transition: transform var(--transition-fast);
}

.theme-switcher__arrow.is-open {
  transform: rotate(180deg);
}

/* 下拉菜单 / Dropdown */
.theme-switcher__dropdown {
  position: absolute;
  top: calc(100% + var(--space-2));
  right: 0;
  min-width: 240px;
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 100;
  overflow: hidden;
}

.theme-switcher__header {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-tertiary);
  border-bottom: 1px solid var(--color-border-secondary);
}

.theme-switcher__options {
  padding: var(--space-2);
}

.theme-switcher__option {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3);
  text-align: left;
  background: none;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.theme-switcher__option:hover {
  background-color: var(--color-bg-tertiary);
}

.theme-switcher__option.is-active {
  background-color: var(--color-primary-50);
}

.theme-switcher__preview {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-primary);
}

.theme-switcher__preview-dot {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
}

.theme-switcher__info {
  flex: 1;
  min-width: 0;
}

.theme-switcher__name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.theme-switcher__desc {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: 2px;
}

.theme-switcher__check {
  width: 16px;
  height: 16px;
  color: var(--color-primary-600);
}

/* 动画 / Animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all var(--transition-fast);
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
