from typing import Optional, Dict, Any
import httpx
from loguru import logger

class LlamaService:
    def __init__(self):
        self.base_url = "http://localhost:11434/api"
        self.model = "llama2:13b-chat"
        self._check_model()
    
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

    async def process_transcription(
        self,
        transcription: str,
        system_prompt: str = "You are a helpful assistant processing audio transcriptions.",
    ) -> str:
        """Process a transcription using the LLaMA model"""
        prompt = f"""
        System: {system_prompt}
        User: Process this transcription: {transcription}
        Assistant: """
        
        return await self.generate_response(prompt)

# Initialize the service
llama_service = LlamaService() 