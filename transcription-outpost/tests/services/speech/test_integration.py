import pytest
from pathlib import Path

from app.core.models import TranscriptionRequest
from app.services.speech import SpeechServiceFactory, SpeechServiceType


@pytest.mark.integration
@pytest.mark.asyncio
async def test_paddle_integration(test_data_dir):
    """Integration test for PaddleSpeech service"""
    # Initialize service
    service = await SpeechServiceFactory.get_service(SpeechServiceType.PADDLE)
    
    try:
        # Test file transcription
        audio_path = test_data_dir / "test.wav"
        request = TranscriptionRequest(audio_format="wav", language="en")
        
        # Only run if test file exists
        if audio_path.exists():
            text, confidence = await service.transcribe_file(audio_path, request)
            
            # Basic validation
            assert isinstance(text, str)
            assert len(text) > 0
            assert 0 <= confidence <= 1.0
            
            print(f"Transcription result: {text} (confidence: {confidence})")
    
    finally:
        # Cleanup
        await SpeechServiceFactory.cleanup() 