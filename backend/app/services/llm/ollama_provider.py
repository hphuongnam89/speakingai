import httpx
import logging
from app.core.config import settings
from .base import LLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    async def chat(self, messages: list[dict], options: dict | None = None) -> str:
        timeout = (options or {}).get("timeout", settings.OLLAMA_TIMEOUT)
        model = (options or {}).get("model", settings.OLLAMA_MODEL)
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise

    async def is_available(self) -> bool:
        url = f"{settings.OLLAMA_BASE_URL}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False

    async def test_connection(self) -> dict:
        import time
        start = time.time()
        url = f"{settings.OLLAMA_BASE_URL}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url)
                latency = round((time.time() - start) * 1000, 1)
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    return {
                        "available": True,
                        "error": None,
                        "latency_ms": latency,
                        "model": settings.OLLAMA_MODEL,
                        "installed_models": models
                    }
                return {"available": False, "error": f"HTTP {res.status_code}", "latency_ms": latency}
        except Exception as e:
            latency = round((time.time() - start) * 1000, 1)
            return {"available": False, "error": str(e), "latency_ms": latency}
