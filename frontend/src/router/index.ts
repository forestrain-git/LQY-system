/**
 * 路由配置 / Router Configuration
 *
 * Author: AI Sprint
 * Date: 2026-04-07
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import Dashboard from '@/views/Dashboard.vue'
import DeviceList from '@/views/devices/DeviceList.vue'
import AlertList from '@/views/alerts/AlertList.vue'

// 路由配置 / Route configuration
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '总览看板' }
      },
      {
        path: '/dispatch',
        name: 'Dispatch',
        component: () => import('@/views/DispatchBoard.vue'),
        meta: { title: '智慧调度' }
      },
      {
        path: '/devices',
        name: 'DeviceList',
        component: DeviceList,
        meta: { title: '设备管理' }
      },
      {
        path: '/alerts',
        name: 'AlertList',
        component: AlertList,
        meta: { title: '告警管理' }
      },
      {
        path: '/workorders',
        name: 'WorkOrders',
        component: () => import('@/views/WorkOrderView.vue'),
        meta: { title: '工单管理' }
      },
      {
        path: '/safety',
        name: 'Safety',
        component: () => import('@/views/SafetyView.vue'),
        meta: { title: '安全管控' }
      },
      {
        path: '/ai-assistant',
        name: 'AIAssistant',
        component: () => import('@/views/AIAssistantView.vue'),
        meta: { title: 'AI助手' }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { title: '个人中心' }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/SettingsView.vue'),
        meta: { title: '系统设置' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '页面不存在' }
  }
]

// 创建路由实例 / Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 / Route guard
router.beforeEach((to, from, next) => {
  // 设置页面标题 / Set page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - 龙泉驿环卫智能体`
  }

  // 这里可以添加权限检查 / Can add auth check here
  next()
})

export default router
