<template>
  <div class="settings-view">
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-subtitle">配置系统参数和个性化选项</p>
    </div>

    <div class="settings-grid">
      <!-- 主题设置 -->
      <div class="settings-card">
        <div class="card-header">
          <Palette class="card-icon" />
          <h3>外观设置</h3>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">深色模式</div>
            <div class="setting-desc">切换系统深色/浅色主题</div>
          </div>
          <div class="toggle-switch active">已开启</div>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">紧凑模式</div>
            <div class="setting-desc">减小间距显示更多内容</div>
          </div>
          <div class="toggle-switch">已关闭</div>
        </div>
      </div>

      <!-- 通知设置 -->
      <div class="settings-card">
        <div class="card-header">
          <Bell class="card-icon" />
          <h3>通知设置</h3>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">告警通知</div>
            <div class="setting-desc">设备故障和安全告警</div>
          </div>
          <div class="toggle-switch active">已开启</div>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">工单提醒</div>
            <div class="setting-desc">新工单和超时提醒</div>
          </div>
          <div class="toggle-switch active">已开启</div>
        </div>
        
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">日报推送</div>
            <div class="setting-desc">每日运营数据汇总</div>
          </div>
          <div class="toggle-switch">已关闭</div>
        </div>
      </div>

      <!-- 数据设置 -->
      <div class="settings-card wide">
        <div class="card-header">
          <Database class="card-icon" />
          <h3>数据管理</h3>
        </div>
        
        <div class="data-stats">
          <div class="data-stat-item">
            <div class="data-stat-icon">💾</div>
            <div class="data-stat-info">
              <div class="data-stat-value">2.4 GB</div>
              <div class="data-stat-label">数据库大小</div>
            </div>
          </div>
          
          <div class="data-stat-item">
            <div class="data-stat-icon">📊</div>
            <div class="data-stat-info">
              <div class="data-stat-value">156万</div>
              <div class="data-stat-label">数据记录</div>
            </div>
          </div>
          
          <div class="data-stat-item">
            <div class="data-stat-icon">📅</div>
            <div class="data-stat-info">
              <div class="data-stat-value">90天</div>
              <div class="data-stat-label">数据保留</div>
            </div>
          </div>
        </div>
        
        <div class="data-actions">
          <button class="btn-secondary">📥 导出数据</button>
          <button class="btn-secondary">🗄️ 备份管理</button>
          <button class="btn-danger">🗑️ 清理缓存</button>
        </div>
      </div>

      <!-- 系统信息 -->
      <div class="settings-card">
        <div class="card-header">
          <Info class="card-icon" />
          <h3>系统信息</h3>
        </div>
        
        <div class="info-list">
          <div class="info-item">
            <span class="info-label">系统版本</span>
            <span class="info-value">v1.0.1</span>
          </div>
          <div class="info-item">
            <span class="info-label">最后更新</span>
            <span class="info-value">2026-04-08</span>
          </div>
          <div class="info-item">
            <span class="info-label">运行状态</span>
            <span class="info-value status-good">正常运行</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Palette, Bell, Database, Info } from 'lucide-vue-next'
</script>

<style scoped>
/* 高对比度强制样式 */
.settings-view {
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

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.settings-card {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
  border: 1px solid rgba(148, 163, 184, 0.2) !important;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
}

.settings-card.wide {
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
  color: #3b82f6;
}

.card-header h3 {
  font-size: 18px;
  color: #f8fafc !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.setting-name {
  font-size: 15px;
  font-weight: 600;
  color: #f8fafc !important;
  margin-bottom: 4px;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.setting-desc {
  font-size: 13px;
  color: #64748b !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.toggle-switch {
  padding: 6px 14px;
  background: rgba(148, 163, 184, 0.2) !important;
  color: #94a3b8 !important;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.toggle-switch.active {
  background: rgba(34, 197, 94, 0.2) !important;
  color: #22c55e !important;
}

.data-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.data-stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(15, 23, 42, 0.4) !important;
  border-radius: 10px;
}

.data-stat-icon {
  font-size: 28px;
}

.data-stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #f8fafc !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.data-stat-label {
  font-size: 13px;
  color: #94a3b8 !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.data-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-secondary {
  background: rgba(148, 163, 184, 0.2) !important;
  color: #e2e8f0 !important;
  border: 1px solid rgba(148, 163, 184, 0.3) !important;
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.btn-danger {
  background: rgba(239, 68, 68, 0.2) !important;
  color: #fca5a5 !important;
  border: 1px solid rgba(239, 68, 68, 0.3) !important;
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.info-label {
  font-size: 14px;
  color: #94a3b8 !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc !important;
  font-family: 'Microsoft YaHei', sans-serif !important;
}

.status-good {
  color: #22c55e !important;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  .settings-card.wide {
    grid-column: span 1;
  }
  .data-stats {
    grid-template-columns: 1fr;
  }
}
</style>
