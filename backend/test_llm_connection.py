"""
快速测试 Road2All API 连接
"""

import asyncio
import os
from dotenv import load_dotenv

# 加载 .env
load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

async def test_llm_connection():
    """测试 LLM API 连接"""
    
    import httpx
    
    api_key = os.getenv("ROAD2ALL_API_KEY")
    model = os.getenv("ROAD2ALL_MODEL", "gpt-4o")
    api_base = os.getenv("ROAD2ALL_API_BASE", "https://api.siliconflow.cn/v1")
    
    print(f"🔍 LLM 连接配置信息")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"API Base: {api_base}")
    print(f"Model: {model}")
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    if not api_key or api_key == "sk-your-api-key-here":
        print("❌ 错误: API Key 未配置或仍为示例值")
        return False
    
    # 构建请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": "请用一句话介绍一下自己。"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        print("📤 正在发送测试请求到 Road2All API...")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            
            print(f"📥 收到响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                
                print()
                print("✅ API 连接成功！")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"📝 模型的回复：")
                print(f"   {content}")
                print()
                print(f"📊 Token 使用: {tokens}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                return True
            else:
                print(f"❌ API 调用失败")
                print(f"状态码: {response.status_code}")
                print(f"响应: {response.text[:200]}")
                return False
    
    except Exception as e:
        print(f"❌ 连接异常: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llm_connection())
    exit(0 if success else 1)
