from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from pathlib import Path
from pydantic import BaseModel

from ...core.models import TranscriptionRequest


class AudioTranscriptionResult(BaseModel):
    """Model for transcription results"""
    text: str
    confidence: float
    duration: Optional[float] = None
    language: Optional[str] = None
    model: str


class BaseSpeechService(ABC):
    """Base class for speech-to-text services"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the speech service and load models"""
        pass

    @abstractmethod
    async def transcribe(self, content: bytes, file_ext: str) -> AudioTranscriptionResult:
        """
        Transcribe audio content
        
        Args:
            content: Raw audio bytes
            file_ext: Audio file extension (e.g. 'wav', 'mp3')
            
        Returns:
            AudioTranscriptionResult containing transcription and metadata
        """
        pass

    @abstractmethod
    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], request: TranscriptionRequest
    ) -> AsyncIterator[AudioTranscriptionResult]:
        """
        Transcribe an audio stream
        
        Args:
            audio_stream: Async iterator of audio chunks
            request: Transcription request parameters
            
        Returns:
            Async iterator of AudioTranscriptionResult
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass 