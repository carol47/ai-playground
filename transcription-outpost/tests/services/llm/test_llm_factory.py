import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.llm.factory import (
    LLMServiceFactory, 
    LLMServiceType, 
    get_llm_service
)
from app.services.llm.base import BaseLLMService
from app.services.llm.providers.llama import LlamaService


@pytest.mark.asyncio
class TestLLMServiceFactory:
    """Test LLM service factory functionality"""
    
    async def test_factory_creates_llama_service(self):
        """Test factory creates LLaMA service correctly"""
        with patch("app.services.llm.providers.llama.LlamaService") as mock_llama:
            mock_instance = AsyncMock(spec=LlamaService)
            mock_llama.return_value = mock_instance
            
            service = await LLMServiceFactory.get_service(LLMServiceType.LLAMA)
            
            assert service is mock_instance
            mock_instance.initialize.assert_called_once()
    
    async def test_factory_singleton_behavior(self):
        """Test factory returns singleton instances"""
        with patch("app.services.llm.providers.llama.LlamaService") as mock_llama:
            mock_instance = AsyncMock(spec=LlamaService)
            mock_llama.return_value = mock_instance
            
            # Get service twice
            service1 = await LLMServiceFactory.get_service(LLMServiceType.LLAMA)
            service2 = await LLMServiceFactory.get_service(LLMServiceType.LLAMA)
            
            # Should be same instance
            assert service1 is service2
            # Initialize should only be called once
            assert mock_instance.initialize.call_count == 1
            
            # Cleanup
            await LLMServiceFactory.cleanup()
    
    async def test_factory_unknown_service_type(self):
        """Test factory raises error for unknown service type"""
        with pytest.raises(ValueError, match="Unknown LLM service type"):
            await LLMServiceFactory.get_service("unknown_llm")  # type: ignore
    
    async def test_factory_cleanup(self):
        """Test factory cleanup functionality"""
        with patch("app.services.llm.providers.llama.LlamaService") as mock_llama:
            mock_instance = AsyncMock(spec=LlamaService)
            mock_llama.return_value = mock_instance
            
            # Get service and cleanup
            await LLMServiceFactory.get_service(LLMServiceType.LLAMA)
            await LLMServiceFactory.cleanup()
            
            # Cleanup should be called on instance
            mock_instance.cleanup.assert_called_once()
            
            # Instance should be reset
            assert LLMServiceFactory._instance is None
    
    async def test_get_llm_service_function(self):
        """Test convenience function for getting LLM service"""
        with patch("app.services.llm.providers.llama.LlamaService") as mock_llama:
            mock_instance = AsyncMock(spec=LlamaService)
            mock_llama.return_value = mock_instance
            
            service = await get_llm_service()
            
            assert service is mock_instance
            mock_instance.initialize.assert_called_once()
    
    async def test_get_llm_service_with_type(self):
        """Test convenience function with specific service type"""
        with patch("app.services.llm.providers.llama.LlamaService") as mock_llama:
            mock_instance = AsyncMock(spec=LlamaService)
            mock_llama.return_value = mock_instance
            
            service = await get_llm_service(LLMServiceType.LLAMA)
            
            assert service is mock_instance
            mock_instance.initialize.assert_called_once()
    
    async def test_multiple_service_types(self):
        """Test factory handles multiple service types correctly"""
        with patch("app.services.llm.providers.llama.LlamaService") as mock_llama:
            mock_instance = AsyncMock(spec=LlamaService)
            mock_llama.return_value = mock_instance
            
            # Get LLaMA service
            llama_service = await LLMServiceFactory.get_service(LLMServiceType.LLAMA)
            
            assert llama_service is mock_instance
            mock_instance.initialize.assert_called_once()
            
            # Future: test with multiple service types when more are added
            await LLMServiceFactory.cleanup()


class TestLLMServiceTypes:
    """Test LLM service type enumeration"""
    
    def test_llm_service_type_values(self):
        """Test that all expected service types are available"""
        assert LLMServiceType.LLAMA == "llama"
        assert "llama" in [t.value for t in LLMServiceType]
    
    def test_llm_service_type_string_behavior(self):
        """Test service type can be used as string"""
        service_type = LLMServiceType.LLAMA
        # LLMServiceType inherits from str, so str() returns the enum name, not the value
        assert str(service_type) == "LLMServiceType.LLAMA"
        assert service_type == "llama"  # Value comparison works
        assert service_type.value == "llama"  # Direct value access


@pytest.mark.asyncio
class TestLLMServiceIntegration:
    """Test LLM service integration with actual provider"""
    
    async def test_llm_service_interface_compliance(self):
        """Test that LLM service implements required interface"""
        with patch("app.services.llm.providers.llama.LlamaService") as mock_llama:
            mock_instance = AsyncMock(spec=LlamaService)
            mock_llama.return_value = mock_instance
            
            service = await LLMServiceFactory.get_service(LLMServiceType.LLAMA)
            
            # Check that service has required methods from BaseLLMService
            assert hasattr(service, "initialize")
            assert hasattr(service, "cleanup")
            assert hasattr(service, "generate_response")
            assert hasattr(service, "process_transcription")
            
            await LLMServiceFactory.cleanup()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_factory():
    """Auto-cleanup factory between tests"""
    yield
    await LLMServiceFactory.cleanup() 