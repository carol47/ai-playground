import asyncio
from pathlib import Path
from typing import AsyncIterator, Optional
import tempfile

import numpy as np
import soundfile as sf
from paddlespeech.cli.asr.infer import ASRExecutor
from paddlespeech.server.engine.asr.online.asr_engine import PaddleASRConnectionHandler

from ....core.logger import log
from ....core.models import TranscriptionRequest
from ..base import BaseSpeechService


class PaddleSpeechService(BaseSpeechService):
    """PaddleSpeech-based speech-to-text service"""

    def __init__(self):
        self.asr_executor: Optional[ASRExecutor] = None
        self.stream_handler: Optional[PaddleASRConnectionHandler] = None

    async def initialize(self) -> None:
        """Initialize PaddleSpeech ASR models"""
        log.info("Initializing PaddleSpeech ASR service")
        # Initialize in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        self.asr_executor = await loop.run_in_executor(None, ASRExecutor)
        self.stream_handler = PaddleASRConnectionHandler()
        log.info("PaddleSpeech ASR service initialized")

    async def transcribe_file(
        self, audio_path: Path, request: TranscriptionRequest
    ) -> tuple[str, float]:
        """
        Transcribe an audio file using PaddleSpeech
        
        Args:
            audio_path: Path to the audio file
            request: Transcription request parameters
            
        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        if not self.asr_executor:
            raise RuntimeError("PaddleSpeech ASR service not initialized")

        # Run transcription in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.asr_executor,
            str(audio_path),
            request.language
        )

        # PaddleSpeech returns a dict with text and other metadata
        text = result.get("text", "")
        confidence = result.get("confidence", 0.0)

        return text, confidence

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], request: TranscriptionRequest
    ) -> AsyncIterator[tuple[str, float]]:
        """
        Transcribe an audio stream using PaddleSpeech
        
        Args:
            audio_stream: Async iterator of audio chunks
            request: Transcription request parameters
            
        Returns:
            Async iterator of (transcribed_text, confidence_score) tuples
        """
        if not self.stream_handler:
            raise RuntimeError("PaddleSpeech ASR service not initialized")

        # Initialize stream
        await self.stream_handler.initialize_connection()

        try:
            async for chunk in audio_stream:
                # Convert bytes to numpy array
                with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
                    temp_file.write(chunk)
                    temp_file.flush()
                    audio_data, sample_rate = sf.read(temp_file.name)

                # Process chunk
                result = await self.stream_handler.process_chunk(audio_data)
                if result and result.get("text"):
                    yield result["text"], result.get("confidence", 0.0)

        finally:
            # Cleanup stream
            await self.stream_handler.finalize_connection()

    async def cleanup(self) -> None:
        """Cleanup PaddleSpeech resources"""
        if self.stream_handler:
            await self.stream_handler.finalize_connection()
        self.asr_executor = None
        self.stream_handler = None
        log.info("PaddleSpeech ASR service cleaned up") 