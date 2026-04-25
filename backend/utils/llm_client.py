"""
LLM 客户端 - 统一的大模型调用接口
支持 OpenAI、Road2All、本地模型等
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any
from enum import Enum

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


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
    """统一的 LLM 客户端（连接池复用）"""
    
    # 类级共享连接池，避免每次调用重建 TCP/SSL 连接
    _shared_client: Optional[httpx.AsyncClient] = None
    _shared_client_config: Optional[Dict[str, Any]] = None
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or self._get_configured_provider()
        self.api_key = os.getenv("ROAD2ALL_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("ROAD2ALL_MODEL", "gpt-4o")
        self.api_base = os.getenv("ROAD2ALL_API_BASE", "https://api.siliconflow.cn/v1")
        self.timeout = float(os.getenv("LLM_TIMEOUT", "60"))
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "2"))
        self.retry_backoff = float(os.getenv("LLM_RETRY_BACKOFF", "0.6"))
        self.trust_env = os.getenv("LLM_TRUST_ENV", "0").strip().lower() in ("1", "true", "yes", "on")
        self.verify_ssl = os.getenv("LLM_VERIFY_SSL", "0").strip().lower() in ("1", "true", "yes", "on")
    
    @classmethod
    def _get_shared_client(
        cls,
        *,
        timeout: float,
        trust_env: bool,
        verify_ssl: bool,
    ) -> httpx.AsyncClient:
        """获取或创建共享的 httpx 异步客户端（连接池复用）"""
        target_config = {
            "timeout": timeout,
            "trust_env": trust_env,
            "verify_ssl": verify_ssl,
        }

        need_recreate = (
            cls._shared_client is None
            or cls._shared_client.is_closed
            or cls._shared_client_config != target_config
        )

        if need_recreate:
            if cls._shared_client is not None and not cls._shared_client.is_closed:
                try:
                    asyncio.create_task(cls._shared_client.aclose())
                except Exception:
                    pass

            cls._shared_client = httpx.AsyncClient(
                timeout=timeout,
                verify=verify_ssl,
                trust_env=trust_env,
                limits=httpx.Limits(
                    max_connections=10,
                    max_keepalive_connections=5,
                    keepalive_expiry=120,
                ),
            )
            cls._shared_client_config = target_config

        return cls._shared_client

    async def _post_with_retry(self, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> httpx.Response:
        """对网络抖动进行轻量重试，减少 ConnectError 触发概率。"""
        last_exc: Optional[Exception] = None
        proxy_keys = ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy")
        proxy_in_env = any(os.getenv(k) for k in proxy_keys)

        for attempt in range(self.max_retries + 1):
            try:
                client = self._get_shared_client(
                    timeout=self.timeout,
                    trust_env=self.trust_env,
                    verify_ssl=self.verify_ssl,
                )
                return await client.post(url, headers=headers, json=payload)
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RemoteProtocolError) as e:
                last_exc = e
                if attempt < self.max_retries:
                    wait = self.retry_backoff * (attempt + 1)
                    logger.warning(
                        "LLM 网络异常，准备重试: attempt=%s/%s type=%s trust_env=%s proxy_in_env=%s wait=%.1fs",
                        attempt + 1,
                        self.max_retries + 1,
                        type(e).__name__,
                        self.trust_env,
                        proxy_in_env,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue
                break

        raise Exception(
            f"LLM 网络连接失败: type={type(last_exc).__name__ if last_exc else 'unknown'}, "
            f"trust_env={self.trust_env}, proxy_in_env={proxy_in_env}. "
            f"可尝试设置 LLM_TRUST_ENV=0 或检查代理/网络连通性。"
        )
    
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
            response = await self._post_with_retry(
                url=f"{self.api_base}/chat/completions",
                headers=headers,
                payload=payload,
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
                response_text = response.text[:500] if response.text else ""
                logger.error(
                    "Road2All API 调用错误: status=%s body=%s",
                    response.status_code,
                    response_text,
                )
                raise Exception(
                    f"LLM API 失败: status={response.status_code}, body={response_text or '<empty>'}"
                )
        
        except asyncio.TimeoutError:
            logger.error("LLM API 调用超时")
            raise Exception("LLM API 调用超时")
        except Exception as e:
            logger.error(
                "LLM 调用异常: type=%s repr=%r str=%s",
                type(e).__name__,
                e,
                str(e),
                exc_info=True,
            )
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
            response = await self._post_with_retry(
                url="https://api.openai.com/v1/chat/completions",
                headers=headers,
                payload=payload,
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
                response_text = response.text[:500] if response.text else ""
                raise Exception(
                    f"OpenAI API 失败: status={response.status_code}, body={response_text or '<empty>'}"
                )
        
        except Exception as e:
            logger.error(
                "OpenAI 调用异常: type=%s repr=%r str=%s",
                type(e).__name__,
                e,
                str(e),
                exc_info=True,
            )
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
