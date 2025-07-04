from typing import Any, Dict
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from loguru import logger

from ..providers.llama import llama_service

class LlamaLLM(LLM):
    """Custom LangChain LLM class for our LlamaService"""
    
    @property
    def _llm_type(self) -> str:
        return "custom_llama"
    
    async def _acall(self, prompt: str, stop: list[str] | None = None, **kwargs: Any) -> str:
        """Async call to the LlamaService"""
        return await llama_service.generate_response(prompt)
    
    def _call(self, prompt: str, stop: list[str] | None = None, **kwargs: Any) -> str:
        """Synchronous call - we'll use async in practice"""
        raise NotImplementedError("Please use async calls with this LLM")

class TranscriptionChain:
    """LangChain for processing transcriptions"""
    
    def __init__(self):
        self.llm = LlamaLLM()
        self._initialize_chains()
    
    def _initialize_chains(self) -> None:
        """Initialize different processing chains"""
        # Basic transcription processing chain
        self.process_prompt = PromptTemplate(
            input_variables=["transcription"],
            template="""
            Process the following transcription, correcting any obvious errors,
            and format it into clear, punctuated text:
            
            {transcription}
            """
        )
        
        # Modern LangChain pattern: prompt | llm
        self.process_chain = self.process_prompt | self.llm
        
        # Summary chain
        self.summary_prompt = PromptTemplate(
            input_variables=["transcription"],
            template="""
            Provide a concise summary of the following transcription:
            
            {transcription}
            """
        )
        
        # Modern LangChain pattern: prompt | llm
        self.summary_chain = self.summary_prompt | self.llm
    
    async def process_transcription(self, transcription: str) -> Dict[str, str]:
        """Process a transcription through multiple chains"""
        try:
            # Run chains using modern LangChain invoke API
            processed = await self.process_chain.ainvoke({"transcription": transcription})
            summary = await self.summary_chain.ainvoke({"transcription": transcription})
            
            return {
                "processed_text": processed,
                "summary": summary
            }
        
        except Exception as e:
            logger.error(f"Error in transcription chain: {str(e)}")
            raise

# Initialize the chain
transcription_chain = TranscriptionChain() 