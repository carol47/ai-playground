from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from pathlib import Path

from ...core.models import TranscriptionRequest


class BaseSpeechService(ABC):
    """Base class for speech-to-text services"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the speech service and load models"""
        pass

    @abstractmethod
    async def transcribe_file(
        self, audio_path: Path, request: TranscriptionRequest
    ) -> tuple[str, float]:
        """
        Transcribe an audio file
        
        Args:
            audio_path: Path to the audio file
            request: Transcription request parameters
            
        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        pass

    @abstractmethod
    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], request: TranscriptionRequest
    ) -> AsyncIterator[tuple[str, float]]:
        """
        Transcribe an audio stream
        
        Args:
            audio_stream: Async iterator of audio chunks
            request: Transcription request parameters
            
        Returns:
            Async iterator of (transcribed_text, confidence_score) tuples
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass 