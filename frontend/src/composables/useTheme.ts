/**
 * 主题管理组合式函数 / Theme Management Composable
 *
 * 管理三套主题的切换和持久化
 * Manages switching and persistence of 3 themes
 *
 * Author: AI Sprint
 * Date: 2026-04-07
 */

import { ref, computed, watch, type Ref } from 'vue'

/**
 * 主题类型 / Theme types
 */
export type Theme = 'cursor' | 'linear' | 'kraken'

/**
 * 主题配置 / Theme configuration
 */
export interface ThemeConfig {
  name: Theme
  label: string
  labelEn: string
  description: string
  icon: string
  colors: {
    primary: string
    background: string
    text: string
  }
}

/**
 * 主题配置列表 / Theme configurations
 */
export const THEMES: ThemeConfig[] = [
  {
    name: 'cursor',
    label: 'Cursor',
    labelEn: 'Cursor',
    description: '深色开发者主题 / Dark developer theme',
    icon: 'Code',
    colors: {
      primary: '#22c55e',
      background: '#0d1117',
      text: '#f0f6fc'
    }
  },
  {
    name: 'linear',
    label: 'Linear',
    labelEn: 'Linear',
    description: '浅色专业主题 / Light professional theme',
    icon: 'Layout',
    colors: {
      primary: '#8b5cf6',
      background: '#ffffff',
      text: '#111827'
    }
  },
  {
    name: 'kraken',
    label: 'Kraken',
    labelEn: 'Kraken',
    description: '深色金融主题 / Dark finance theme',
    icon: 'TrendingUp',
    colors: {
      primary: '#f97316',
      background: '#0a0e1a',
      text: '#f9fafb'
    }
  }
]

/**
 * 存储键 / Storage key
 */
const STORAGE_KEY = 'lqy-theme-preference'

/**
 * 当前主题 / Current theme ref
 */
const currentTheme: Ref<Theme> = ref('cursor')

/**
 * 初始化主题 / Initialize theme
 */
export function initTheme(): void {
  // 尝试从 localStorage 读取 / Try read from localStorage
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved && THEMES.find(t => t.name === saved)) {
    currentTheme.value = saved as Theme
  } else {
    // 检测系统偏好 / Detect system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    currentTheme.value = prefersDark ? 'cursor' : 'linear'
  }

  // 应用主题 / Apply theme
  applyTheme(currentTheme.value)
}

/**
 * 应用主题到 DOM / Apply theme to DOM
 */
export function applyTheme(theme: Theme): void {
  document.documentElement.setAttribute('data-theme', theme)
  currentTheme.value = theme
  localStorage.setItem(STORAGE_KEY, theme)
}

/**
 * 主题管理组合式函数 / Theme management composable
 */
export function useTheme() {
  /**
   * 当前主题 / Current theme
   */
  const theme = computed(() => currentTheme.value)

  /**
   * 当前主题配置 / Current theme config
   */
  const themeConfig = computed(() =>
    THEMES.find(t => t.name === currentTheme.value) || THEMES[0]
  )

  /**
   * 是否深色主题 / Is dark theme
   */
  const isDark = computed(() =>
    currentTheme.value === 'cursor' || currentTheme.value === 'kraken'
  )

  /**
   * 设置主题 / Set theme
   */
  const setTheme = (newTheme: Theme): void => {
    applyTheme(newTheme)
  }

  /**
   * 切换主题 / Toggle theme
   */
  const toggleTheme = (): void => {
    const themes: Theme[] = ['cursor', 'linear', 'kraken']
    const currentIndex = themes.indexOf(currentTheme.value)
    const nextIndex = (currentIndex + 1) % themes.length
    setTheme(themes[nextIndex])
  }

  /**
   * 获取主题变量 / Get theme CSS variable
   */
  const getCssVar = (name: string): string => {
    return getComputedStyle(document.documentElement)
      .getPropertyValue(`--color-${name}`)
      .trim()
  }

  return {
    theme,
    themeConfig,
    isDark,
    themes: THEMES,
    setTheme,
    toggleTheme,
    getCssVar
  }
}

export default useTheme
