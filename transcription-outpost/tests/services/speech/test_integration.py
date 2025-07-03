import pytest
from pathlib import Path

from app.core.models import TranscriptionRequest
from app.services.speech import SpeechServiceFactory, SpeechServiceType


@pytest.mark.integration
@pytest.mark.asyncio
async def test_whisper_integration(test_data_dir):
    """Integration test for Whisper service"""
    # Initialize service
    service = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
    
    try:
        # Test file transcription
        audio_path = test_data_dir / "simple.wav"  # Use existing test file
        
        # Only run if test file exists
        if audio_path.exists():
            with open(audio_path, "rb") as f:
                content = f.read()
            
            result = await service.transcribe(content, "wav")
            
            # Basic validation
            assert hasattr(result, 'text')
            assert hasattr(result, 'confidence') 
            assert isinstance(result.text, str)
            assert len(result.text) > 0
            assert 0 <= result.confidence <= 1.0
            
            print(f"Transcription result: {result.text} (confidence: {result.confidence})")
        else:
            print("Test audio file not found, skipping integration test")
    
    finally:
        # Cleanup
        await SpeechServiceFactory.cleanup() 