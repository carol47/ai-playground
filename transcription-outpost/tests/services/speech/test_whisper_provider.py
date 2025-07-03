import io
import tempfile
from pathlib import Path
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np

from app.core.models import TranscriptionRequest
from app.services.speech.providers.whisper import WhisperService
from app.services.speech.factory import SpeechServiceFactory, SpeechServiceType
from app.services.speech.base import AudioTranscriptionResult


@pytest_asyncio.fixture
async def whisper_service():
    """Fixture for creating a whisper service instance"""
    service = WhisperService()
    with patch("whisper.load_model") as mock_model:
        # Configure mocks
        mock_whisper = MagicMock()
        mock_whisper.transcribe.return_value = {
            "text": "Hello world",
            "segments": [{"text": "Hello world", "start": 0, "end": 1, "no_speech_prob": 0.1}],
            "duration": 2.0,
            "language": "en"
        }
        mock_model.return_value = mock_whisper
        
        # Initialize service
        await service.initialize()
        yield service
        await service.cleanup()


@pytest.mark.asyncio
class TestWhisperProvider:
    """Test Whisper provider functionality"""
    
    async def test_provider_initialization(self):
        """Test provider initializes correctly"""
        service = WhisperService()
        
        assert service.model_name == "base"
        assert service.model is None  # Not initialized yet
    
    async def test_provider_initialization_loads_model(self):
        """Test provider loads model on initialization"""
        service = WhisperService()
        
        with patch("whisper.load_model") as mock_model:
            mock_whisper = MagicMock()
            mock_model.return_value = mock_whisper
            
            await service.initialize()
            
            assert service.model is not None
            mock_model.assert_called_once_with("base")
    
    async def test_transcribe_audio_content(self, whisper_service: WhisperService):
        """Test transcription with audio content"""
        # Create dummy audio content
        audio_content = b"dummy audio data"
        
        # Mock temporary file creation
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_temp.return_value.__enter__.return_value = mock_file
            mock_temp.return_value = mock_file
            
            with patch("os.path.exists", return_value=True), \
                 patch("os.unlink") as mock_unlink:
                
                result = await whisper_service.transcribe(audio_content, "wav")
                
                assert isinstance(result, AudioTranscriptionResult)
                assert result.text == "Hello world"
                assert result.confidence == 0.9  # 1.0 - 0.1 (no_speech_prob)
                assert result.duration == 2.0
                assert result.language == "en"
                assert result.model == "whisper-base"
                
                # Verify model was called
                whisper_service.model.transcribe.assert_called_once()
    
    async def test_transcribe_with_audio_conversion(self, whisper_service: WhisperService):
        """Test transcription with audio format conversion"""
        # Create dummy MP3 content
        audio_content = b"dummy mp3 data"
        
        with patch("pydub.AudioSegment.from_file") as mock_from_file, \
             patch("tempfile.NamedTemporaryFile") as mock_temp:
            
            # Mock AudioSegment conversion
            mock_audio = MagicMock()
            mock_from_file.return_value = mock_audio
            mock_audio.export.return_value = None
            
            # Mock temporary file
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_temp.return_value = mock_file
            
            with patch("os.path.exists", return_value=True), \
                 patch("os.unlink"):
                
                result = await whisper_service.transcribe(audio_content, "mp3")
                
                assert isinstance(result, AudioTranscriptionResult)
                assert result.text == "Hello world"
                
                # Verify conversion was attempted
                mock_from_file.assert_called_once()
                mock_audio.export.assert_called_once()
    
    async def test_transcribe_stream_not_implemented(self, whisper_service: WhisperService):
        """Test that streaming transcription raises NotImplementedError"""
        async def dummy_stream():
            yield b"audio chunk"
        
        request = TranscriptionRequest(audio_format="wav", language="en", stream=True)
        
        # The method raises NotImplementedError immediately when called
        with pytest.raises(NotImplementedError, match="Streaming transcription not yet supported"):
            await whisper_service.transcribe_stream(dummy_stream(), request)
    
    async def test_transcribe_confidence_calculation(self, whisper_service: WhisperService):
        """Test confidence calculation from segments"""
        # Mock whisper result with multiple segments
        whisper_service.model.transcribe.return_value = {
            "text": "Hello world test",
            "segments": [
                {"text": "Hello", "start": 0, "end": 0.5, "no_speech_prob": 0.1},
                {"text": " world", "start": 0.5, "end": 1.0, "no_speech_prob": 0.2},
                {"text": " test", "start": 1.0, "end": 1.5, "no_speech_prob": 0.05}
            ],
            "duration": 1.5,
            "language": "en"
        }
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_temp.return_value = mock_file
            
            with patch("os.path.exists", return_value=True), \
                 patch("os.unlink"):
                
                result = await whisper_service.transcribe(b"dummy audio", "wav")
                
                # Expected confidence: 1.0 - (0.1 + 0.2 + 0.05) / 3 = 1.0 - 0.116... ≈ 0.883
                assert result.confidence == pytest.approx(0.883, rel=1e-2)
    
    async def test_transcribe_no_segments(self, whisper_service: WhisperService):
        """Test transcription with no segments"""
        whisper_service.model.transcribe.return_value = {
            "text": "Hello world",
            "segments": [],
            "duration": 1.0,
            "language": "en"
        }
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_temp.return_value = mock_file
            
            with patch("os.path.exists", return_value=True), \
                 patch("os.unlink"):
                
                result = await whisper_service.transcribe(b"dummy audio", "wav")
                
                assert result.confidence == 0.0  # No segments means 0 confidence
    
    async def test_transcribe_error_handling(self, whisper_service: WhisperService):
        """Test error handling in transcription"""
        whisper_service.model.transcribe.side_effect = Exception("Transcription failed")
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_temp.return_value = mock_file
            
            with patch("os.path.exists", return_value=True), \
                 patch("os.unlink"):
                
                with pytest.raises(Exception, match="Transcription failed"):
                    await whisper_service.transcribe(b"dummy audio", "wav")
    
    async def test_temporary_file_cleanup(self, whisper_service: WhisperService):
        """Test that temporary files are cleaned up"""
        with patch("tempfile.NamedTemporaryFile") as mock_temp, \
             patch("os.path.exists", return_value=True) as mock_exists, \
             patch("os.unlink") as mock_unlink:
            
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_temp.return_value = mock_file
            
            await whisper_service.transcribe(b"dummy audio", "wav")
            
            # Verify cleanup was attempted
            mock_unlink.assert_called_once_with("/tmp/test.wav")
    
    async def test_cleanup_method(self):
        """Test provider cleanup method"""
        service = WhisperService()
        
        # Cleanup should not raise any errors
        await service.cleanup()


@pytest.mark.asyncio
class TestWhisperProviderFactory:
    """Test Whisper provider through factory"""
    
    async def test_factory_creates_whisper_provider(self):
        """Test factory creates Whisper provider"""
        with patch("app.services.speech.factory.WhisperService") as mock_whisper:
            mock_instance = AsyncMock()
            mock_whisper.return_value = mock_instance
            
            service = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
            
            assert service is mock_instance
            mock_instance.initialize.assert_called_once()
            
            await SpeechServiceFactory.cleanup()
    
    async def test_factory_returns_same_instance(self):
        """Test factory returns same instance on multiple calls"""
        with patch("app.services.speech.factory.WhisperService") as mock_whisper:
            mock_instance = AsyncMock()
            mock_whisper.return_value = mock_instance
            
            service1 = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
            service2 = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
            
            assert service1 is service2
            assert mock_instance.initialize.call_count == 1
            
            await SpeechServiceFactory.cleanup()
    
    async def test_factory_cleanup_whisper(self):
        """Test factory cleanup for Whisper service"""
        with patch("app.services.speech.factory.WhisperService") as mock_whisper:
            mock_instance = AsyncMock()
            mock_whisper.return_value = mock_instance
            
            await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
            await SpeechServiceFactory.cleanup()
            
            mock_instance.cleanup.assert_called_once()
            assert SpeechServiceFactory._instance is None


@pytest.mark.asyncio 
class TestWhisperProviderIntegration:
    """Integration tests for Whisper provider"""
    
    async def test_ffmpeg_configuration(self):
        """Test that FFmpeg configuration is handled"""
        service = WhisperService()
        
        # This test verifies the service can be created without FFmpeg errors
        assert service is not None
        assert service.model_name == "base"
    
    async def test_model_loading_with_different_sizes(self):
        """Test that different model sizes can be configured"""
        service = WhisperService()
        
        # Test that model name can be changed
        service.model_name = "tiny"
        
        with patch("whisper.load_model") as mock_model:
            mock_whisper = MagicMock()
            mock_model.return_value = mock_whisper
            
            await service.initialize()
            
            mock_model.assert_called_once_with("tiny")
    
    async def test_language_detection(self, whisper_service: WhisperService):
        """Test automatic language detection"""
        # Verify that language is set to None for auto-detection
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.wav"
            mock_temp.return_value = mock_file
            
            with patch("os.path.exists", return_value=True), \
                 patch("os.unlink"):
                
                await whisper_service.transcribe(b"dummy audio", "wav")
                
                # Verify transcribe was called with language=None (auto-detect)
                call_args = whisper_service.model.transcribe.call_args
                assert call_args[1]["language"] is None
                assert call_args[1]["fp16"] is False 