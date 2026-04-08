<template>
  <div class="profile-view">
    <div class="page-header">
      <h1 class="page-title">个人中心</h1>
      <p class="page-subtitle">管理您的个人信息和账户设置</p>
    </div>

    <div class="profile-grid">
      <!-- 个人信息卡片 -->
      <div class="profile-card">
        <div class="card-header">
          <User class="card-icon" />
          <h3>基本信息</h3>
        </div>
        
        <div class="form-group">
          <label>用户名</label>
          <input type="text" value="管理员" class="form-input" readonly>
        </div>
        
        <div class="form-group">
          <label>邮箱</label>
          <input type="email" value="admin@lqy.gov.cn" class="form-input" readonly>
        </div>
        
        <div class="form-group">
          <label>手机号</label>
          <input type="tel" value="138****8888" class="form-input" readonly>
        </div>
        
        <button class="btn-primary">编辑信息</button>
      </div>

      <!-- 账户统计卡片 -->
      <div class="profile-card">
        <div class="card-header">
          <Activity class="card-icon" />
          <h3>账户统计</h3>
        </div>
        
        <div class="stats-list">
          <div class="stat-row">
            <span class="stat-name">登录次数</span>
            <span class="stat-value">128次</span>
          </div>
          <div class="stat-row">
            <span class="stat-name">操作记录</span>
            <span class="stat-value">456条</span>
          </div>
          <div class="stat-row">
            <span class="stat-name">最后登录</span>
            <span class="stat-value">2026-04-08 14:30</span>
          </div>
          <div class="stat-row">
            <span class="stat-name">账户状态</span>
            <span class="stat-value status-active">正常</span>
          </div>
        </div>
      </div>

      <!-- 安全设置卡片 -->
      <div class="profile-card wide">
        <div class="card-header">
          <Shield class="card-icon" />
          <h3>安全设置</h3>
        </div>
        
        <div class="security-list">
          <div class="security-item">
            <div class="security-info">
              <div class="security-title">登录密码</div>
              <div class="security-desc">建议定期更换密码以保护账户安全</div>
            </div>
            <button class="btn-secondary">修改密码</button>
          </div>
          
          <div class="security-item">
            <div class="security-info">
              <div class="security-title">两步验证</div>
              <div class="security-desc">开启后登录时需要额外的验证码</div>
            </div>
            <div class="toggle-switch active">已开启</div>
          </div>
          
          <div class="security-item">
            <div class="security-info">
              <div class="security-title">登录通知</div>
              <div class="security-desc">新设备登录时发送通知</div>
            </div>
            <div class="toggle-switch active">已开启</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { User, Activity, Shield } from 'lucide-vue-next'
</script>

<style scoped>
/* 高对比度强制样式 */
.profile-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
  padding: 24px;
  color: #f8fafc;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #f8fafc !important;
  margin-bottom: 8px;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
}

.page-subtitle {
  font-size: 14px;
  color: #94a3b8 !important;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.profile-card {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
  border: 1px solid rgba(148, 163, 184, 0.2) !important;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
}

.profile-card.wide {
  grid-column: span 2;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.card-icon {
  width: 24px;
  height: 24px;
  color: #10b981;
}

.card-header h3 {
  font-size: 18px;
  color: #f8fafc !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #94a3b8 !important;
  margin-bottom: 6px;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.5) !important;
  border: 1px solid rgba(148, 163, 184, 0.2) !important;
  border-radius: 8px;
  color: #f8fafc !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.btn-primary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
  color: white !important;
  border: none !important;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.btn-secondary {
  background: rgba(148, 163, 184, 0.2) !important;
  color: #e2e8f0 !important;
  border: 1px solid rgba(148, 163, 184, 0.3) !important;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.stat-name {
  font-size: 14px;
  color: #94a3b8 !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.status-active {
  color: #22c55e !important;
}

.security-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(15, 23, 42, 0.3) !important;
  border-radius: 8px;
}

.security-title {
  font-size: 15px;
  font-weight: 600;
  color: #f8fafc !important;
  margin-bottom: 4px;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.security-desc {
  font-size: 13px;
  color: #64748b !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.toggle-switch {
  padding: 6px 12px;
  background: rgba(34, 197, 94, 0.2) !important;
  color: #22c55e !important;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  .profile-card.wide {
    grid-column: span 1;
  }
}
</style>
