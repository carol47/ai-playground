from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageBase(BaseModel):
    """Base model for chat messages"""
    content: str = Field(..., description="The content of the message")
    role: str = Field(default="user", description="The role of the message sender (user/assistant)")


class ChatMessage(MessageBase):
    """Model for chat messages with metadata"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))


class ChatResponse(BaseModel):
    """Model for chat responses"""
    message: ChatMessage
    context: Optional[dict] = Field(default=None, description="Additional context or metadata")


class TranscriptionRequest(BaseModel):
    """Model for transcription requests"""
    audio_format: str = Field(..., description="Format of the audio file (wav, mp3, etc.)")
    language: str = Field(default="en", description="Language code for transcription")
    stream: bool = Field(default=True, description="Whether to stream the transcription")


class TranscriptionResponse(BaseModel):
    """Model for transcription responses"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Confidence score of the transcription")
    segments: Optional[List[dict]] = Field(default=None, description="Time-aligned segments")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata") 