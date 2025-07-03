"""Speech-to-text service providers"""

from .whisper import WhisperService
# from .paddle import PaddleSpeechService  # Disabled until paddlespeech is installed

__all__ = ["WhisperService"] 