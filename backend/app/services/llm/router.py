import time
import logging
from typing import Optional, Tuple
from fastapi import HTTPException
from app.core.config import settings
from .ollama_provider import OllamaProvider
from .deepseek_provider import DeepSeekProvider

logger = logging.getLogger(__name__)

class ModelRouter:
    """
    Intelligent Model Router with Automatic Cloud Fallback:
    1. Primary: Local Ollama (low latency, zero cost, offline capable).
    2. Fallback / High-Quality: DeepSeek Cloud (when Ollama fails, times out, or high-accuracy requested).
    """

    def __init__(self):
        self.ollama = OllamaProvider()
        self.deepseek = DeepSeekProvider()

    async def chat_with_metadata(
        self, messages: list[dict], options: Optional[dict] = None
    ) -> Tuple[str, dict]:
        opts = options or {}
        preference = opts.get("preference", settings.MODEL_ROUTING_PREFERENCE)
        force_cloud = opts.get("force_cloud", False) or opts.get("high_quality", False)
        local_only = opts.get("local_only", False)
        cloud_fallback_allowed = opts.get("cloud_fallback", True)
        
        start_time = time.time()
        fallback_triggered = False
        fallback_reason = None
        provider_used = "none"
        model_used = None

        # Case 1: Force Cloud or Cloud-Only Mode
        if force_cloud or preference == "cloud_only":
            if not settings.DEEPSEEK_ENABLED or not (await self.deepseek.is_available()):
                raise HTTPException(
                    status_code=503,
                    detail="Cloud LLM (DeepSeek) requested but not enabled or API key missing"
                )
            try:
                reply = await self.deepseek.chat(messages, opts)
                latency = round((time.time() - start_time) * 1000, 1)
                return reply, {
                    "provider_used": "deepseek",
                    "model_used": settings.DEEPSEEK_MODEL,
                    "fallback_triggered": False,
                    "fallback_reason": None,
                    "latency_ms": latency
                }
            except Exception as e:
                logger.error(f"DeepSeek direct call failed: {e}")
                raise HTTPException(status_code=502, detail=f"Cloud LLM error: {e}")

        # Case 2: Local Only Mode (No fallback permitted)
        if local_only or preference == "local_only":
            try:
                reply = await self.ollama.chat(messages, opts)
                latency = round((time.time() - start_time) * 1000, 1)
                return reply, {
                    "provider_used": "ollama",
                    "model_used": settings.OLLAMA_MODEL,
                    "fallback_triggered": False,
                    "fallback_reason": None,
                    "latency_ms": latency
                }
            except Exception as e:
                logger.error(f"Local Ollama failed in local_only mode: {e}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Local Ollama inference failed: {e}. Cloud fallback is disabled."
                )

        # Case 3: Auto Mode (Local Ollama first -> Automatic DeepSeek Cloud Fallback)
        try:
            # Attempt Local Ollama first
            reply = await self.ollama.chat(messages, opts)
            latency = round((time.time() - start_time) * 1000, 1)
            return reply, {
                "provider_used": "ollama",
                "model_used": settings.OLLAMA_MODEL,
                "fallback_triggered": False,
                "fallback_reason": None,
                "latency_ms": latency
            }
        except Exception as ollama_err:
            fallback_reason = str(ollama_err)
            logger.warning(f"Ollama failed or timed out ({ollama_err}). Evaluating cloud fallback...")

            # Fallback to DeepSeek if enabled
            if cloud_fallback_allowed and settings.DEEPSEEK_ENABLED and (await self.deepseek.is_available()):
                logger.info("Triggering automatic DeepSeek cloud fallback...")
                try:
                    reply = await self.deepseek.chat(messages, opts)
                    latency = round((time.time() - start_time) * 1000, 1)
                    return reply, {
                        "provider_used": "deepseek",
                        "model_used": settings.DEEPSEEK_MODEL,
                        "fallback_triggered": True,
                        "fallback_reason": fallback_reason,
                        "latency_ms": latency
                    }
                except Exception as deepseek_err:
                    logger.error(f"Both Ollama and DeepSeek fallback failed: {deepseek_err}")
                    raise HTTPException(
                        status_code=503,
                        detail=f"All LLM providers failed. Ollama: {fallback_reason} | DeepSeek: {deepseek_err}"
                    )

            raise HTTPException(
                status_code=503,
                detail=f"Local Ollama unavailable: {fallback_reason}. Cloud fallback is not configured or disabled."
            )

    async def chat(self, messages: list[dict], options: Optional[dict] = None) -> str:
        reply, _ = await self.chat_with_metadata(messages, options)
        return reply

    async def get_active_provider(self) -> str:
        if await self.ollama.is_available():
            return "ollama"
        if settings.DEEPSEEK_ENABLED and await self.deepseek.is_available():
            return "deepseek"
        return "none"

    async def get_available_models(self) -> dict:
        available = []
        if await self.ollama.is_available():
            available.append(f"ollama ({settings.OLLAMA_MODEL})")
        if settings.DEEPSEEK_ENABLED and await self.deepseek.is_available():
            available.append(f"deepseek ({settings.DEEPSEEK_MODEL})")
            
        active = await self.get_active_provider()
        
        return {
            "active": active,
            "available": available,
            "cloud_fallback_enabled": settings.DEEPSEEK_ENABLED,
            "routing_preference": settings.MODEL_ROUTING_PREFERENCE
        }

    async def check_providers_health(self) -> dict:
        ollama_status = await self.ollama.test_connection()
        deepseek_status = await self.deepseek.test_connection()
        active = await self.get_active_provider()

        return {
            "active_provider": active,
            "routing_preference": settings.MODEL_ROUTING_PREFERENCE,
            "cloud_fallback_ready": bool(settings.DEEPSEEK_ENABLED and deepseek_status.get("available")),
            "ollama": ollama_status,
            "deepseek": deepseek_status
        }

_model_router = None

def get_model_router() -> ModelRouter:
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router
