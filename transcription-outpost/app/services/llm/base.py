from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class LLMResult(BaseModel):
    """Model for LLM results"""
    text: str
    confidence: Optional[float] = None
    model: str
    metadata: Dict[str, Any] = {}


class BaseLLMService(ABC):
    """Base class for Language Model services"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the LLM service and load models"""
        pass

    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response to a prompt
        
        Args:
            prompt: Input prompt text
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    async def process_transcription(self, transcription: str) -> Dict[str, str]:
        """
        Process a transcription through LLM chains
        
        Args:
            transcription: Raw transcription text
            
        Returns:
            Dictionary with processed results
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass 