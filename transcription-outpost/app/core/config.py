from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings for environment variable loading"""
    
    # App Config
    APP_NAME: str = "Transcription Outpost"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Model Paths
    LLAMA_MODEL_PATH: str = "models/llama-2-13b-chat.gguf"
    
    # Audio Config
    MAX_AUDIO_SIZE_MB: int = 25
    SUPPORTED_AUDIO_FORMATS: list[str] = ["wav", "mp3", "m4a", "ogg", "webm"]
    SAMPLE_RATE: int = 16000
    
    # WebSocket Config
    WS_PING_INTERVAL: int = 30  # seconds
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global Settings Instance
settings = get_settings() 