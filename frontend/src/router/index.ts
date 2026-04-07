import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import DeviceList from '@/views/devices/DeviceList.vue'
import AlertList from '@/views/alerts/AlertList.vue'
import Test from '@/views/Test.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Dashboard, name: 'Dashboard' },
    { path: '/devices', component: DeviceList, name: 'DeviceList' },
    { path: '/alerts', component: AlertList, name: 'AlertList' },
    { path: '/test', component: Test, name: 'Test' },
  ],
})

export default router
