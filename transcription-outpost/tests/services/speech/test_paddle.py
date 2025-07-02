import asyncio
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.models import TranscriptionRequest
from app.services.speech import PaddleSpeechService, SpeechServiceFactory, SpeechServiceType


@pytest.fixture
async def speech_service():
    """Fixture for creating a speech service instance"""
    service = PaddleSpeechService()
    with patch("paddlespeech.cli.asr.infer.ASRExecutor") as mock_executor, \
         patch("paddlespeech.server.engine.asr.online.asr_engine.PaddleASRConnectionHandler") as mock_handler:
        
        # Configure mocks
        mock_executor.return_value = MagicMock()
        mock_handler.return_value = AsyncMock()
        
        # Initialize service
        await service.initialize()
        yield service
        await service.cleanup()


@pytest.mark.asyncio
async def test_transcribe_file(speech_service, tmp_path):
    """Test file-based transcription"""
    # Create a dummy audio file
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"dummy audio data")
    
    # Configure mock response
    speech_service.asr_executor.return_value = {
        "text": "Hello world",
        "confidence": 0.95
    }
    
    # Test transcription
    request = TranscriptionRequest(audio_format="wav", language="en")
    text, confidence = await speech_service.transcribe_file(audio_file, request)
    
    assert text == "Hello world"
    assert confidence == 0.95
    speech_service.asr_executor.assert_called_once_with(str(audio_file), "en")


@pytest.mark.asyncio
async def test_transcribe_stream(speech_service):
    """Test streaming transcription"""
    # Mock stream handler responses
    speech_service.stream_handler.process_chunk.side_effect = [
        {"text": "Hello", "confidence": 0.9},
        {"text": "world", "confidence": 0.85},
        None,  # No result for last chunk
    ]
    
    # Create async iterator for audio chunks
    async def audio_stream():
        chunks = [b"chunk1", b"chunk2", b"chunk3"]
        for chunk in chunks:
            yield chunk
    
    # Test streaming
    request = TranscriptionRequest(audio_format="wav", language="en", stream=True)
    results = []
    async for text, confidence in speech_service.transcribe_stream(audio_stream(), request):
        results.append((text, confidence))
    
    assert len(results) == 2
    assert results[0] == ("Hello", 0.9)
    assert results[1] == ("world", 0.85)
    
    # Verify stream handler was used correctly
    assert speech_service.stream_handler.initialize_connection.called
    assert speech_service.stream_handler.process_chunk.call_count == 3
    assert speech_service.stream_handler.finalize_connection.called


@pytest.mark.asyncio
async def test_factory_singleton():
    """Test that factory returns singleton instances"""
    service1 = await SpeechServiceFactory.get_service(SpeechServiceType.PADDLE)
    service2 = await SpeechServiceFactory.get_service(SpeechServiceType.PADDLE)
    assert service1 is service2
    
    # Cleanup
    await SpeechServiceFactory.cleanup()


@pytest.mark.asyncio
async def test_factory_unknown_type():
    """Test factory with unknown service type"""
    with pytest.raises(ValueError):
        await SpeechServiceFactory.get_service("unknown") 