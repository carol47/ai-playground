import os
from pathlib import Path
from pydub import AudioSegment
import pydub.utils

def configure_ffmpeg():
    """Configure ffmpeg path for audio processing"""
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
    
    if not Path(ffmpeg_path).exists():
        raise RuntimeError(
            f"FFmpeg not found at {ffmpeg_path}. Please ensure FFmpeg is installed via winget install Gyan.FFmpeg"
        )
    
    pydub.AudioSegment.converter = ffmpeg_path
    return ffmpeg_path 