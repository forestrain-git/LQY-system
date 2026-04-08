<!--
  登录页面 / Login Page

  提供用户认证功能
  Provides user authentication

  Author: AI Sprint
  Date: 2026-04-08
-->
<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-header">
        <div class="login-logo">
          <Trash2 class="logo-icon" />
        </div>
        <h1 class="login-title">龙泉驿环卫</h1>
        <p class="login-subtitle">智能管理系统</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <div class="input-wrapper">
            <User class="input-icon" />
            <input
              v-model="form.username"
              type="text"
              class="form-input"
              placeholder="请输入用户名"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="input-wrapper">
            <Lock class="input-icon" />
            <input
              v-model="form.password"
              type="password"
              class="form-input"
              placeholder="请输入密码"
              required
            />
          </div>
        </div>

        <div v-if="error" class="error-message">
          <AlertCircle class="error-icon" />
          {{ error }}
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          <RefreshCw v-if="loading" class="spinning" />
          <span v-else>登录</span>
        </button>
      </form>

      <div class="login-footer">
        <p class="hint-text">默认账号: admin / admin123</p>
        <p class="hint-text">operator / operator123</p>
        <p class="hint-text" style="margin-top: 8px; color: var(--color-primary-400);">💡 后端离线时可使用演示模式登录</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Trash2, User, Lock, AlertCircle, RefreshCw } from 'lucide-vue-next'
import apiClient from '@/api'

const router = useRouter()

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    // 尝试调用后端API
    const response = await apiClient.post('/api/v1/auth/login/json', {
      username: form.username,
      password: form.password
    })

    const data = response.data

    if (data.code === 0 && data.data) {
      // 保存token
      localStorage.setItem('auth-token', data.data.access_token)
      localStorage.setItem('user-info', JSON.stringify(data.data.user || { username: form.username }))

      ElMessage.success('登录成功')

      // 跳转到首页
      router.push('/')
    } else {
      error.value = data.message || '登录失败'
    }
  } catch (err: any) {
    // 网络错误时使用本地演示登录
    console.log('Backend unavailable, using demo mode')

    // 验证默认账号
    if ((form.username === 'admin' && form.password === 'admin123') ||
        (form.username === 'operator' && form.password === 'operator123')) {
      // 生成本地token
      const mockToken = 'demo-token-' + Date.now()
      const mockUser = {
        username: form.username,
        role: form.username === 'admin' ? 'admin' : 'operator',
        name: form.username === 'admin' ? '系统管理员' : '操作员'
      }

      localStorage.setItem('auth-token', mockToken)
      localStorage.setItem('user-info', JSON.stringify(mockUser))

      ElMessage.success('演示模式登录成功')
      router.push('/')
    } else {
      error.value = '用户名或密码错误（演示模式：admin/admin123）'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-secondary);
  background-image: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-bg-primary) 100%);
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: var(--space-8);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-xl);
  box-shadow: 0 20px 60px var(--shadow-color);
}

.login-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.login-logo {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-4);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-primary-50);
  border-radius: var(--radius-lg);
}

.logo-icon {
  width: 40px;
  height: 40px;
  color: var(--color-primary-600);
}

.login-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.login-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
}

.login-form {
  margin-bottom: var(--space-6);
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--color-text-tertiary);
}

.form-input {
  width: 100%;
  padding: var(--space-3) var(--space-3) var(--space-3) calc(var(--space-3) + 28px);
  font-size: var(--text-base);
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  background-color: var(--color-bg-primary);
}

.form-input::placeholder {
  color: var(--color-text-tertiary);
}

.error-message {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  margin-bottom: var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-accent-danger);
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-md);
}

.error-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.login-btn {
  width: 100%;
  padding: var(--space-4);
  font-size: var(--text-base);
  font-weight: 600;
  color: white;
  background-color: var(--color-primary-600);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.login-btn:hover:not(:disabled) {
  background-color: var(--color-primary-700);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.login-footer {
  text-align: center;
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border-secondary);
}

.hint-text {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin: 2px 0;
}
</style>