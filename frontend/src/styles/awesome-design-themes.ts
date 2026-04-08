// 顶级精选9种主题 - 来自 awesome-design-md 的准确颜色提取
export interface DesignTheme {
  name: string
  label: string
  description: string
  isDark: boolean
  colors: {
    primary: string
    secondary: string
    accent: string
    warning: string
    success: string
    danger: string
    bgPrimary: string
    bgSecondary: string
    bgCard: string
    bgHover: string
    bgSidebar: string
    textPrimary: string
    textSecondary: string
    textMuted: string
    borderColor: string
    divider: string
  }
}

// 1. Linear - 深蓝专业 (来自 linear.app)
export const linearTheme: DesignTheme = {
  name: 'linear',
  label: 'Linear',
  description: '深蓝专业，极致简约',
  isDark: true,
  colors: {
    primary: '#5e6ad2',
    secondary: '#7170ff',
    accent: '#828fff',
    warning: '#f59e0b',
    success: '#27a644',
    danger: '#ef4444',
    bgPrimary: '#08090a',
    bgSecondary: '#0f1011',
    bgCard: '#191a1b',
    bgHover: '#28282c',
    bgSidebar: '#08090a',
    textPrimary: '#f7f8f8',
    textSecondary: '#d0d6e0',
    textMuted: '#8a8f98',
    borderColor: '#23252a',
    divider: '#34343a',
  }
}

// 2. Vercel - 浅色极简 (来自 vercel.com)
export const vercelTheme: DesignTheme = {
  name: 'vercel',
  label: 'Vercel',
  description: '纯白极简，现代商务',
  isDark: false,
  colors: {
    primary: '#0070f3',
    secondary: '#7928ca',
    accent: '#ff5b4f',
    warning: '#f5a623',
    success: '#0070f3',
    danger: '#ff0000',
    bgPrimary: '#ffffff',
    bgSecondary: '#fafafa',
    bgCard: '#ffffff',
    bgHover: '#f5f5f5',
    bgSidebar: '#fafafa',
    textPrimary: '#171717',
    textSecondary: '#4d4d4d',
    textMuted: '#666666',
    borderColor: '#ebebeb',
    divider: '#f0f0f0',
  }
}

// 3. Supabase - 绿宝石 (来自 supabase.com)
export const supabaseTheme: DesignTheme = {
  name: 'supabase',
  label: 'Supabase',
  description: '深黑绿宝石，开发者最爱',
  isDark: true,
  colors: {
    primary: '#3ecf8e',
    secondary: '#00c573',
    accent: '#3ecf8e',
    warning: '#f59e0b',
    success: '#3ecf8e',
    danger: '#ef4444',
    bgPrimary: '#0f0f0f',
    bgSecondary: '#171717',
    bgCard: '#141414',
    bgHover: '#2e2e2e',
    bgSidebar: '#0f0f0f',
    textPrimary: '#fafafa',
    textSecondary: '#b4b4b4',
    textMuted: '#898989',
    borderColor: '#2e2e2e',
    divider: '#242424',
  }
}

// 4. Raycast - 纯黑现代 (来自 raycast.com)
export const raycastTheme: DesignTheme = {
  name: 'raycast',
  label: 'Raycast',
  description: '纯黑底色，多彩强调',
  isDark: true,
  colors: {
    primary: '#ff6363',
    secondary: '#55b3ff',
    accent: '#ffbc33',
    warning: '#ffbc33',
    success: '#5fc992',
    danger: '#ff6363',
    bgPrimary: '#040506',
    bgSecondary: '#0c0d0e',
    bgCard: '#151617',
    bgHover: '#1e1f21',
    bgSidebar: '#040506',
    textPrimary: '#f4f4f6',
    textSecondary: '#c8c8ca',
    textMuted: '#8e8e90',
    borderColor: '#1e1f21',
    divider: '#262728',
  }
}

// 5. Apple - 纯黑玻璃 (来自 apple.com)
export const appleTheme: DesignTheme = {
  name: 'apple',
  label: 'Apple',
  description: '苹果纯黑，蓝色强调',
  isDark: true,
  colors: {
    primary: '#2997ff',
    secondary: '#2997ff',
    accent: '#2997ff',
    warning: '#ff9f0a',
    success: '#30d158',
    danger: '#ff453a',
    bgPrimary: '#000000',
    bgSecondary: '#1d1d1f',
    bgCard: '#1d1d1f',
    bgHover: '#272729',
    bgSidebar: '#000000',
    textPrimary: '#f5f5f7',
    textSecondary: '#a0a0a0',
    textMuted: '#6e6e73',
    borderColor: '#2a2a2c',
    divider: '#1d1d1f',
  }
}

// 6. Spotify - 暗黑绿 (来自 spotify.com)
export const spotifyTheme: DesignTheme = {
  name: 'spotify',
  label: 'Spotify',
  description: '暗黑音乐风，绿色强调',
  isDark: true,
  colors: {
    primary: '#1ed760',
    secondary: '#1ed760',
    accent: '#1ed760',
    warning: '#ffa42b',
    success: '#1ed760',
    danger: '#f3727f',
    bgPrimary: '#0a0a0a',
    bgSecondary: '#111111',
    bgCard: '#252525',
    bgHover: '#1f1f1f',
    bgSidebar: '#0a0a0a',
    textPrimary: '#ffffff',
    textSecondary: '#b3b3b3',
    textMuted: '#7c7c7c',
    borderColor: '#4d4d4d',
    divider: '#2a2a2a',
  }
}

// 7. Stripe - 紫蓝商务 (来自 stripe.com)
export const stripeTheme: DesignTheme = {
  name: 'stripe',
  label: 'Stripe',
  description: '紫蓝渐变，商务专业',
  isDark: true,
  colors: {
    primary: '#665efd',
    secondary: '#7a73ff',
    accent: '#b9b9f9',
    warning: '#d4a04a',
    success: '#15be53',
    danger: '#ea2261',
    bgPrimary: '#0e0f2e',
    bgSecondary: '#151632',
    bgCard: '#1c1e42',
    bgHover: '#25284d',
    bgSidebar: '#0e0f2e',
    textPrimary: '#e8ecf0',
    textSecondary: '#c8d0da',
    textMuted: '#8a95a8',
    borderColor: 'rgba(255,255,255,0.1)',
    divider: 'rgba(255,255,255,0.1)',
  }
}

// 8. Notion - 温暖深色 (来自 notion.so)
export const notionTheme: DesignTheme = {
  name: 'notion',
  label: 'Notion',
  description: '温暖灰调，舒适阅读',
  isDark: true,
  colors: {
    primary: '#4da3f0',
    secondary: '#5aacf5',
    accent: '#3dbdb9',
    warning: '#f07020',
    success: '#2fca52',
    danger: '#f07020',
    bgPrimary: '#191919',
    bgSecondary: '#1e1e1e',
    bgCard: '#252525',
    bgHover: '#2d2d2d',
    bgSidebar: '#191919',
    textPrimary: 'rgba(255,255,255,0.92)',
    textSecondary: '#d4d3d1',
    textMuted: '#a8a5a0',
    borderColor: 'rgba(255,255,255,0.1)',
    divider: 'rgba(255,255,255,0.1)',
  }
}

// 9. Cursor - 暖橙复古 (来自 cursor.sh)
export const cursorTheme: DesignTheme = {
  name: 'cursor',
  label: 'Cursor',
  description: '暖橙复古，代码编辑器风',
  isDark: true,
  colors: {
    primary: '#f54e00',
    secondary: '#d9a04a',
    accent: '#f54e00',
    warning: '#d9a04a',
    success: '#2fba8a',
    danger: '#e04a6f',
    bgPrimary: '#1a1915',
    bgSecondary: '#1e1d17',
    bgCard: '#2a2922',
    bgHover: '#33322a',
    bgSidebar: '#1a1915',
    textPrimary: '#e6e5e0',
    textSecondary: 'rgba(230, 229, 224, 0.55)',
    textMuted: 'rgba(230, 229, 224, 0.35)',
    borderColor: 'rgba(230, 229, 224, 0.1)',
    divider: 'rgba(230, 229, 224, 0.1)',
  }
}

// 所有可用主题（按视觉差异排序）
export const awesomeDesignThemes: DesignTheme[] = [
  linearTheme,      // 深蓝专业
  vercelTheme,      // 浅色极简
  supabaseTheme,    // 绿宝石
  raycastTheme,     // 多彩黑
  appleTheme,       // 纯黑蓝
  spotifyTheme,     // 暗黑绿
  stripeTheme,      // 紫蓝商务
  notionTheme,      // 温暖灰
  cursorTheme,      // 暖橙复古
]

// 应用主题到文档
export function applyAwesomeDesignTheme(theme: DesignTheme) {
  const root = document.documentElement

  // 设置 CSS 变量
  root.style.setProperty('--color-primary', theme.colors.primary)
  root.style.setProperty('--color-secondary', theme.colors.secondary)
  root.style.setProperty('--color-accent', theme.colors.accent)
  root.style.setProperty('--color-warning', theme.colors.warning)
  root.style.setProperty('--color-success', theme.colors.success)
  root.style.setProperty('--color-danger', theme.colors.danger)

  root.style.setProperty('--bg-primary', theme.colors.bgPrimary)
  root.style.setProperty('--bg-secondary', theme.colors.bgSecondary)
  root.style.setProperty('--bg-card', theme.colors.bgCard)
  root.style.setProperty('--bg-hover', theme.colors.bgHover)
  root.style.setProperty('--bg-sidebar', theme.colors.bgSidebar)

  root.style.setProperty('--text-primary', theme.colors.textPrimary)
  root.style.setProperty('--text-secondary', theme.colors.textSecondary)
  root.style.setProperty('--text-muted', theme.colors.textMuted)

  root.style.setProperty('--border-color', theme.colors.borderColor)
  root.style.setProperty('--divider', theme.colors.divider)

  // 设置主题属性
  root.setAttribute('data-theme', theme.name)
  root.setAttribute('data-theme-dark', String(theme.isDark))

  // 保存到 localStorage
  localStorage.setItem('app-theme', theme.name)
}

// 加载保存的主题
export function loadSavedAwesomeTheme(): DesignTheme {
  const savedThemeName = localStorage.getItem('app-theme')
  if (savedThemeName) {
    const theme = awesomeDesignThemes.find(t => t.name === savedThemeName)
    if (theme) {
      applyAwesomeDesignTheme(theme)
      return theme
    }
  }
  applyAwesomeDesignTheme(linearTheme)
  return linearTheme
}
