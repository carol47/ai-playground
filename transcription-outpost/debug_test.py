#!/usr/bin/env python3
"""Direct WhisperService test to debug transcription issues"""

import asyncio
import os
from pathlib import Path

# Add the app directory to the Python path
import sys
sys.path.append('.')

from app.services.speech.whisper import WhisperService

async def test_whisper_directly():
    print("🔍 Direct WhisperService Test")
    print("=" * 40)
    
    # Test file path
    test_file = Path("tests/data/simple.wav")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📁 Test file: {test_file} ({test_file.stat().st_size} bytes)")
    
    try:
        # Create WhisperService instance
        print("🤖 Creating WhisperService...")
        whisper_service = WhisperService()
        
        # Initialize the service
        print("⚡ Initializing Whisper model...")
        await whisper_service.initialize()
        print("✅ Whisper model initialized successfully!")
        
        # Read test file
        print("📖 Reading test file...")
        with open(test_file, 'rb') as f:
            content = f.read()
        
        print(f"📊 File content size: {len(content)} bytes")
        
        # Perform transcription
        print("🎙️  Starting transcription...")
        result = await whisper_service.transcribe(content, "wav")
        
        print("🎉 SUCCESS! Direct transcription worked!")
        print(f"📝 Text: \"{result.text}\"")
        print(f"📈 Confidence: {result.confidence:.3f}")
        print(f"🌍 Language: {result.language}")
        print(f"🤖 Model: {result.model}")
        print(f"⏰ Duration: {result.duration}s")
        
    except Exception as e:
        print(f"❌ Error during direct test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_whisper_directly()) 