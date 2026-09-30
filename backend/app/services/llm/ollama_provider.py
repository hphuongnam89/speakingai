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
            "stream": False,
            "think": (options or {}).get("think", settings.OLLAMA_THINK),
            "options": {
                "num_ctx": settings.OLLAMA_CONTEXT_LENGTH,
                "num_predict": (options or {}).get("max_tokens", settings.OLLAMA_MAX_OUTPUT_TOKENS),
                "temperature": 0.4,
            },
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                logger.info(
                    "Ollama completed model=%s reason=%s output_tokens=%s duration_ms=%s",
                    model, data.get("done_reason"), data.get("eval_count"),
                    round(data.get("total_duration", 0) / 1e6),
                )
                content = data.get("message", {}).get("content", "").strip()
                if not content:
                    raise RuntimeError(f"Ollama returned an empty reply for model {model}")
                if data.get("done_reason") == "length":
                    raise RuntimeError("Ollama reply was cut short. Please try a shorter answer.")
                return content
        except httpx.TimeoutException as e:
            logger.warning("Ollama request timed out after %s seconds", timeout)
            raise TimeoutError(f"Ollama request timed out after {timeout} seconds") from e
        except Exception as e:
            logger.exception("Ollama chat failed (%s): %s", type(e).__name__, e)
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
                        "available": settings.OLLAMA_MODEL in models,
                        "error": None if settings.OLLAMA_MODEL in models else "Configured model is not installed",
                        "latency_ms": latency,
                        "model": settings.OLLAMA_MODEL,
                        "installed_models": models
                    }
                return {"available": False, "error": f"HTTP {res.status_code}", "latency_ms": latency}
        except Exception as e:
            latency = round((time.time() - start) * 1000, 1)
            return {"available": False, "error": str(e), "latency_ms": latency}
