"""Script to test the Whisper transcription service."""
import asyncio
import os
from pathlib import Path

from app.core.models import TranscriptionRequest
from app.services.speech import SpeechServiceFactory, SpeechServiceType


async def test_transcription(audio_file_path: str | None = None):
    """Test transcription of audio files."""
    # Initialize the service
    service = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
    
    try:
        # Test the converted WAV file
        audio_path = Path(__file__).resolve().parent.parent / 'tests' / 'data' / 'converted.wav'
        if not audio_path.exists():
            print(f"Error: File not found: {audio_path}")
            return
            
        print(f"\nTranscribing {audio_path.name}...")
        print(f"Full path: {audio_path}")
        request = TranscriptionRequest(audio_format="wav", language="en")
        
        try:
            text, confidence = await service.transcribe_file(audio_path, request)
            print(f"Transcription: {text}")
            print(f"Confidence: {confidence:.2f}")
        except Exception as e:
            print(f"Error transcribing {audio_path.name}: {e}")
            print("File exists:", audio_path.exists())
            print("File size:", audio_path.stat().st_size if audio_path.exists() else "N/A")
    
    finally:
        # Cleanup
        await SpeechServiceFactory.cleanup()

if __name__ == '__main__':
    asyncio.run(test_transcription()) 