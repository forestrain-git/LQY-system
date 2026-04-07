# 15小时AI编程极限冲刺计划

## 项目信息
- **项目名称**: 龙泉驿环卫智能体
- **冲刺目标**: 15小时内完成预测算法、调度系统、工单系统、设备管理、安全管控、AI Agent
- **当前状态**: 准备启动
- **环境就绪**: ✅ Python/Node/Docker/Playwright

---

## 核心要求

1. ✅ **前端框架丰满** - 6大模块完整页面
2. ✅ **审美在线** - 3套主题(Cursor/Linear/Kraken) + 下拉切换
3. ✅ **大模型先用Kimi** - 预留本地模型切换
4. ✅ **子Agent审查** - 每个阶段结束审查
5. ✅ **前3周期后暂停** - Hour 6等用户确认
6. ✅ **详细代码注释** - 中英文双语
7. ✅ **Mock模拟真实** - 4个硬件模拟器
8. ✅ **技术债务清单** - 每个阶段记录

---

## 15小时详细时间表

| 阶段 | 时间 | 内容 | 检查点 |
|------|------|------|--------|
| 1 | Hour 0-2 | 预测算法 + 架构重构 + Mock系统 | 子Agent审查 |
| 2 | Hour 2-4 | 核心数据模型扩展 + Mock数据 | 子Agent审查 |
| 3 | Hour 4-6 | 智慧调度 + 设计系统 + 硬件模拟 | ⏸️ 用户确认 |
| 4 | Hour 6-8 | 工单系统 + 前端页面框架 | 子Agent审查 |
| 5 | Hour 8-10 | 设备管理 + 预测展示 + AI助手 | 子Agent审查 |
| 6 | Hour 10-12 | 安全管控 + AI Agent + Kimi集成 | 子Agent审查 |
| 7 | Hour 12-14 | 前端看板 + 3套主题完整实现 | 子Agent审查 |
| 8 | Hour 14-15 | 集成测试 + 文档 + 技术债务清单 | 最终交付 |

---

## 设计系统方案

### 主题列表
1. **Cursor** - 暖色调，#f2f1ed背景，#26251e文字
2. **Linear** - 暗色调，#08090a背景，#f7f8f8文字
3. **Kraken** - 亮色调，#ffffff背景，#7132f5强调

### 主题切换方式
- 顶部导航栏下拉菜单
- 自动持久化到localStorage
- CSS变量系统切换

---

## 硬件模拟系统

```
mocks/
├── device_simulator.py       # 设备传感器数据
├── badge_simulator.py        # 人员工牌定位
├── fence_simulator.py        # 电子围栏事件
├── vehicle_gps_simulator.py  # 车辆GPS轨迹
└── weighbridge_simulator.py  # 地磅称重数据
```

### 模拟数据规格
- **电子围栏**: 10-30cm精度，进出事件，SOS报警，异常行为
- **人员工牌**: 实时定位，静置监测，跌倒/滞留检测
- **车辆GPS**: 实时位置，行驶轨迹，速度，进/出站
- **地磅称重**: 车辆重量，垃圾品类，时间戳

---

## AI架构设计

```
┌─────────────────────────────────────────────┐
│              AI Service Interface           │
├─────────────────────────────────────────────┤
│  ┌──────────────┐      ┌──────────────┐    │
│  │  Kimi API    │◄────►│  本地LLM     │    │
│  │  (当前使用)   │      │  (未来切换)   │    │
│  └──────────────┘      └──────────────┘    │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  Agent System                               │
│  ├── 总控Agent (Master Agent)               │
│  ├── 调度Agent (Dispatch Agent)             │
│  └── 助手Agent (Chat Agent)                 │
└─────────────────────────────────────────────┘
```

---

## 代码注释规范

```python
# 示例：中英文双语注释
class BerthAllocator:
    """
    泊位分配器 / Berth Allocation Allocator
    
    根据车辆类型、泊位状态、排队情况，智能分配最优泊位
    Allocates optimal berth based on vehicle type, berth status, and queue
    
    分配策略 / Allocation Strategy:
    1. 品类匹配：生活垃圾→生活泊位，厨余→厨余泊位
    2. 距离最短：选择距离入口最近的可用泊位
    3. 负载均衡：避免单个泊位过度使用
    
    Args:
        vehicle_type: 车辆垃圾类型 / Vehicle waste type
        available_berths: 可用泊位列表 / List of available berths
        
    Returns:
        Berth: 分配的泊位对象 / Allocated berth object
    """
```

---

## 子Agent审查机制

每个阶段结束时召唤子Agent：
1. 代码质量审查
2. 架构合理性审查
3. Mock数据合理性审查
4. UI/UX审查
5. 根据审查结果调优

---

## 技术债务记录模板

```markdown
## Hour X 技术债务

| 债务项 | 原因 | 优先级 | 建议解决时间 |
|--------|------|--------|--------------|
| 调度算法简化 | 使用规则代替多目标优化 | 中 | Sprint 2 |
| 文件存储本地 | 未接入OSS | 低 | 部署前 |
| AI上下文5轮 | 性能考虑 | 低 | 有用户反馈后 |
```

---

## 上下文管理策略

### 每小时执行
- 清理大输出文件
- 只保留关键截图
- 代码只展示关键片段

### 每3小时执行
- `/clear` 清理旧输出
- 重新加载进度文件

### 应急方案
- 上下文>90%时保存Git commit
- 必要时启动新会话恢复

---

## 中断恢复指南

### 如果任务中断

1. **检查当前进度**
   ```bash
   cat sprint_status.json
   git log --oneline -5
   ```

2. **恢复环境**
   ```bash
   cd /home/forestrain/WSL-Projects/LQY-system
   source venv/bin/activate
   docker compose ps
   ```

3. **读取计划**
   ```bash
   cat Sprint_15h_Plan.md
   cat Sprint_Current_Status.md
   ```

4. **继续执行**
   - 找到当前阶段
   - 从该阶段任务描述开始
   - 召唤子Agent审查上一阶段（如需要）

---

## 文件清单

| 文件 | 用途 |
|------|------|
| `Sprint_15h_Plan.md` | 本计划文件 |
| `Sprint_Current_Status.md` | 实时进度追踪 |
| `Sprint_Tech_Debt.md` | 技术债务清单 |
| `progress.json` | 结构化进度数据 |

---

## 启动命令

```bash
# 后端
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm run dev

# 测试
python -m pytest tests/ -v
```

---

**计划创建时间**: 2026-04-07
**最后更新**: 准备启动
**状态**: 就绪
