from typing import Optional, Dict, Any
import httpx
from loguru import logger

from ..base import BaseLLMService

class LlamaService(BaseLLMService):
    def __init__(self):
        self.base_url = "http://localhost:11434/api"
        self.model = "llama2:13b-chat"
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the LLM service and load models"""
        if not self._initialized:
            self._check_model()
            self._initialized = True
    
    def _check_model(self) -> None:
        """Verify that the model is available"""
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.base_url}/tags")
                models = response.json()
                
                if not any(model["name"] == self.model for model in models["models"]):
                    raise RuntimeError(
                        f"Model {self.model} not found. Please run 'ollama pull {self.model}' first."
                    )
                
                logger.success(f"LLaMA model '{self.model}' is available!")
        
        except Exception as e:
            logger.error(f"Failed to check LLaMA model: {str(e)}")
            raise
    
    async def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.95,
    ) -> str:
        """Generate a response from the LLaMA model using Ollama"""
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "top_p": top_p,
                        "stream": False,
                    },
                    timeout=30.0,
                )
                
                result = response.json()
                return result["response"].strip()
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def process_transcription(self, transcription: str) -> Dict[str, str]:
        """Process a transcription through LLM chains"""
        try:
            # Process the transcription for better formatting
            process_prompt = f"""
            Process the following transcription, correcting any obvious errors,
            and format it into clear, punctuated text:
            
            {transcription}
            """
            
            processed_text = await self.generate_response(process_prompt)
            
            # Generate a summary
            summary_prompt = f"""
            Provide a concise summary of the following transcription:
            
            {transcription}
            """
            
            summary = await self.generate_response(summary_prompt)
            
            return {
                "processed_text": processed_text,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error in transcription processing: {str(e)}")
            raise
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        # No specific cleanup needed for HTTP client
        self._initialized = False

# Initialize the service
llama_service = LlamaService() 