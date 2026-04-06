# 龙泉驿环卫智能体 - AI编程验证项目

**目标**：7天验证AI编程能力边界，构建可运行的智慧环卫POC系统

**方式**：1人 + Claude Code，99%代码AI生成

---

## 项目结构

```
lqy-system/
├── START.md                    # ⭐ 启动入口，Claude读取后开始执行
├── ARCHITECTURE_CONTRACT.md    # 架构契约（技术规范，不可变）
├── SEMI_AUTO_GUIDE.md         # 半自动化执行指南
├── POC_Sprint_Plan.md         # 完整7天计划
├── prompts/                   # 每日Prompt文件
│   ├── day1/                 # Day 1: 后端骨架
│   │   ├── 00_check_env.md
│   │   ├── 01_project_structure.md
│   │   ├── 02_models.md
│   │   ├── 03_api_and_tests.md
│   │   ├── 04_docker_and_tools.md
│   │   └── 05_final_validation.md
│   └── MASTER_CONTROLLER.md  # 主控脚本（备用）
├── ProjectInformation/       # 项目原始需求文档
└── backend/                  # 代码生成目录（Day 1后创建）
```

---

## 快速开始

### 环境要求

- Python 3.10+
- Docker & Docker Compose
- Git
- Claude Code (已配置)

### 启动方式

```bash
# 1. 进入项目目录
cd lqy-system

# 2. 启动Claude Code
claude

# 3. 在Claude中输入（只需这一句）：
请读取 START.md 并开始执行
```

Claude会自动完成：
- 环境检查
- 读取架构契约
- 询问从哪天开始
- 按步骤执行开发

---

## 工作流程

### 每日流程（4小时有效工作）

```
09:00  启动Claude，输入启动指令
09:30  Claude自动读取任务，生成代码
11:30  你审查代码，执行验证脚本
12:00  午休
13:30  Claude修复或继续下阶段
15:30  最终验证，Git提交
16:30  结束，可选/clear清理上下文
```

### 关键介入点

每完成一个Step，Claude会暂停等你决策：
- `"继续"` - 执行下一步
- `"检查"` - 查看当前进度
- `"重做"` - 重新执行当前步骤
- `"回退"` - 回到上一步
- `"结束"` - 保存进度，明天继续

---

## 7天计划概览

| 天数 | 目标 | 核心交付 |
|------|------|----------|
| Day 1 | 后端骨架 | FastAPI + 模型 + API + 测试 |
| Day 2 | 数据流 | MQTT + WebSocket + 设备模拟器 |
| Day 3 | 告警引擎 | 异常检测 + 告警生成 |
| Day 4 | 前端看板 | Vue3 + ECharts 实时图表 |
| Day 5 | 预测算法 | 趋势预测 + 提前预警 |
| Day 6 | 3D展示 | Three.js 简单可视化 |
| Day 7 | 集成文档 | 完整演示 + 验证报告 |

---

## 关键文件说明

### START.md
**唯一入口**。Claude读取后自动执行所有步骤。包含：
- 环境检查协议
- 架构契约加载
- 分步骤执行流程
- 上下文压缩机制
- 用户快捷指令

### ARCHITECTURE_CONTRACT.md
**技术规范**。所有代码必须遵循：
- 技术栈（FastAPI/SQLModel/PostgreSQL）
- API响应格式
- 数据库规范
- 错误代码表
- 代码风格

### prompts/day1/
**详细Prompt**。Claude按需读取，生成具体代码。

---

## 状态追踪

当前进度会记录在 `progress.json`：

```json
{
  "current_day": 1,
  "current_step": 0,
  "status": "not_started",
  "tech_debt": []
}
```

Git标签标记里程碑：
- `day1-complete`
- `day2-complete`
- ...

---

## 克隆后设置

如果你从GitHub克隆此项目，请参考：
**[CLONE_GUIDE.md](./CLONE_GUIDE.md)**

---

## 注意事项

1. **不要直接修改Prompt文件** - 它们是Claude的执行指令
2. **每Step完成后必须验证** - 运行测试脚本，检查Git状态
3. **及时提交Git** - 每个Step完成后提交，方便回退
4. **监控上下文长度** - Claude提示"[上下文压缩]"时确认状态
5. **保持专注** - 4小时高质量工作 > 8小时低效工作

---

## 许可证

内部项目，仅供学习交流。

---

**开始**：`请读取 START.md 并开始执行`
