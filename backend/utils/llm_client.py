"""
LLM 客户端 - 统一的大模型调用接口
支持 OpenAI、Road2All、本地模型等
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any
from enum import Enum

import httpx
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(str, Enum):
    """LLM 提供商枚举"""
    OPENAI = "openai"
    ROAD2ALL = "road2all"
    CLAUDE = "claude"
    LOCAL = "local"


class LLMResponse:
    """LLM 响应对象"""
    def __init__(self, content: str, tokens_used: int = 0, model: str = ""):
        self.content = content
        self.tokens_used = tokens_used
        self.model = model


class LLMClient:
    """统一的 LLM 客户端"""
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or self._get_configured_provider()
        self.api_key = os.getenv("ROAD2ALL_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("ROAD2ALL_MODEL", "gpt-4o")
        self.api_base = os.getenv("ROAD2ALL_API_BASE", "https://api.road2all.tech/v1")
        self.timeout = 60
    
    def _get_configured_provider(self) -> LLMProvider:
        """获取配置的提供商"""
        if os.getenv("ROAD2ALL_API_KEY"):
            return LLMProvider.ROAD2ALL
        elif os.getenv("OPENAI_API_KEY"):
            return LLMProvider.OPENAI
        else:
            return LLMProvider.ROAD2ALL  # 默认使用 Road2All
    
    async def call_async(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        异步调用 LLM
        
        Args:
            system_prompt: 系统角色提示
            user_prompt: 用户提示
            temperature: 温度参数（0.0-1.0）
            max_tokens: 最大输出token数
            **kwargs: 其他参数
        
        Returns:
            LLMResponse 对象
        """
        
        if self.provider == LLMProvider.ROAD2ALL:
            return await self._call_road2all_async(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif self.provider == LLMProvider.OPENAI:
            return await self._call_openai_async(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")
    
    async def _call_road2all_async(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """调用 Road2All API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    tokens = data.get("usage", {}).get("total_tokens", 0)
                    return LLMResponse(
                        content=content,
                        tokens_used=tokens,
                        model=self.model
                    )
                else:
                    print(f"API 调用错误: {response.status_code} - {response.text}")
                    raise Exception(f"LLM API 失败: {response.status_code}")
        
        except asyncio.TimeoutError:
            print("LLM API 调用超时")
            raise Exception("LLM API 调用超时")
        except Exception as e:
            print(f"LLM 调用异常: {e}")
            raise
    
    async def _call_openai_async(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """调用 OpenAI API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    tokens = data.get("usage", {}).get("total_tokens", 0)
                    return LLMResponse(
                        content=content,
                        tokens_used=tokens,
                        model=self.model
                    )
                else:
                    raise Exception(f"OpenAI API 失败: {response.status_code}")
        
        except Exception as e:
            print(f"OpenAI 调用异常: {e}")
            raise
    
    def call_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """同步调用 LLM（如果需要）"""
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.call_async(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            )
        finally:
            loop.close()


# 示例用法和测试
if __name__ == "__main__":
    async def test():
        client = LLMClient()
        
        result = await client.call_async(
            system_prompt="你是一个有帮助的助手。",
            user_prompt="请简要介绍一下 Python 的特点。",
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"模型: {result.model}")
        print(f"响应: {result.content}")
        print(f"Token 使用: {result.tokens_used}")
    
    # 运行测试
    # asyncio.run(test())
