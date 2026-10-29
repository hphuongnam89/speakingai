from pydantic_settings import BaseSettings
from pydantic import model_validator

class Settings(BaseSettings):
    APP_NAME: str = "IELTS Speaking AI Coach"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "ornith-1.5:9b"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_ENABLED: bool = False
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DATABASE_URL: str = "sqlite:///./data/app.db"
    WHISPER_MODEL: str = "medium.en"
    WHISPER_DEVICE: str = "auto"  # auto, cuda, cpu
    WHISPER_COMPUTE_TYPE: str = "auto"  # auto, float16, int8
    AUDIO_DIR: str = "./data/audio"
    MAX_AUDIO_BYTES: int = 15 * 1024 * 1024
    MAX_AUDIO_DURATION_MS: int = 180000
    AUDIO_RETENTION_HOURS: int = 24
    DELETE_AUDIO_AFTER_TRANSCRIPTION: bool = False
    PRONUNCIATION_ASSESSOR_URL: str = ""
    PRONUNCIATION_ASSESSOR_TIMEOUT: float = 300.0
    LLM_TIMEOUT: int = 300
    OLLAMA_TIMEOUT: float = 300.0
    OLLAMA_CONTEXT_LENGTH: int = 4096
    OLLAMA_MAX_OUTPUT_TOKENS: int = 1536
    OLLAMA_THINK: bool = False
    DEEPSEEK_TIMEOUT: float = 30.0
    MODEL_ROUTING_PREFERENCE: str = "auto"  # auto, local_only, cloud_only
    
    # Production & Security
    API_KEY: str = ""
    API_KEY_ENABLED: bool = False
    AUTH_SECRET: str = "development-only-change-me-not-for-production-32"
    ACCESS_TOKEN_TTL_MINUTES: int = 720
    SENTRY_DSN: str = ""
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 120
    CORS_ORIGINS: str = "http://localhost,http://127.0.0.1"
    ENVIRONMENT: str = "development"
    ENABLE_SECURITY_HEADERS: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}

    @model_validator(mode="after")
    def validate_production_security(self):
        # Cap local context length to 4096 if set to excessive values (e.g. 32768) in OS environment
        if self.OLLAMA_CONTEXT_LENGTH > 4096:
            self.OLLAMA_CONTEXT_LENGTH = 4096

        if self.MAX_AUDIO_BYTES < 1024 or self.MAX_AUDIO_BYTES > 100 * 1024 * 1024:
            raise ValueError("MAX_AUDIO_BYTES must be between 1KB and 100MB")
        if self.MAX_AUDIO_DURATION_MS < 1000 or self.MAX_AUDIO_DURATION_MS > 900000:
            raise ValueError("MAX_AUDIO_DURATION_MS must be between 1s and 15m")
        if self.AUDIO_RETENTION_HOURS < 1:
            raise ValueError("AUDIO_RETENTION_HOURS must be at least 1")
        if self.RATE_LIMIT_PER_MINUTE < 1:
            raise ValueError("RATE_LIMIT_PER_MINUTE must be at least 1")
        if not 1 <= self.ACCESS_TOKEN_TTL_MINUTES <= 10080:
            raise ValueError("ACCESS_TOKEN_TTL_MINUTES must be between 1 minute and 7 days")

        if self.ENVIRONMENT.strip().lower() == "production":
            if not self.API_KEY_ENABLED:
                raise ValueError("API_KEY_ENABLED must be true in production")
            if len(self.API_KEY) < 32 or self.API_KEY.lower().startswith("your_secret"):
                raise ValueError("Set API_KEY to a random secret with at least 32 characters")
            if len(self.AUTH_SECRET) < 32 or self.AUTH_SECRET.lower().startswith(("development-only", "your_")):
                raise ValueError("Set AUTH_SECRET to a random secret with at least 32 characters")
            if not self.RATE_LIMIT_ENABLED:
                raise ValueError("RATE_LIMIT_ENABLED must be true in production")
            if not self.CORS_ORIGINS.strip() or "*" in self.CORS_ORIGINS:
                raise ValueError("Set CORS_ORIGINS to explicit origins in production")
            if self.DEEPSEEK_ENABLED and not self.DEEPSEEK_API_KEY.strip():
                raise ValueError("DEEPSEEK_API_KEY is required when cloud fallback is enabled")
        return self

settings = Settings()
