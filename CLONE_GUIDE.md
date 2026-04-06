# 克隆后设置指南

**适用于**：从GitHub克隆项目后，在新电脑上开始工作

---

## 第一步：克隆仓库

```bash
# 克隆项目（替换为你的仓库地址）
git clone https://github.com/YOUR_USERNAME/lqy-system.git
cd lqy-system

# 查看项目结构
ls -la
```

**确认看到以下文件**：
- START.md ⭐
- ARCHITECTURE_CONTRACT.md
- SEMI_AUTO_GUIDE.md
- prompts/
- README.md
- .gitignore

---

## 第二步：环境检查

### 检查Python

```bash
python3 --version
# 需要 3.10+

# 如果没有，安装方式：
# Ubuntu: sudo apt update && sudo apt install python3.11 python3.11-venv
# Mac: brew install python@3.11
# Windows: 从官网下载安装
```

### 检查Docker

```bash
docker --version
docker-compose --version

# 确认Docker守护进程运行中
docker ps
# 应该显示空列表（没有容器），但不报错
```

### 检查Claude Code

```bash
which claude
# 或
claude --version

# 如果没有安装，参考：https://docs.anthropic.com/en/docs/claude-code/installation
```

### 检查端口

```bash
# Linux/Mac
lsof -i :8000
lsof -i :5432
lsof -i :6379

# Windows
netstat -ano | findstr :8000

# 确认这些端口没有被占用
```

---

## 第三步：GitHub配置（必须）

确保Claude Code能访问GitHub：

```bash
# 检查Git配置
git config user.name
git config user.email

# 如果没有，设置：
git config user.name "Your Name"
git config user.name "your.email@example.com"

# 测试GitHub连接
git remote -v
# 应该显示 origin 指向你的仓库
```

---

## 第四步：首次启动

```bash
# 在项目根目录
cd /path/to/lqy-system

# 启动Claude Code
claude
```

**在Claude中输入**：
```
请读取 START.md 并开始执行
```

---

## 第五步：Claude自动执行流程

输入启动指令后，Claude会：

1. **自动检查环境**
   ```
   启动检查
   ========
   Python: 3.11.2 [OK]
   Docker: running [OK]
   端口: 空闲 [OK]
   ```

2. **读取架构契约**
   ```
   架构契约已加载
   =============
   - 技术栈: FastAPI + SQLModel + PostgreSQL + Redis
   ...
   ```

3. **询问从哪天开始**
   ```
   请告诉我你的选择：
   1. "开始Day 1"
   2. "继续Day X"
   3. "验证当前"
   ```

4. **你说**：`开始Day 1`

5. **Claude自动执行**：Step 1 → 完成后等你确认 → Step 2 → ...

---

## 第六步：你的工作

虽然Claude自动生成代码，但你必须：

### 每Step完成后（Claude会暂停等你）

```
Day 1 - Step 1 完成
===================
...
下一步选项:
1. "继续"
2. "检查"
3. "重做"
4. "结束"

请告诉我你的选择：
```

**你的选择**：
- `"检查"` - 先查看生成的代码，确认质量
- `"继续"` - 满意，进入下一步
- `"重做"` - 有问题，重新生成
- `"结束"` - 今天到此，明天继续

### 关键验证（你必须执行）

```bash
# 在Claude之外，你自己开终端执行：

cd lqy-system/backend

# 1. 检查Git状态
git status
git diff

# 2. 运行测试
make test
# 或
pytest -v

# 3. 手动API测试
curl http://localhost:8000/health

# 4. 确认Git提交
git log --oneline -3
```

---

## 第七步：日常开发循环

### 每天开始

```bash
cd lqy-system
git status                    # 确认状态干净
claude                        # 启动

# 在Claude中：
请读取 START.md 并开始执行

# 说：继续Day X（X是你上次做到的天数）
```

### 每天结束

```bash
# 1. 确认Git提交
git add .
git commit -m "Day X: 完成描述"
git tag dayX-complete
git push origin main --tags

# 2. 更新进度
echo '{"current_day": X, "current_step": Y}' > progress.json
git add progress.json && git commit -m "Update progress"

# 3. 退出Claude
# 在Claude中输入：/clear 或直接退出
```

---

## 常见问题

### Q1: Claude说"无法读取文件"

**原因**：路径错误或权限问题

**解决**：
```bash
# 确认文件存在
ls -la START.md

# 在Claude中用绝对路径：
请读取 /path/to/lqy-system/START.md
```

### Q2: Docker启动失败

**检查**：
```bash
# Docker是否运行
docker ps

# 端口是否被占用
lsof -i :8000

# 权限问题（Linux）
sudo usermod -aG docker $USER
# 然后重新登录
```

### Q3: 测试失败

**Claude会询问你**：
```
测试失败
=======
失败测试: [列表]

选择:
1. "自动修复" - 我尝试修复
2. "查看详情" - 输出完整错误
3. "跳过" - 标记技术债
4. "回退" - 回到上一步
```

**建议**：
- 简单错误（typo）：选"自动修复"
- 复杂错误：选"查看详情"，你自己看代码决定
- 不确定：选"跳过"，继续下阶段

### Q4: 上下文太长，Claude"失忆"

**现象**：Claude忘记之前的架构决策

**解决**：
```
你: 清理
Claude: [执行上下文压缩]
你: 契约
Claude: [重新读取ARCHITECTURE_CONTRACT.md]
你: 继续Day X Step Y
```

---

## 文件说明（克隆后）

| 文件 | 用途 | 修改？ |
|------|------|--------|
| START.md | Claude启动入口 | ❌ 不修改 |
| ARCHITECTURE_CONTRACT.md | 技术规范 | ❌ 不修改 |
| prompts/dayX/*.md | 详细Prompt | ❌ 不修改 |
| SEMI_AUTO_GUIDE.md | 人工操作指南 | ⚠️ 按需修改 |
| progress.json | 当前进度 | ✅ 自动更新 |
| backend/ | 生成的代码 | ✅ 自动生成 |

---

## 快速检查清单

开始工作前，确认：

- [ ] Python 3.10+
- [ ] Docker运行中
- [ ] Claude Code可用
- [ ] 端口8000/5432/6379空闲
- [ ] GitHub配置正确
- [ ] 项目目录可写

---

## 开始你的第一次

```bash
cd lqy-system
claude
```

然后输入：
```
请读取 START.md 并开始执行
```

祝顺利！
