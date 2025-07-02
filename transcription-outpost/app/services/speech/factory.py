from enum import Enum
from typing import Optional

from ...core.logger import log
from .base import BaseSpeechService
from .whisper import WhisperService


class SpeechServiceType(str, Enum):
    """Available speech service types"""
    WHISPER = "whisper"
    # Add more service types here as we implement them


class SpeechServiceFactory:
    """Factory for creating and managing speech services"""
    
    _instance: Optional[BaseSpeechService] = None
    
    @classmethod
    async def get_service(
        cls, service_type: SpeechServiceType = SpeechServiceType.WHISPER
    ) -> BaseSpeechService:
        """
        Get or create a speech service instance
        
        Args:
            service_type: Type of speech service to create
            
        Returns:
            Speech service instance
        """
        if cls._instance is None:
            cls._instance = cls._create_service(service_type)
            await cls._instance.initialize()
            
        return cls._instance
    
    @classmethod
    def _create_service(cls, service_type: SpeechServiceType) -> BaseSpeechService:
        """Create a new speech service instance"""
        if service_type == SpeechServiceType.WHISPER:
            log.info("Creating Whisper service")
            return WhisperService(model_name="base")
        else:
            raise ValueError(f"Unknown speech service type: {service_type}")
    
    @classmethod
    async def cleanup(cls) -> None:
        """Cleanup the current speech service instance"""
        if cls._instance:
            await cls._instance.cleanup()
            cls._instance = None 