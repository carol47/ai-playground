#!/usr/bin/env python3
"""Simple transcription test script with detailed output"""

import requests
import time
import sys

def test_transcription():
    print("🎯 Testing FastAPI Transcription Endpoints")
    print("=" * 50)
    
    # Test health first
    try:
        print("1. Testing health endpoint...")
        health_response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"   ✅ Health: {health_response.status_code} - {health_response.json()}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test models endpoint
    try:
        print("2. Testing models endpoint...")
        models_response = requests.get('http://localhost:8000/api/v1/transcription/models', timeout=5)
        print(f"   ✅ Models: {models_response.status_code} - {models_response.json()}")
    except Exception as e:
        print(f"   ❌ Models check failed: {e}")
    
    # Test transcription
    print("3. Testing transcription...")
    test_file = 'tests/data/simple.wav'
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('simple.wav', f, 'audio/wav')}
            print(f"   📤 Sending {test_file} for transcription...")
            
            start_time = time.time()
            response = requests.post('http://localhost:8000/api/v1/transcription/', files=files, timeout=60)
            end_time = time.time()
            
            print(f"   ⏱️  Request took {end_time - start_time:.2f} seconds")
            print(f"   📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("   🎉 SUCCESS! Transcription completed!")
                print(f"   📝 Text: \"{result['text']}\"")
                print(f"   📈 Confidence: {result['confidence']:.3f}")
                print(f"   🌍 Language: {result.get('language', 'N/A')}")
                print(f"   🤖 Model: {result.get('model', 'N/A')}")
                print(f"   ⏰ Duration: {result.get('duration', 'N/A')}s")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
    except FileNotFoundError:
        print(f"   ❌ Test file not found: {test_file}")
    except requests.Timeout:
        print("   ⏰ Request timed out - transcription might be taking too long")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")

if __name__ == "__main__":
    test_transcription() 