import asyncio
from pathlib import Path
from typing import AsyncIterator, Optional, Callable
import tempfile
import functools

import numpy as np
import soundfile as sf
import whisper
from whisper.utils import get_writer

from ...core.logger import log
from ...core.models import TranscriptionRequest
from .base import BaseSpeechService


class WhisperService(BaseSpeechService):
    """Whisper-based speech-to-text service"""

    def __init__(self, model_name: str = "base"):
        """
        Initialize WhisperService
        
        Args:
            model_name: Whisper model to use ("tiny", "base", "small", "medium", "large")
        """
        self.model: Optional[whisper.Whisper] = None
        self.model_name = model_name
        self.sample_rate = 16000  # Whisper expects 16kHz audio

    async def initialize(self) -> None:
        """Initialize Whisper model"""
        log.info(f"Initializing Whisper model: {self.model_name}")
        # Initialize in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(None, whisper.load_model, self.model_name)
        log.info("Whisper model initialized")

    async def transcribe_file(
        self, audio_path: Path, request: TranscriptionRequest
    ) -> tuple[str, float]:
        """
        Transcribe an audio file using Whisper
        
        Args:
            audio_path: Path to the audio file
            request: Transcription request parameters
            
        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        if not self.model:
            raise RuntimeError("Whisper model not initialized")

        # Create a partial function with the keyword arguments
        transcribe_func = functools.partial(
            self.model.transcribe,
            str(audio_path),
            language=request.language if request.language != "auto" else None,
            fp16=False  # Use FP32 for better compatibility
        )

        # Run transcription in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, transcribe_func)

        # Whisper returns a dict with text and other metadata
        text = result.get("text", "").strip()
        # Whisper doesn't provide confidence scores, so we'll use 1.0 for now
        confidence = 1.0

        return text, confidence

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], request: TranscriptionRequest
    ) -> AsyncIterator[tuple[str, float]]:
        """
        Transcribe an audio stream using Whisper
        
        Args:
            audio_stream: Async iterator of audio chunks
            request: Transcription request parameters
            
        Returns:
            Async iterator of (transcribed_text, confidence_score) tuples
        """
        if not self.model:
            raise RuntimeError("Whisper model not initialized")

        # Buffer for accumulating audio data
        buffer = np.array([], dtype=np.float32)
        min_samples = self.sample_rate  # 1 second of audio at 16kHz

        async for chunk in audio_stream:
            try:
                # Convert bytes to numpy array (assuming float32 PCM)
                chunk_data = np.frombuffer(chunk, dtype=np.float32)
                buffer = np.concatenate([buffer, chunk_data])
                
                # Process when we have enough data
                if len(buffer) >= min_samples:
                    # Create a partial function with the keyword arguments
                    transcribe_func = functools.partial(
                        self.model.transcribe,
                        buffer,
                        language=request.language if request.language != "auto" else None,
                        fp16=False
                    )

                    # Run transcription in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, transcribe_func)

                    text = result.get("text", "").strip()
                    if text:
                        yield text, 1.0

                    # Clear buffer
                    buffer = np.array([], dtype=np.float32)

            except Exception as e:
                log.error(f"Error processing audio chunk: {e}")

        # Process any remaining audio
        if len(buffer) > 0:
            try:
                # Create a partial function with the keyword arguments
                transcribe_func = functools.partial(
                    self.model.transcribe,
                    buffer,
                    language=request.language if request.language != "auto" else None,
                    fp16=False
                )

                # Run transcription in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, transcribe_func)

                text = result.get("text", "").strip()
                if text:
                    yield text, 1.0

            except Exception as e:
                log.error(f"Error processing final audio chunk: {e}")

    async def cleanup(self) -> None:
        """Cleanup Whisper resources"""
        self.model = None
        log.info("Whisper service cleaned up") 