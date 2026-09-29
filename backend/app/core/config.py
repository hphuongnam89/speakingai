from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "IELTS Speaking AI Coach"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "ornith-1.5:9b"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_ENABLED: bool = False
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DATABASE_URL: str = "sqlite:///./data/app.db"
    WHISPER_MODEL: str = "base.en"
    AUDIO_DIR: str = "./data/audio"
    LLM_TIMEOUT: int = 120
    OLLAMA_TIMEOUT: float = 30.0
    DEEPSEEK_TIMEOUT: float = 30.0
    MODEL_ROUTING_PREFERENCE: str = "auto"  # auto, local_only, cloud_only
    
    # Production & Security
    API_KEY: str = ""
    API_KEY_ENABLED: bool = False
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 120
    CORS_ORIGINS: str = "*"
    ENVIRONMENT: str = "development"
    ENABLE_SECURITY_HEADERS: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
