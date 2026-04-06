# 龙泉驿环卫智能体 - 主控执行脚本

## 使用方式

1. 启动Claude Code：`claude`
2. 输入：`请读取 /mnt/d/projects/lqy-system/prompts/MASTER_CONTROLLER.md 并按指示执行`
3. 每阶段完成后，Claude会告诉你下一步，你只需说"继续"或"跳过"

---

## 当前阶段检查

**请先确认以下环境：**
- [ ] 当前目录是 `/mnt/d/projects/lqy-system` 或项目根目录
- [ ] Python 3.10+ 可用
- [ ] Docker 运行中（如有则更好）
- [ ] Git 已初始化

**如果以上都OK，回复"环境OK，开始Day 1"，然后执行第一阶段。**

---

## 阶段1：项目初始化（Day 1 - Step 1）

**目标**：创建backend目录结构，能`docker-compose up`启动

**执行步骤**：

1. 读取并执行：`prompts/day1/00_check_env.md`
2. 如果检查通过，读取并执行：`prompts/day1/01_project_structure.md`
3. 生成完成后，验证：
   ```bash
   cd backend && docker-compose config
   # 如果没有错误，说明配置语法正确
   ```
4. 执行：`pip install -r requirements.txt -q && python -c "from app.main import app; print('结构OK')"`

**阶段完成标准**：
- [ ] backend/目录结构完整
- [ ] requirements.txt可安装
- [ ] main.py能import

**完成后输出**：
- 文件树结构
- 阶段完成确认
- 下阶段指令

---

## 阶段2：模型生成（Day 1 - Step 2）

**前置条件**：阶段1完成，你说"继续"

**执行步骤**：

1. 读取并执行：`prompts/day1/02_models.md`
2. 生成完成后，验证：
   ```bash
   python test_models.py
   ```
3. 如果有错误，尝试修复，最多尝试3次
4. 如果3次都失败，输出错误摘要和建议，等待人工决策

**阶段完成标准**：
- [ ] test_models.py通过
- [ ] 所有模型能正常import
- [ ] 关系定义正确

---

## 阶段3：API实现（Day 1 - Step 3）

**前置条件**：阶段2完成，你说"继续"

**执行步骤**：

1. 读取并执行：`prompts/day1/03_api_and_tests.md`
2. 生成完成后，启动数据库：`docker-compose up -d postgres redis`
3. 等待5秒，运行测试：`pytest app/tests/ -v --tb=short`
4. 如果有失败测试，分析原因：
   - 如果是小错误（typo、import错误），自动修复
   - 如果是逻辑错误，输出失败测试和错误信息，等待人工决策

**阶段完成标准**：
- [ ] 13个测试全部通过（或80%以上通过）
- [ ] 覆盖率>80%

---

## 阶段4：Docker完善（Day 1 - Step 4）

**前置条件**：阶段3完成，你说"继续"

**执行步骤**：

1. 读取并执行：`prompts/day1/04_docker_and_tools.md`
2. 生成Makefile和工具脚本
3. 验证Docker构建：`make up` 或 `docker-compose up -d --build`
4. 等待30秒，运行诊断：`python diagnose.py`
5. 如果诊断失败，分析原因并尝试修复

**阶段完成标准**：
- [ ] `make up`能启动所有服务
- [ ] `python diagnose.py`全部通过
- [ ] `curl http://localhost:8000/health`返回200

---

## 阶段5：最终验证（Day 1 - Step 5）

**前置条件**：阶段4完成，你说"继续"

**执行步骤**：

1. 读取并执行：`prompts/day1/05_final_validation.md`
2. 执行端到端验证（curl命令）
3. 生成Day 1报告：`docs/day1_report.md`
4. Git提交并打标签

**阶段完成标准**：
- [ ] 所有curl命令返回预期结果
- [ ] Git提交成功
- [ ] 标签`day1-complete`创建

**完成后输出**：
```
Day 1 完成总结
===============
- 完成时间：XXX
- 代码行数：XXX
- 测试通过率：XX%
- Git提交：XXX

建议：
1. 休息，明天继续Day 2
2. 或继续Day 2（回复"继续Day 2"）
3. 或查看报告（docs/day1_report.md）
```

---

## 阶段6：Day 2 - 数据流

**前置条件**：你说"继续Day 2"

**任务**：MQTT + WebSocket + 设备模拟器

（详细步骤待Day 1完成后补充）

---

## 故障处理协议

### 自动修复策略
遇到以下问题，自动尝试修复（最多3次）：
1. ImportError（缺少依赖）
2. SyntaxError（语法错误）
3. 数据库连接失败（检查配置）
4. 端口被占用（建议更换端口）

### 需人工决策的情况
以下情况输出问题摘要，等待你的指令：
1. 3次自动修复失败
2. 架构设计决策（如"是否使用TimescaleDB"）
3. 需求变更（如"客户要求调整字段"）
4. 性能瓶颈（如"测试运行太慢"）

### 上下文管理
- 每完成一个阶段，建议执行`/clear`清理上下文
- 然后说"继续"，我重新读取master文件继续下阶段
- 这样可以避免上下文窗口溢出

---

## 当前状态

**状态**：未开始 / 阶段X进行中 / 等待确认
**最后更新**：2026-04-06
**下一步**：等待用户确认环境OK

---

## 快捷指令（你说这些我直接执行）

| 你说 | 我执行 |
|------|--------|
| "继续" | 继续下阶段 |
| "跳过" | 跳过当前阶段，进入下阶段 |
| "重试" | 重新执行当前阶段 |
| "回退" | 回退到上一阶段 |
| "报告" | 生成当前进度报告 |
| "Day 1" | 跳到Day 1开始 |
| "Day 2" | 跳到Day 2开始（如果Day1完成）|
| "清理" | 建议执行/clear清理上下文 |
