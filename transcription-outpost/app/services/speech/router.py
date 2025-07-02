from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
from ...core.config import settings
from ...core.logger import log
from .factory import get_transcription_service, SpeechServiceType
from .base import AudioTranscriptionResult

router = APIRouter(prefix="/transcription", tags=["transcription"])

@router.post("/", response_model=AudioTranscriptionResult)
async def transcribe_audio(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    model: str = "whisper",  # default to whisper since we switched from paddle
) -> AudioTranscriptionResult:
    """
    Transcribe an uploaded audio file
    
    Args:
        file: The audio file to transcribe
        model: The model to use for transcription (currently only supports 'whisper')
        background_tasks: FastAPI background tasks for cleanup
    
    Returns:
        AudioTranscriptionResult containing the transcription text and metadata
    """
    # Validate file size
    if file.size and file.size > settings.MAX_AUDIO_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum of {settings.MAX_AUDIO_SIZE_MB}MB"
        )
    
    # Get file extension and validate format
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported audio format. Supported formats: {settings.SUPPORTED_AUDIO_FORMATS}"
        )
    
    try:
        # Get transcription service
        transcription_service = await get_transcription_service(SpeechServiceType.WHISPER)
        
        # Read file content
        content = await file.read()
        
        # Add cleanup to background tasks
        background_tasks.add_task(file.close)
        
        # Perform transcription
        result = await transcription_service.transcribe(content, file_ext)
        
        return result
        
    except Exception as e:
        log.error(f"Transcription failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Transcription failed. Please try again."
        )

@router.get("/models")
async def list_available_models() -> dict:
    """List available transcription models"""
    return {
        "available_models": ["whisper"],
        "default_model": "whisper"
    } 