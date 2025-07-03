from enum import Enum
from typing import Optional

from ...core.logger import log
from .base import BaseLLMService


class LLMServiceType(str, Enum):
    """Available LLM service types"""
    LLAMA = "llama"
    # Add more service types here as we implement them


class LLMServiceFactory:
    """Factory for creating and managing LLM services"""
    
    _instance: Optional[BaseLLMService] = None
    
    @classmethod
    async def get_service(
        cls, service_type: LLMServiceType = LLMServiceType.LLAMA
    ) -> BaseLLMService:
        """
        Get or create an LLM service instance
        
        Args:
            service_type: Type of LLM service to create
            
        Returns:
            LLM service instance
        """
        if cls._instance is None:
            cls._instance = cls._create_service(service_type)
            await cls._instance.initialize()
            
        return cls._instance
    
    @classmethod
    def _create_service(cls, service_type: LLMServiceType) -> BaseLLMService:
        """Create a new LLM service instance"""
        if service_type == LLMServiceType.LLAMA:
            log.info("Creating LLaMA service")
            from .providers.llama import LlamaService
            return LlamaService()
        else:
            raise ValueError(f"Unknown LLM service type: {service_type}")
    
    @classmethod
    async def cleanup(cls) -> None:
        """Cleanup the current LLM service instance"""
        if cls._instance:
            await cls._instance.cleanup()
            cls._instance = None


# Expose factory method at module level
async def get_llm_service(
    service_type: LLMServiceType = LLMServiceType.LLAMA
) -> BaseLLMService:
    """Get an LLM service instance"""
    return await LLMServiceFactory.get_service(service_type) 