import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.llm.chains.transcription import (
    TranscriptionChain,
    LlamaLLM,
    transcription_chain
)


@pytest_asyncio.fixture
async def mock_llama_service():
    """Mock LLaMA service for testing"""
    with patch("app.services.llm.chains.transcription.llama_service") as mock_service:
        mock_service.generate_response = AsyncMock(return_value="Enhanced transcription text")
        yield mock_service


@pytest.mark.asyncio
class TestTranscriptionChain:
    """Test transcription chain functionality"""
    
    async def test_chain_initialization(self):
        """Test chain initializes correctly"""
        chain = TranscriptionChain()
        
        assert chain.llm is not None
        assert hasattr(chain, 'process_chain')
        assert hasattr(chain, 'summary_chain')
        assert hasattr(chain, 'process_prompt')
        assert hasattr(chain, 'summary_prompt')
    
    async def test_llama_llm_properties(self):
        """Test LlamaLLM properties"""
        llm = LlamaLLM()
        
        assert llm._llm_type == "custom_llama"
        
        # Test that sync call raises NotImplementedError
        with pytest.raises(NotImplementedError):
            llm._call("test prompt")
    
    async def test_process_transcription_basic(self, mock_llama_service):
        """Test basic transcription processing"""
        chain = TranscriptionChain()
        
        # Set up the mock service to return different responses based on the prompt
        async def mock_response(prompt, **kwargs):
            if "correcting any obvious errors" in prompt:
                return "Enhanced transcription text"
            elif "concise summary" in prompt:
                return "Brief summary"
            return "Default response"
        
        mock_llama_service.generate_response.side_effect = mock_response
        
        result = await chain.process_transcription("hello world")
        
        assert result["processed_text"] == "Enhanced transcription text"
        assert result["summary"] == "Brief summary"
        
        # Verify service was called twice (once for each chain)
        assert mock_llama_service.generate_response.call_count == 2
    
    async def test_process_transcription_error_handling(self, mock_llama_service):
        """Test error handling in transcription processing"""
        chain = TranscriptionChain()
        
        # Mock service to raise exception
        async def mock_error(*args, **kwargs):
            raise Exception("Chain processing error")
        
        mock_llama_service.generate_response.side_effect = mock_error
        
        with pytest.raises(Exception, match="Chain processing error"):
            await chain.process_transcription("hello world")
    
    async def test_llama_llm_async_call(self, mock_llama_service):
        """Test LlamaLLM async call"""
        llm = LlamaLLM()
        
        result = await llm._acall("test prompt")
        
        assert result == "Enhanced transcription text"
        mock_llama_service.generate_response.assert_called_once_with("test prompt")
    
    async def test_global_transcription_chain(self):
        """Test global transcription chain instance"""
        assert transcription_chain is not None
        assert isinstance(transcription_chain, TranscriptionChain)
    
    async def test_prompt_templates(self):
        """Test that prompt templates are properly configured"""
        chain = TranscriptionChain()
        
        # Test process prompt
        process_prompt = chain.process_prompt.format(transcription="test text")
        assert "test text" in process_prompt
        assert "correcting any obvious errors" in process_prompt
        
        # Test summary prompt  
        summary_prompt = chain.summary_prompt.format(transcription="test text")
        assert "test text" in summary_prompt
        assert "concise summary" in summary_prompt
    
    async def test_chain_configuration(self):
        """Test that chains are properly configured"""
        chain = TranscriptionChain()
        
        # Test that chains are RunnableSequence (modern LangChain pattern)
        assert hasattr(chain.process_chain, 'steps')
        assert hasattr(chain.summary_chain, 'steps')
        assert len(chain.process_chain.steps) == 2  # prompt + llm
        assert len(chain.summary_chain.steps) == 2  # prompt + llm


@pytest.mark.asyncio 
class TestTranscriptionChainIntegration:
    """Integration tests for transcription chain"""
    
    async def test_end_to_end_processing(self, mock_llama_service):
        """Test end-to-end transcription processing"""
        chain = TranscriptionChain()
        
        # Mock the service responses for different prompts
        async def mock_response(prompt, **kwargs):
            if "correcting any obvious errors" in prompt:
                return "This is a corrected transcription."
            elif "concise summary" in prompt:
                return "Meeting about project updates."
            return "Default response"
        
        mock_llama_service.generate_response.side_effect = mock_response
        
        result = await chain.process_transcription("this is a transcripshun")
        
        assert "processed_text" in result
        assert "summary" in result
        assert result["processed_text"] == "This is a corrected transcription."
        assert result["summary"] == "Meeting about project updates."
    
    async def test_empty_transcription_handling(self, mock_llama_service):
        """Test handling of empty transcription"""
        chain = TranscriptionChain()
        
        async def mock_response(prompt, **kwargs):
            if "correcting any obvious errors" in prompt:
                return ""
            elif "concise summary" in prompt:
                return "No content to summarize."
            return "Default response"
        
        mock_llama_service.generate_response.side_effect = mock_response
        
        result = await chain.process_transcription("")
        
        assert result["processed_text"] == ""
        assert result["summary"] == "No content to summarize." 