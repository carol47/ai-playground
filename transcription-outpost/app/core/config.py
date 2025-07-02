from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2:13b-chat"
    OLLAMA_TIMEOUT: float = 30.0
    
    # Hardware Configuration
    USE_GPU: bool = True
    CUDA_DEVICE: str = "cuda:0"
    
    class Config:
        env_file = ".env"

settings = Settings() 