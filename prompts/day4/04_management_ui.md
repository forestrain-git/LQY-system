# Day 4 - Prompt 4: 告警管理与设备管理界面

**时机**：WebSocket集成完成后执行
**预期耗时**：Claude生成25分钟，你Review 15分钟
**人工决策**：确认管理功能完整，操作流畅

---

## 输入Prompt

```text
请实现告警管理和设备管理的完整界面。

【告警管理列表页】（src/views/alerts/AlertList.vue）

功能完整的告警管理界面：

1. 搜索筛选栏
   - 时间范围选择（今天/最近7天/最近30天/自定义）
   - 告警级别下拉（Critical/Warning/Info，可多选）
   - 告警状态下拉（Active/Acknowledged/Resolved，可多选）
   - 告警指标下拉（Temperature/Vibration/Current）
   - 设备选择器（下拉选择特定设备）
   - 搜索按钮 + 重置按钮

2. 操作按钮栏
   - 批量确认按钮（选中时启用）
   - 批量解决按钮（选中时启用）
   - 刷新按钮（带旋转动画）
   - 导出按钮（导出CSV）

3. 告警表格
   - 列定义：
     * 复选框（批量操作）
     * 时间（格式：YYYY-MM-DD HH:mm:ss）
     * 设备名称（可点击跳转设备详情）
     * 告警指标（带图标：温度🔥/振动📳/电流⚡）
     * 告警级别（Tag显示，Supabase+Raycast配色）：
       - Critical：背景rgba(255, 121, 198, 0.15)，文字#FF79C6（Raycast粉）
       - Warning：背景rgba(255, 184, 108, 0.15)，文字#FFB86C（Raycast橙）
       - Info：背景rgba(139, 233, 253, 0.15)，文字#8BE9FD（Raycast青）
     * 告警内容（截断显示，hover显示完整，颜色#F8F8F2）
     * 状态（Tag显示，深色主题）：
       - Active：背景rgba(255, 121, 198, 0.15)，文字#FF79C6
       - Acknowledged：背景rgba(255, 184, 108, 0.15)，文字#FFB86C
       - Resolved：背景rgba(62, 207, 142, 0.15)，文字#3ECF8E（Supabase绿）
     * 持续时间（从创建到现在/已解决显示总时长）
     * 操作按钮（确认/解决/详情）

4. 分页器
   - 每页条数选择（10/20/50）
   - 分页导航
   - 总条数显示

5. 告警详情弹窗
   - 点击详情按钮弹出Drawer
   - 显示完整告警信息
   - 显示设备基本信息
   - 显示该设备最近24小时的相关指标曲线
   - 操作按钮（确认/解决）

表格列宽分配：
- 时间：160px
- 设备：120px
- 指标：100px
- 级别：100px
- 内容：200px（自适应）
- 状态：100px
- 持续：120px
- 操作：150px

【告警规则管理】（src/views/alerts/AlertRules.vue）

告警规则配置界面：

1. 规则列表
   - 列：ID、适用设备、指标、条件、阈值、持续时间、状态、操作
   - 条件显示："温度 > 80℃"
   - 状态开关：启用/禁用
   - 操作：编辑、删除

2. 新建规则按钮
   - 弹出Dialog表单
   - 字段：
     * 设备选择（下拉，留空表示所有设备）
     * 指标选择（温度/振动/电流）
     * 操作符（>/< /=）
     * 阈值（数字输入）
     * 持续时间（秒，0表示立即）
     * 描述（文本框）

3. 编辑规则
   - 同新建，预填充数据

4. 删除确认
   - Element Plus MessageBox确认
   - 确认后删除，刷新列表

【设备管理列表页】（src/views/devices/DeviceList.vue）

设备管理界面：

1. 搜索筛选栏
   - 设备名称搜索（模糊搜索）
   - 设备类型下拉（Compressor/Pump/Fan/Conveyor/Other）
   - 设备状态下拉（Online/Offline/Maintenance/Disabled）
   - 搜索按钮 + 重置按钮

2. 操作按钮
   - 新增设备按钮
   - 刷新按钮
   - 导出设备列表

3. 设备卡片网格（每行4个卡片）
   - 卡片内容：
     * 设备名称（大字号）
     * 设备类型（图标+文字）
     * 状态标签（Supabase+Raycast配色）：
       - Online：背景rgba(62, 207, 142, 0.15)，文字#3ECF8E（Supabase绿）
       - Offline：背景rgba(255, 121, 198, 0.15)，文字#FF79C6（Raycast粉）
       - Maintenance：背景rgba(255, 184, 108, 0.15)，文字#FFB86C（Raycast橙）
       - Disabled：背景rgba(98, 114, 164, 0.15)，文字#6272A4（Raycast灰蓝）
     * 位置信息
     * 最新数据（温度/振动/电流，没有显示"无数据"）
     * 更新时间（几分钟前）
   - 操作按钮：查看详情、编辑、删除

4. 分页器（同告警列表）

【设备详情页】（src/views/devices/DeviceDetail.vue）

设备详情界面：

1. 页面头部
   - 返回按钮
   - 设备名称
   - 编辑按钮
   - 删除按钮

2. 设备基本信息卡片
   - ID、名称、类型、位置、状态、创建时间
   - 状态可切换（Online/Offline/Maintenance）

3. 实时数据面板
   - 大字号显示当前温度、振动、电流
   - 与上次数据比较（上升/下降箭头+数值）
   - 最后更新时间

4. 历史数据图表
   - 时间范围选择（最近1小时/6小时/24小时/7天）
   - 三线图表（温度、振动、电流）
   - 支持缩放（dataZoom）
   - 支持下载图表

5. 告警历史表格
   - 该设备的所有告警
   - 最近20条
   - 可跳转告警详情

6. 数据统计卡片
   - 今日数据条数
   - 平均温度/振动/电流
   - 最高温度记录

【新增/编辑设备弹窗】（src/components/devices/DeviceFormDialog.vue）

表单字段：
- 设备名称（必填，校验唯一性）
- 设备类型（下拉选择）
- 安装位置（文本）
- 初始状态（默认Offline）

提交后：
- 成功：提示"创建成功"，刷新列表
- 失败：显示错误信息

【API集成】

更新API文件：

src/api/alerts.ts:
```typescript
export const alertApi = {
  getAlerts: (params: AlertQueryParams) => axios.get('/api/v1/alerts', { params }),
  getAlertStats: () => axios.get('/api/v1/alerts/stats'),
  acknowledgeAlert: (id: number) => axios.post(`/api/v1/alerts/${id}/acknowledge`),
  resolveAlert: (id: number) => axios.post(`/api/v1/alerts/${id}/resolve`),
  batchAcknowledge: (ids: number[]) => axios.post('/api/v1/alerts/acknowledge-batch', { ids }),
  exportAlerts: (params: AlertQueryParams) => axios.get('/api/v1/alerts/export', { params, responseType: 'blob' }),
}
```

src/api/alert-rules.ts:
```typescript
export const alertRuleApi = {
  getRules: () => axios.get('/api/v1/alert-rules'),
  createRule: (data: AlertRuleCreate) => axios.post('/api/v1/alert-rules', data),
  updateRule: (id: number, data: AlertRuleUpdate) => axios.put(`/api/v1/alert-rules/${id}`, data),
  deleteRule: (id: number) => axios.delete(`/api/v1/alert-rules/${id}`),
}
```

src/api/devices.ts:
```typescript
export const deviceApi = {
  getDevices: (params: DeviceQueryParams) => axios.get('/api/v1/devices', { params }),
  getDevice: (id: number) => axios.get(`/api/v1/devices/${id}`),
  createDevice: (data: DeviceCreate) => axios.post('/api/v1/devices', data),
  updateDevice: (id: number, data: DeviceUpdate) => axios.put(`/api/v1/devices/${id}`, data),
  deleteDevice: (id: number) => axios.delete(`/api/v1/devices/${id}`),
  getDeviceStats: (id: number) => axios.get(`/api/v1/devices/${id}/stats`),
  getDeviceData: (id: number, params: DataQueryParams) => axios.get(`/api/v1/devices/${id}/data`, { params }),
}
```

【页面级状态管理】

创建页面store：

src/stores/alerts.ts:
```typescript
export const useAlertsStore = defineStore('alerts', () => {
  // State
  const alertList = ref<Alert[]>([])
  const pagination = ref({ page: 1, size: 20, total: 0 })
  const filters = ref({
    level: [] as string[],
    status: [] as string[],
    metric: [] as string[],
    deviceId: undefined as number | undefined,
    startTime: undefined as string | undefined,
    endTime: undefined as string | undefined,
  })
  const selectedAlerts = ref<number[]>([])
  const loading = ref(false)
  
  // Actions
  const fetchAlerts = async () => { }
  const acknowledgeSelected = async () => { }
  const resolveSelected = async () => { }
  const exportAlerts = async () => { }
  
  return {
    alertList,
    pagination,
    filters,
    selectedAlerts,
    loading,
    fetchAlerts,
    acknowledgeSelected,
    resolveSelected,
    exportAlerts,
  }
})
```

【样式统一】

搜索栏样式（深色主题）：
- 背景：#1C1C1C（Supabase灰）
- 边框：1px solid #252525
- 内边距：16px
- 圆角：8px
- 元素间距：12px

操作按钮栏：
- 底部边距：16px
- 按钮间距：8px

表格样式（Supabase+Raycast深色主题）：
- 表头背景：#1C1C1C（Supabase灰）
- 表头文字：#B0B0B0，粗体
- 表头底部边框：2px solid rgba(62, 207, 142, 0.3)（绿色微光）
- 表身背景：#0F0F0F（Raycast黑）
- 表身文字：#F8F8F2
- 行高：48px
- 行底部边框：1px solid #252525
- 悬停背景：#1C1C1C（Supabase灰）
- 选中行背景：#252525，左边框3px solid #BD93F9（Raycast紫）

【空状态处理】

无数据时显示：
- Element Plus Empty组件
- 提示文字："暂无数据"
- 操作建议按钮（如"立即添加"）

【加载状态】

- 表格加载：v-loading="loading"
- 按钮加载：:loading="submitting"
- 卡片加载：el-skeleton

【验证步骤】

1. 告警列表页：
   - 访问 /alerts
   - 验证筛选功能正常
   - 验证分页正常
   - 验证确认/解决操作
   - 验证批量操作
   - 验证导出功能

2. 告警规则页：
   - 访问 /alert-rules
   - 验证新建规则
   - 验证编辑规则
   - 验证删除规则
   - 验证启用/禁用开关

3. 设备列表页：
   - 访问 /devices
   - 验证搜索筛选
   - 验证新增设备
   - 验证编辑设备
   - 验证删除设备
   - 验证跳转详情

4. 设备详情页：
   - 点击设备进入详情
   - 验证实时数据显示
   - 验证历史图表
   - 验证告警历史
   - 验证状态切换
```

---

## 预期输出

```
生成文件：
- src/views/alerts/AlertList.vue [完成]
- src/views/alerts/AlertRules.vue [完成]
- src/views/devices/DeviceList.vue [完成]
- src/views/devices/DeviceDetail.vue [完成]
- src/components/alerts/AlertDetailDrawer.vue [完成]
- src/components/alerts/AlertRuleFormDialog.vue [完成]
- src/components/devices/DeviceCard.vue [完成]
- src/components/devices/DeviceFormDialog.vue [完成]
- src/components/devices/DeviceStatsPanel.vue [完成]
- src/stores/alerts.ts [完成]
- src/stores/devices.ts [更新]
- src/api/alerts.ts [完成]
- src/api/alert-rules.ts [完成]
- src/api/devices.ts [更新]

界面效果：
- /alerts：完整告警列表，支持筛选、分页、批量操作
- /alert-rules：规则管理表格，支持CRUD
- /devices：设备卡片网格，支持搜索筛选
- /devices/:id：设备详情，显示实时数据和历史图表
```

---

## 你的决策

- [ ] 管理功能完整 → 继续Prompt 5（验证打包）
- [ ] 需要调整布局 → 告诉Claude修改
- [ ] 缺少功能 → 补充需求

---

## 手工验证

```bash
cd frontend
npm run dev

# 测试告警管理
# 1. 访问 http://localhost:5173/alerts
# 2. 测试筛选器，观察表格数据变化
# 3. 选中告警，测试批量确认
# 4. 点击告警详情，查看Drawer

# 测试设备管理
# 1. 访问 http://localhost:5173/devices
# 2. 点击"新增设备"，填写表单提交
# 3. 点击设备卡片进入详情
# 4. 验证实时数据更新
# 5. 验证历史图表可正常显示
```
