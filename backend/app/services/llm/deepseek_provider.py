import httpx
import logging
from app.core.config import settings
from .base import LLMProvider

logger = logging.getLogger(__name__)

class DeepSeekProvider(LLMProvider):
    async def chat(self, messages: list[dict], options: dict | None = None) -> str:
        timeout = (options or {}).get("timeout", settings.DEEPSEEK_TIMEOUT)
        model = (options or {}).get("model", settings.DEEPSEEK_MODEL)
        url = f"{settings.DEEPSEEK_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek chat error: {e}")
            raise

    async def is_available(self) -> bool:
        if not settings.DEEPSEEK_ENABLED or not settings.DEEPSEEK_API_KEY:
            return False
        return True

    async def test_connection(self) -> dict:
        if not settings.DEEPSEEK_API_KEY:
            return {"available": False, "error": "DEEPSEEK_API_KEY is not configured", "latency_ms": None}
        import time
        start = time.time()
        url = f"{settings.DEEPSEEK_BASE_URL}/models"
        headers = {"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, headers=headers)
                latency = round((time.time() - start) * 1000, 1)
                if res.status_code in [200, 201]:
                    return {"available": True, "error": None, "latency_ms": latency, "model": settings.DEEPSEEK_MODEL}
                else:
                    return {"available": False, "error": f"HTTP {res.status_code}: {res.text[:100]}", "latency_ms": latency}
        except Exception as e:
            latency = round((time.time() - start) * 1000, 1)
            return {"available": False, "error": str(e), "latency_ms": latency}
