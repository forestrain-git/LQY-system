#!/usr/bin/env python3
"""
Kimi API 连接测试脚本
Test Kimi API Connection
"""

import os
import sys
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_kimi_api():
    """测试Kimi API连接"""
    api_key = os.getenv("KIMI_API_KEY", "")

    if not api_key:
        print("❌ 错误: 未找到 KIMI_API_KEY 环境变量")
        print("请确保 .env 文件中包含 KIMI_API_KEY")
        return False

    # 隐藏部分Key用于显示
    masked_key = api_key[:20] + "..." + api_key[-10:]
    print(f"✓ 找到 API Key: {masked_key}")

    # 测试API连接
    try:
        print("\n正在测试 Kimi API 连接...")

        response = httpx.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "moonshot-v1-8k",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, this is a test. Please respond with 'Kimi API is working!'"}
                ],
                "max_tokens": 50,
                "temperature": 0.3
            },
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"✅ API 连接成功!")
            print(f"✅ 响应内容: {content}")
            print(f"✅ 使用模型: {data.get('model', 'unknown')}")
            print(f"✅ 消耗tokens: {data.get('usage', {}).get('total_tokens', 'unknown')}")
            return True
        else:
            print(f"❌ API 请求失败")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False

    except httpx.TimeoutException:
        print("❌ 错误: 请求超时")
        print("可能原因: 网络连接问题或API服务不可用")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def test_backend_integration():
    """测试后端集成配置"""
    print("\n" + "="*50)
    print("测试后端集成配置")
    print("="*50)

    try:
        # 检查后端AI服务配置
        sys.path.insert(0, 'backend')
        from app.modules.ai.service import get_ai_service

        service = get_ai_service()
        if service.api_key:
            masked_key = service.api_key[:20] + "..." + service.api_key[-10:]
            print(f"✅ AI服务已配置 API Key: {masked_key}")
            return True
        else:
            print("❌ AI服务未配置 API Key")
            return False
    except Exception as e:
        print(f"⚠️  无法检查后端的配置: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("Kimi API 连接测试")
    print("="*50)

    success = test_kimi_api()
    test_backend_integration()

    if success:
        print("\n✅ 所有测试通过! Kimi API 配置正确")
        sys.exit(0)
    else:
        print("\n❌ 测试未通过，请检查配置")
        sys.exit(1)
