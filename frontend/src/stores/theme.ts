import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  awesomeDesignThemes,
  linearTheme,
  applyAwesomeDesignTheme,
  loadSavedAwesomeTheme,
  type DesignTheme
} from '@/styles/awesome-design-themes'

export const useThemeStore = defineStore('theme', () => {
  // State
  const currentTheme = ref<DesignTheme>(linearTheme)
  const isThemeReady = ref(false)

  // Getters
  const availableThemes = computed(() => awesomeDesignThemes)
  const darkThemesList = computed(() => awesomeDesignThemes.filter((t: DesignTheme) => t.isDark))
  const lightThemesList = computed(() => awesomeDesignThemes.filter((t: DesignTheme) => !t.isDark))
  const themeColors = computed(() => currentTheme.value.colors)
  const isDark = computed(() => currentTheme.value.isDark)

  // Actions
  const initTheme = () => {
    const savedTheme = loadSavedAwesomeTheme()
    currentTheme.value = savedTheme
    isThemeReady.value = true
  }

  const setTheme = (themeName: string) => {
    const theme = awesomeDesignThemes.find(t => t.name === themeName)
    if (theme) {
      applyAwesomeDesignTheme(theme)
      currentTheme.value = theme
      return true
    }
    return false
  }

  const toggleTheme = () => {
    const currentIndex = awesomeDesignThemes.findIndex(t => t.name === currentTheme.value.name)
    const nextIndex = (currentIndex + 1) % awesomeDesignThemes.length
    const nextTheme = awesomeDesignThemes[nextIndex]
    setTheme(nextTheme.name)
    return nextTheme
  }

  return {
    // State
    currentTheme,
    isThemeReady,
    // Getters
    availableThemes,
    darkThemesList,
    lightThemesList,
    themeColors,
    isDark,
    // Actions
    initTheme,
    setTheme,
    toggleTheme
  }
})
