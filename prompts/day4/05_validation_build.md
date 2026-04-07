# Day 4 - Prompt 5: 前端验证、Docker集成与Git提交

**时机**：所有界面开发完成后执行
**预期耗时**：Claude生成20分钟，你Review 15分钟
**人工决策**：确认前端功能完整，性能达标，准备Git提交

---

## 输入Prompt

```text
请完成前端验证、Docker集成和Git提交。

【端到端测试脚本】（frontend/validate_frontend.py）

创建前端验证脚本：

```python
#!/usr/bin/env python3
"""前端验证脚本

测试前端构建、API连通性和基本功能
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令，返回结果"""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def check_npm_install():
    """检查npm依赖安装"""
    print("[1/6] 检查npm依赖...")
    frontend_dir = Path(__file__).parent
    node_modules = frontend_dir / "node_modules"
    
    if not node_modules.exists():
        print("  未找到node_modules，执行npm install...")
        success, stdout, stderr = run_command("npm install", cwd=frontend_dir)
        if not success:
            print(f"  ✗ npm install失败: {stderr}")
            return False
    
    print("  ✓ 依赖已安装")
    return True

def check_typescript_build():
    """检查TypeScript编译"""
    print("[2/6] 检查TypeScript编译...")
    frontend_dir = Path(__file__).parent
    
    success, stdout, stderr = run_command("npm run build", cwd=frontend_dir)
    if not success:
        print(f"  ✗ TypeScript编译失败: {stderr}")
        return False
    
    print("  ✓ TypeScript编译通过")
    return True

def check_api_connectivity():
    """检查API连通性"""
    print("[3/6] 检查API连通性...")
    
    try:
        # 检查后端健康端点
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✓ 后端API连接正常: {response.json()}")
            return True
        else:
            print(f"  ✗ 后端API返回异常状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ✗ 无法连接到后端API（http://localhost:8000）")
        print("    请确保后端服务已启动: docker-compose up -d")
        return False
    except Exception as e:
        print(f"  ✗ 检查API时出错: {e}")
        return False

def check_env_files():
    """检查环境配置文件"""
    print("[4/6] 检查环境配置文件...")
    frontend_dir = Path(__file__).parent
    
    env_dev = frontend_dir / ".env.development"
    env_prod = frontend_dir / ".env.production"
    
    if not env_dev.exists():
        print("  ✗ 缺少.env.development文件")
        return False
    
    if not env_prod.exists():
        print("  ✗ 缺少.env.production文件")
        return False
    
    # 检查关键变量
    with open(env_dev) as f:
        content = f.read()
        if "VITE_API_BASE_URL" not in content:
            print("  ✗ .env.development缺少VITE_API_BASE_URL")
            return False
    
    print("  ✓ 环境配置文件完整")
    return True

def check_dockerfile():
    """检查Dockerfile"""
    print("[5/6] 检查Dockerfile...")
    frontend_dir = Path(__file__).parent
    dockerfile = frontend_dir / "Dockerfile"
    
    if not dockerfile.exists():
        print("  ✗ 缺少Dockerfile")
        return False
    
    print("  ✓ Dockerfile存在")
    return True

def run_linter():
    """运行代码检查"""
    print("[6/6] 运行代码检查...")
    frontend_dir = Path(__file__).parent
    
    # 检查是否有lint命令
    package_json = frontend_dir / "package.json"
    with open(package_json) as f:
        import json
        config = json.load(f)
        scripts = config.get("scripts", {})
        
        if "lint" in scripts:
            success, stdout, stderr = run_command("npm run lint", cwd=frontend_dir)
            if not success:
                print(f"  ⚠ 代码检查发现问题: {stdout}")
                # 不返回False，因为lint错误不一定是致命的
            else:
                print("  ✓ 代码检查通过")
        else:
            print("  ℹ 未配置lint脚本，跳过")
    
    return True

def main():
    print("=" * 60)
    print("龙泉驿环卫智能体 - Day 4 前端验证")
    print("=" * 60)
    
    checks = [
        check_npm_install,
        check_env_files,
        check_dockerfile,
        check_api_connectivity,
        check_typescript_build,
        run_linter,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"  ✗ 检查出错: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    if all(results):
        print("结果: ✓ 所有检查通过")
        print("=" * 60)
        return 0
    else:
        print("结果: ✗ 部分检查失败")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

【性能测试】（frontend/performance_test.py）

简单的性能测试：

```python
"""前端性能测试

测试页面加载性能
"""

import requests
import time
import statistics

def test_api_response_time():
    """测试API响应时间"""
    print("[性能测试] API响应时间")
    
    endpoints = [
        "http://localhost:8000/health",
        "http://localhost:8000/api/v1/devices",
        "http://localhost:8000/api/v1/alerts",
    ]
    
    for url in endpoints:
        times = []
        for _ in range(5):
            start = time.time()
            try:
                response = requests.get(url, timeout=10)
                elapsed = (time.time() - start) * 1000  # ms
                times.append(elapsed)
            except Exception as e:
                print(f"  ✗ {url}: 请求失败 - {e}")
                break
        else:
            avg_time = statistics.mean(times)
            print(f"  ✓ {url}: 平均响应时间 {avg_time:.1f}ms")

if __name__ == "__main__":
    test_api_response_time()
```

【Dockerfile完善】（frontend/Dockerfile）

确保Dockerfile完整：

```dockerfile
# 构建阶段
FROM node:18-alpine as builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./
RUN npm install

# 复制源代码
COPY . .

# 构建
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置（如果需要）
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

【Docker Compose集成】（更新backend/docker-compose.yml）

添加前端服务：

```yaml
  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    container_name: lqy_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

【构建脚本】（frontend/build.sh）

一键构建脚本：

```bash
#!/bin/bash
set -e

echo "===== 龙泉驿环卫智能体 - 前端构建 ====="

# 安装依赖
echo "[1/4] 安装依赖..."
npm install

# 代码检查
echo "[2/4] 代码检查..."
npm run lint || echo "代码检查发现问题，继续构建..."

# TypeScript编译
echo "[3/4] TypeScript编译..."
npm run build

# 运行测试
echo "[4/4] 运行验证..."
python3 validate_frontend.py

echo "===== 构建完成 ====="
```

【生产环境配置】（frontend/.env.production）

```
VITE_API_BASE_URL=/api
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_TITLE=龙泉驿环卫智能体
VITE_APP_VERSION=1.0.0
```

【README更新】（frontend/README.md）

创建前端项目说明：

```markdown
# 龙泉驿环卫智能体 - 前端

技术栈：Vue 3 + TypeScript + Vite + Element Plus + ECharts

## 快速开始

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产包
npm run build

# 代码检查
npm run lint
```

## 项目结构

- src/api/ - API接口
- src/components/ - 组件
- src/views/ - 页面
- src/stores/ - Pinia状态管理
- src/composables/ - 组合式函数

## 验证

```bash
python3 validate_frontend.py
```

## Docker构建

```bash
docker build -t lqy-frontend .
docker run -p 80:80 lqy-frontend
```
```

【测试清单】（frontend/CHECKLIST.md）

手动测试清单：

```markdown
# Day 4 测试清单

## 功能测试

- [ ] 页面能正常加载，无Console报错
- [ ] WebSocket连接成功（Header状态绿色）
- [ ] 模拟器数据实时显示在仪表盘
- [ ] 温度曲线每10秒更新
- [ ] 产生异常时弹出告警通知

## 告警管理

- [ ] 告警列表能正常筛选
- [ ] 能确认告警
- [ ] 能解决告警
- [ ] 批量操作正常

## 设备管理

- [ ] 设备列表显示正常
- [ ] 能新增设备
- [ ] 能编辑设备
- [ ] 能删除设备
- [ ] 设备详情显示实时数据
- [ ] 历史图表可切换时间范围

## 性能测试

- [ ] 页面运行10分钟不卡顿
- [ ] 内存占用稳定在200MB以内
- [ ] 温度曲线滚动流畅

## 兼容性

- [ ] Chrome正常
- [ ] Firefox正常
- [ ] Edge正常
```

【Git提交】

```bash
# 提交前端代码
git add frontend/
git commit -m "Day 4: 前端看板 - Vue3 + ECharts 实时可视化

- 初始化Vue3 + TypeScript + Vite项目
- 集成Element Plus UI组件库
- 实现实时仪表盘（温度曲线、仪表盘、统计卡片）
- 实现告警管理（列表、筛选、确认/解决）
- 实现设备管理（列表、详情、实时数据）
- WebSocket实时数据推送集成
- 响应式布局，适配多屏
- Docker容器化配置

验证: python3 frontend/validate_frontend.py"

# 打标签
git tag day4-complete
```

【性能优化建议】（可选）

如果发现性能问题：

1. ECharts优化：
   - 使用`animation: false`关闭动画
   - 限制数据点数量（最多100个点）
   - 使用`appendData`增量更新

2. Vue优化：
   - 大列表使用虚拟滚动
   - 使用`shallowRef`避免深层响应
   - 组件懒加载

3. 网络优化：
   - API响应压缩
   - WebSocket心跳间隔调整
   - HTTP缓存策略

【验证步骤】

执行完整验证：

1. 环境检查：
   ```bash
   cd frontend
   python3 validate_frontend.py
   ```

2. 功能测试：
   ```bash
   npm run dev
   # 打开浏览器测试所有功能
   ```

3. 构建测试：
   ```bash
   npm run build
   # 检查dist目录生成
   ```

4. Docker测试：
   ```bash
   docker build -t lqy-frontend .
   docker run -p 80:80 lqy-frontend
   # 访问 http://localhost
   ```

5. 端到端测试：
   - 启动后端
   - 启动模拟器
   - 验证实时数据流
   - 验证告警通知
   - 运行30分钟观察稳定性
```

---

## 预期输出

```
生成文件：
- frontend/validate_frontend.py [完成]
- frontend/performance_test.py [完成]
- frontend/build.sh [完成]
- frontend/Dockerfile [更新]
- frontend/.env.production [更新]
- frontend/README.md [完成]
- frontend/CHECKLIST.md [完成]
- docker-compose.yml [更新，添加frontend服务]

验证结果：
✓ TypeScript编译通过
✓ API连通性正常
✓ 环境配置完整
✓ Docker构建成功
✓ 代码检查通过

Git提交：
day4-complete 标签
```

---

## 你的决策

- [ ] 所有验证通过 → 标记Day 4完成
- [ ] 有编译错误 → 让Claude修复
- [ ] 性能不达标 → 优化后再提交
- [ ] 功能完整 → 准备Day 5

---

## 手工验证命令

```bash
# 1. 完整验证
cd frontend
python3 validate_frontend.py

# 2. 构建测试
npm run build

# 3. Docker测试
docker build -t lqy-frontend .
docker run -p 80:80 lqy-frontend

# 4. 提交
git add .
git commit -m "Day 4: 前端看板 - Vue3 + ECharts 实时可视化"
git tag day4-complete
```

## Day 4 完成标准

- [ ] 前端项目能正常构建
- [ ] TypeScript编译无错误
- [ ] 所有页面可正常访问
- [ ] WebSocket实时推送工作
- [ ] 告警通知正常弹出
- [ ] 验证脚本通过
- [ ] Docker构建成功
- [ ] Git提交并打标签

## 明日预告

Day 5将构建预测算法，实现趋势分析和提前预警，前端将展示预测曲线。
