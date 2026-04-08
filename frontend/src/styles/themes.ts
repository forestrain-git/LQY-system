// 主题配置文件 - 龙泉驿环卫智能体设计系统
// Theme Configuration - LQY Sanitation Intelligence Design System

export interface Theme {
  name: string
  label: string
  description: string
  colors: {
    // 主色调 / Primary Colors
    primary: string
    primaryLight: string
    primaryDark: string
    secondary: string
    accent: string

    // 状态色 / Status Colors
    success: string
    warning: string
    danger: string
    info: string

    // 背景色 / Background Colors
    bgPrimary: string
    bgSecondary: string
    bgElevated: string
    bgCard: string
    bgHover: string

    // 文字色 / Text Colors
    textPrimary: string
    textSecondary: string
    textMuted: string
    textInverse: string

    // 边框 / Borders
    borderPrimary: string
    borderSecondary: string
    divider: string

    // 阴影 / Shadows
    shadowColor: string
  }

  // 字体 / Typography
  fontFamily: {
    sans: string
    mono: string
  }

  // 圆角 / Border Radius
  radius: {
    sm: string
    md: string
    lg: string
    xl: string
    full: string
  }

  // 间距 / Spacing
  space: {
    unit: number
  }
}

// ===========================================
// Cursor Theme (暖色调 / Warm Tone)
// 灵感: Cursor编辑器 - 温暖专业
// ===========================================
export const cursorTheme: Theme = {
  name: 'cursor',
  label: 'Cursor',
  description: '暖色调，适合长时间使用',
  colors: {
    primary: '#26251e',
    primaryLight: '#f2f1ed',
    primaryDark: '#1a1914',
    secondary: '#6b6b5e',
    accent: '#e4a11b',

    success: '#22c55e',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',

    bgPrimary: '#f2f1ed',
    bgSecondary: '#e8e6e1',
    bgElevated: '#ffffff',
    bgCard: '#ffffff',
    bgHover: '#e0ddd5',

    textPrimary: '#26251e',
    textSecondary: '#6b6b5e',
    textMuted: '#9c9b8e',
    textInverse: '#f2f1ed',

    borderPrimary: '#d4d1c8',
    borderSecondary: '#e0ddd5',
    divider: '#e8e6e1',

    shadowColor: 'rgba(38, 37, 30, 0.08)'
  },
  fontFamily: {
    sans: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif',
    mono: '"JetBrains Mono", "Fira Code", monospace'
  },
  radius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px'
  },
  space: {
    unit: 4
  }
}

// ===========================================
// Linear Theme (暗色调 / Dark Tone)
// 灵感: Linear应用 - 深色专业
// ===========================================
export const linearTheme: Theme = {
  name: 'linear',
  label: 'Linear',
  description: '暗色调，沉浸式体验',
  colors: {
    primary: '#5e6ad2',
    primaryLight: '#8b93e6',
    primaryDark: '#4f5bbf',
    secondary: '#8a8f98',
    accent: '#f4d03f',

    success: '#4ade80',
    warning: '#fbbf24',
    danger: '#f87171',
    info: '#60a5fa',

    bgPrimary: '#08090a',
    bgSecondary: '#0f1112',
    bgElevated: '#161b22',
    bgCard: '#1c2128',
    bgHover: '#21262d',

    textPrimary: '#f7f8f8',
    textSecondary: '#8a8f98',
    textMuted: '#5c6168',
    textInverse: '#08090a',

    borderPrimary: '#30363d',
    borderSecondary: '#21262d',
    divider: '#1c2128',

    shadowColor: 'rgba(0, 0, 0, 0.4)'
  },
  fontFamily: {
    sans: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    mono: '"JetBrains Mono", monospace'
  },
  radius: {
    sm: '6px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px'
  },
  space: {
    unit: 4
  }
}

// ===========================================
// Kraken Theme (亮色调 / Light Tone with Accent)
// 灵感: GitKraken - 紫色强调
// ===========================================
export const krakenTheme: Theme = {
  name: 'kraken',
  label: 'Kraken',
  description: '亮色调，紫色强调色',
  colors: {
    primary: '#7132f5',
    primaryLight: '#9c7bf8',
    primaryDark: '#5a1fd4',
    secondary: '#6e7681',
    accent: '#f778ba',

    success: '#3fb950',
    warning: '#d29922',
    danger: '#f85149',
    info: '#58a6ff',

    bgPrimary: '#ffffff',
    bgSecondary: '#f6f8fa',
    bgElevated: '#ffffff',
    bgCard: '#ffffff',
    bgHover: '#f3f4f6',

    textPrimary: '#24292f',
    textSecondary: '#57606a',
    textMuted: '#8c959f',
    textInverse: '#ffffff',

    borderPrimary: '#d0d7de',
    borderSecondary: '#e1e4e8',
    divider: '#e1e4e8',

    shadowColor: 'rgba(113, 50, 245, 0.12)'
  },
  fontFamily: {
    sans: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    mono: '"SF Mono", "Fira Code", monospace'
  },
  radius: {
    sm: '6px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px'
  },
  space: {
    unit: 4
  }
}

// ===========================================
// 所有可用主题
// ===========================================
export const availableThemes: Theme[] = [
  cursorTheme,
  linearTheme,
  krakenTheme
]

// 默认主题
export const defaultTheme = cursorTheme

// ===========================================
// 主题应用函数
// ===========================================

export function applyTheme(theme: Theme) {
  const root = document.documentElement
  const style = root.style

  // 设置CSS变量 / Set CSS Variables
  style.setProperty('--color-primary', theme.colors.primary)
  style.setProperty('--color-primary-light', theme.colors.primaryLight)
  style.setProperty('--color-primary-dark', theme.colors.primaryDark)
  style.setProperty('--color-secondary', theme.colors.secondary)
  style.setProperty('--color-accent', theme.colors.accent)

  style.setProperty('--color-accent-success', theme.colors.success)
  style.setProperty('--color-accent-warning', theme.colors.warning)
  style.setProperty('--color-accent-danger', theme.colors.danger)
  style.setProperty('--color-accent-info', theme.colors.info)

  style.setProperty('--color-bg-primary', theme.colors.bgPrimary)
  style.setProperty('--color-bg-secondary', theme.colors.bgSecondary)
  style.setProperty('--color-bg-elevated', theme.colors.bgElevated)
  style.setProperty('--color-bg-card', theme.colors.bgCard)
  style.setProperty('--color-bg-hover', theme.colors.bgHover)

  style.setProperty('--color-text-primary', theme.colors.textPrimary)
  style.setProperty('--color-text-secondary', theme.colors.textSecondary)
  style.setProperty('--color-text-muted', theme.colors.textMuted)
  style.setProperty('--color-text-inverse', theme.colors.textInverse)

  style.setProperty('--color-border-primary', theme.colors.borderPrimary)
  style.setProperty('--color-border-secondary', theme.colors.borderSecondary)
  style.setProperty('--color-divider', theme.colors.divider)

  style.setProperty('--shadow-color', theme.colors.shadowColor)

  // 字体 / Font Family
  style.setProperty('--font-sans', theme.fontFamily.sans)
  style.setProperty('--font-mono', theme.fontFamily.mono)

  // 圆角 / Border Radius
  style.setProperty('--radius-sm', theme.radius.sm)
  style.setProperty('--radius-md', theme.radius.md)
  style.setProperty('--radius-lg', theme.radius.lg)
  style.setProperty('--radius-xl', theme.radius.xl)
  style.setProperty('--radius-full', theme.radius.full)

  // 间距 / Spacing
  style.setProperty('--space-unit', theme.space.unit.toString())

  // 计算间距变量
  const unit = theme.space.unit
  for (let i = 1; i <= 12; i++) {
    style.setProperty(`--space-${i}`, `${i * unit * 0.25}rem`)
  }

  // 字体大小 / Font Sizes
  style.setProperty('--text-xs', '0.75rem')
  style.setProperty('--text-sm', '0.875rem')
  style.setProperty('--text-base', '1rem')
  style.setProperty('--text-lg', '1.125rem')
  style.setProperty('--text-xl', '1.25rem')
  style.setProperty('--text-2xl', '1.5rem')
  style.setProperty('--text-3xl', '1.875rem')
  style.setProperty('--text-4xl', '2.25rem')

  // 保存到localStorage
  localStorage.setItem('app-theme', theme.name)

  // 添加主题属性到body
  document.body.setAttribute('data-theme', theme.name)
}

// 加载保存的主题
export function loadSavedTheme(): Theme {
  if (typeof window === 'undefined') {
    return defaultTheme
  }

  const savedThemeName = localStorage.getItem('app-theme')
  if (savedThemeName) {
    const theme = availableThemes.find(t => t.name === savedThemeName)
    if (theme) {
      applyTheme(theme)
      return theme
    }
  }

  applyTheme(defaultTheme)
  return defaultTheme
}

// 通过名称获取主题
export function getThemeByName(name: string): Theme {
  return availableThemes.find(t => t.name === name) || defaultTheme
}
