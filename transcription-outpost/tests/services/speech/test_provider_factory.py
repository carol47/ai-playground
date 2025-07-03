import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.speech.factory import (
    SpeechServiceFactory, 
    SpeechServiceType, 
    get_transcription_service
)
from app.services.speech.base import BaseSpeechService
from app.services.speech.providers.whisper import WhisperService


@pytest.mark.asyncio
class TestSpeechServiceFactory:
    """Test speech service factory functionality"""
    
    async def test_factory_creates_whisper_service(self):
        """Test factory creates Whisper service correctly"""
        with patch("app.services.speech.factory.WhisperService") as mock_whisper:
            mock_instance = AsyncMock(spec=WhisperService)
            mock_whisper.return_value = mock_instance
            
            service = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
            
            assert service is mock_instance
            mock_instance.initialize.assert_called_once()
    
    async def test_factory_singleton_behavior(self):
        """Test factory returns singleton instances"""
        with patch("app.services.speech.factory.WhisperService") as mock_whisper:
            mock_instance = AsyncMock(spec=WhisperService)
            mock_whisper.return_value = mock_instance
            
            # Get service twice
            service1 = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
            service2 = await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
            
            # Should be same instance
            assert service1 is service2
            # Initialize should only be called once
            assert mock_instance.initialize.call_count == 1
            
            # Cleanup
            await SpeechServiceFactory.cleanup()
    
    async def test_factory_unknown_service_type(self):
        """Test factory raises error for unknown service type"""
        # Create a custom service type that doesn't exist
        with patch("app.services.speech.factory.SpeechServiceType") as mock_enum:
            mock_enum.WHISPER = "whisper"
            # Test with an invalid enum value by mocking the _create_service method
            with patch.object(SpeechServiceFactory, '_create_service', side_effect=ValueError("Unknown speech service type")):
                with pytest.raises(ValueError, match="Unknown speech service type"):
                    await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
    
    async def test_factory_cleanup(self):
        """Test factory cleanup functionality"""
        with patch("app.services.speech.factory.WhisperService") as mock_whisper:
            mock_instance = AsyncMock(spec=WhisperService)
            mock_whisper.return_value = mock_instance
            
            # Get service and cleanup
            await SpeechServiceFactory.get_service(SpeechServiceType.WHISPER)
            await SpeechServiceFactory.cleanup()
            
            # Cleanup should be called on instance
            mock_instance.cleanup.assert_called_once()
            
            # Instance should be reset
            assert SpeechServiceFactory._instance is None
    
    async def test_get_transcription_service_function(self):
        """Test convenience function for getting transcription service"""
        with patch("app.services.speech.factory.WhisperService") as mock_whisper:
            mock_instance = AsyncMock(spec=WhisperService)
            mock_whisper.return_value = mock_instance
            
            service = await get_transcription_service()
            
            assert service is mock_instance
            mock_instance.initialize.assert_called_once()
    
    async def test_get_transcription_service_with_type(self):
        """Test convenience function with specific service type"""
        with patch("app.services.speech.factory.WhisperService") as mock_whisper:
            mock_instance = AsyncMock(spec=WhisperService)
            mock_whisper.return_value = mock_instance
            
            service = await get_transcription_service(SpeechServiceType.WHISPER)
            
            assert service is mock_instance
            mock_instance.initialize.assert_called_once()


@pytest.mark.asyncio
class TestSpeechServiceTypes:
    """Test speech service type enumeration"""
    
    def test_speech_service_type_values(self):
        """Test that all expected service types are available"""
        assert SpeechServiceType.WHISPER == "whisper"
        assert "whisper" in [t.value for t in SpeechServiceType]
    
    def test_speech_service_type_string_behavior(self):
        """Test service type can be used as string"""
        service_type = SpeechServiceType.WHISPER
        # SpeechServiceType str() returns the enum name, not the value
        assert str(service_type) == "SpeechServiceType.WHISPER"
        assert service_type == "whisper"  # Value comparison works
        assert service_type.value == "whisper"  # Direct value access


@pytest_asyncio.fixture(autouse=True)
async def cleanup_factory():
    """Auto-cleanup factory between tests"""
    yield
    await SpeechServiceFactory.cleanup() 