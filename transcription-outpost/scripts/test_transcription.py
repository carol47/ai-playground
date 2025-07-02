"""Script to test the Whisper transcription service."""
import asyncio
import os
from pathlib import Path
import httpx
from pydub import AudioSegment
import pydub.utils

from app.core.models import TranscriptionRequest
from app.services.speech import SpeechServiceFactory, SpeechServiceType

# Configure ffmpeg path
ffmpeg_path = os.path.join(
    os.environ.get('LOCALAPPDATA', ''),
    'Microsoft',
    'WinGet',
    'Packages',
    'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe',
    'ffmpeg-7.1.1-full_build',
    'bin',
    'ffmpeg.exe'
)
pydub.AudioSegment.converter = ffmpeg_path

async def test_transcription():
    """Test the transcription endpoint with our test audio files"""
    # Get the path to the test files relative to this script
    script_dir = Path(__file__).resolve().parent.parent
    test_files = [
        script_dir / "tests/data/simple.wav",
        script_dir / "tests/data/quote.wav",
        script_dir / "tests/data/numbers.wav"
    ]
    
    async with httpx.AsyncClient() as client:
        for test_file in test_files:
            if not test_file.exists():
                print(f"Skipping {test_file} - file not found")
                continue
                
            print(f"\nTesting transcription with {test_file.name}")
            
            # Prepare the file upload
            with open(test_file, "rb") as f:
                files = {"file": (test_file.name, f, "audio/wav")}
                
                try:
                    # Make the request
                    response = await client.post(
                        "http://localhost:8000/api/v1/transcription/",
                        files=files,
                        follow_redirects=True
                    )
                    
                    # Check response
                    if response.status_code == 200:
                        result = response.json()
                        print(f"Transcription successful!")
                        print(f"Text: {result['text']}")
                        print(f"Confidence: {result['confidence']}")
                        print(f"Language: {result.get('language', 'not detected')}")
                        print(f"Duration: {result.get('duration', 'not available')}s")
                    else:
                        print(f"Error: {response.status_code}")
                        print(response.text)
                        
                except Exception as e:
                    print(f"Error testing {test_file}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_transcription()) 