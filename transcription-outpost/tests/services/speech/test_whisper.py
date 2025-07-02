import asyncio
from pathlib import Path
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np

from app.core.models import TranscriptionRequest
from app.services.speech import WhisperService, SpeechServiceFactory, SpeechServiceType


@pytest_asyncio.fixture
async def speech_service():
    """Fixture for creating a speech service instance"""
    service = WhisperService(model_name="tiny")  # Use tiny model for faster tests
    with patch("whisper.load_model") as mock_model:
        # Configure mocks
        mock_whisper = MagicMock()
        mock_whisper.transcribe.return_value = {
            "text": "Hello world",
            "segments": [{"text": "Hello world", "start": 0, "end": 1}]
        }
        mock_model.return_value = mock_whisper
        
        # Initialize service
        await service.initialize()
        yield service
        await service.cleanup()


@pytest.mark.asyncio
async def test_transcribe_file(speech_service: WhisperService, tmp_path):
    """Test file-based transcription"""
    # Create a dummy audio file
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"dummy audio data")
    
    # Test transcription
    request = TranscriptionRequest(audio_format="wav", language="en")
    text, confidence = await speech_service.transcribe_file(audio_file, request)
    
    assert text == "Hello world"
    assert confidence == 1.0
    speech_service.model.transcribe.assert_called_once_with(
        str(audio_file),
        language="en",
        fp16=False
    )


@pytest.mark.asyncio
async def test_transcribe_stream(speech_service: WhisperService):
    """Test streaming transcription"""
    # Create async iterator for audio chunks
    async def audio_stream():
        # Create 1 second of silence at 16kHz
        samples = np.zeros(16000, dtype=np.float32)
        yield samples.tobytes()
    
    # Test streaming
    request = TranscriptionRequest(audio_format="wav", language="en", stream=True)
    results = []
    async for text, confidence in speech_service.transcribe_stream(audio_stream(), request):
        results.append((text, confidence))
    
    assert len(results) == 1  # Only one result since we're using a mock
    assert results[0] == ("Hello world", 1.0)


@pytest.mark.asyncio
async def test_factory_singleton():
    """Test that factory returns singleton instances"""
    service1 = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
    service2 = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
    assert service1 is service2
    
    # Cleanup
    await SpeechServiceFactory.cleanup()


@pytest.mark.asyncio
async def test_factory_unknown_type():
    """Test factory with unknown service type"""
    with pytest.raises(ValueError):
        await SpeechServiceFactory.get_service("unknown") 