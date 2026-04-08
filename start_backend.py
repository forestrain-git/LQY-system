#!/usr/bin/env python3
"""
启动后端服务脚本
"""

import os
import sys

# 设置正确的路径
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, 'backend')
sys.path.insert(0, backend_dir)

# 设置环境变量
os.environ['PYTHONPATH'] = backend_dir

# 导入并启动
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
