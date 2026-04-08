import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

// Import styles - 高对比度主题系统
import 'element-plus/dist/index.css'
import './style.css'
import './styles/high-contrast-theme.css'
// 移除冲突的主题文件
// import './styles/professional-theme.css'
// import './styles/design-system.css'
import './styles/global-fix.css' // 全局紧急修复

const app = createApp(App)

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
