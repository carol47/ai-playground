import io
import tempfile
from pathlib import Path
from typing import AsyncIterator, Optional
import whisper
import numpy as np
from pydub import AudioSegment
import pydub.utils
import os

from ....core.config import settings
from ....core.logger import log
from ....core.models import TranscriptionRequest
from ..base import BaseSpeechService, AudioTranscriptionResult


# Configure ffmpeg path for both pydub and whisper
ffmpeg_dir = os.path.join(
    os.environ.get('LOCALAPPDATA', ''),
    'Microsoft',
    'WinGet',
    'Packages',
    'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe',
    'ffmpeg-7.1.1-full_build',
    'bin'
)
ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')

if os.path.exists(ffmpeg_path):
    # Configure pydub
    pydub.AudioSegment.converter = ffmpeg_path
    pydub.AudioSegment.ffmpeg = ffmpeg_path
    pydub.AudioSegment.ffprobe = ffmpeg_path.replace('ffmpeg.exe', 'ffprobe.exe')
    
    # Add FFmpeg to PATH so Whisper can find it
    if ffmpeg_dir not in os.environ.get('PATH', ''):
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
        
    # Also try to configure whisper directly if possible
    try:
        import whisper
        if hasattr(whisper.audio, 'SAMPLE_RATE'):
            # Set the ffmpeg command that whisper will use
            os.environ['FFMPEG_PATH'] = ffmpeg_path
    except:
        pass


class WhisperService(BaseSpeechService):
    """Whisper-based speech-to-text service"""
    
    def __init__(self):
        self.model = None
        self.model_name = "base"  # Can be tiny, base, small, medium, large
        
    async def initialize(self) -> None:
        """Initialize Whisper model"""
        if self.model is None:
            log.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            log.info("Whisper model loaded successfully")
    
    async def transcribe(self, content: bytes, file_ext: str) -> AudioTranscriptionResult:
        """Transcribe audio content using Whisper"""
        await self.initialize()
        
        # Convert audio to WAV format if needed
        if file_ext != "wav":
            audio = AudioSegment.from_file(io.BytesIO(content), format=file_ext)
            wav_data = io.BytesIO()
            audio.export(wav_data, format="wav")
            content = wav_data.getvalue()
        
        # Create temporary file for Whisper with explicit deletion handling
        import tempfile
        import os
        
        temp_file = None
        try:
            # Create temporary file with delete=False to ensure it exists during transcription
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file.write(content)
            temp_file.flush()
            temp_file.close()  # Close the file so Whisper can access it
            
            # Perform transcription
            result = self.model.transcribe(
                temp_file.name,
                language=None,  # Auto-detect language
                fp16=False  # Use float32 for CPU-only setup
            )
            
            # Calculate average confidence from segments if available
            segments = result.get("segments", [])
            avg_confidence = 0.0
            if segments:
                confidences = [seg.get("no_speech_prob", 0.0) for seg in segments]
                avg_confidence = 1.0 - (sum(confidences) / len(confidences)) if confidences else 0.0
            
            return AudioTranscriptionResult(
                text=result["text"].strip(),
                confidence=avg_confidence,
                duration=float(result.get("duration", 0.0)),
                language=result.get("language"),
                model=f"whisper-{self.model_name}"
            )
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except OSError:
                    pass  # File might already be deleted
    
    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], request: TranscriptionRequest
    ) -> AsyncIterator[AudioTranscriptionResult]:
        """
        Stream transcription is not yet supported by Whisper
        This is a placeholder for future implementation
        """
        raise NotImplementedError("Streaming transcription not yet supported by Whisper")
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        # Whisper doesn't require explicit cleanup
        pass 