"""Script to generate test audio files for transcription testing."""
import os
from pathlib import Path
import pyttsx3
import soundfile as sf
import numpy as np

def generate_tts_audio(text: str, output_path: Path, sample_rate: int = 16000) -> None:
    """
    Generate a WAV file from text using text-to-speech.
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the WAV file
        sample_rate: Sample rate in Hz (default: 16kHz for Whisper)
    """
    # Initialize the TTS engine
    engine = pyttsx3.init()
    
    # Configure the engine
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to a temporary file first (pyttsx3 only supports basic wav format)
    temp_path = output_path.with_name('temp_' + output_path.name)
    engine.save_to_file(text, str(temp_path))
    engine.runAndWait()
    
    # Read the temporary file and resample to desired sample rate
    data, orig_sr = sf.read(temp_path)
    
    # Convert to mono if stereo
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    # Normalize audio
    data = data / np.abs(data).max()
    
    # Save with desired sample rate
    sf.write(output_path, data, sample_rate)
    
    # Clean up temporary file
    temp_path.unlink()

def main():
    # Create test directory
    test_dir = Path(__file__).parent.parent / 'tests' / 'data'
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate test files with different content
    test_files = [
        ('simple.wav', 'Hello world, this is a test of the transcription service.'),
        ('numbers.wav', 'The numbers are one, two, three, four, five.'),
        ('quote.wav', 'To be, or not to be, that is the question.')
    ]
    
    for filename, text in test_files:
        output_path = test_dir / filename
        print(f'Generating {output_path}...')
        generate_tts_audio(text, output_path)
        print(f'Generated {output_path}')

if __name__ == '__main__':
    main() 