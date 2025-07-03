from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logger import log
from .core.audio import configure_ffmpeg
from .services.speech.router import router as transcription_router
from .services.speech.factory import get_transcription_service, SpeechServiceType

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcription_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.APP_NAME}

# API Info endpoints
@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "ru", "name": "Russian"},
            {"code": "ar", "name": "Arabic"},
            {"code": "hi", "name": "Hindi"},
        ]
    }

@app.get("/info")
async def get_service_info():
    """Get service information"""
    return {
        "service_name": "Transcription Outpost",
        "version": "1.0.0",
        "speech_providers": ["whisper"],
        "llm_providers": ["llama"],
        "supported_formats": settings.SUPPORTED_AUDIO_FORMATS,
        "max_file_size_mb": settings.MAX_AUDIO_SIZE_MB,
        "api_version": "v1",
    }

@app.get("/metrics")
async def get_service_metrics():
    """Get service metrics and statistics"""
    return {
        "requests_total": 0,
        "processing_time_avg": 0.0,
        "active_connections": 0,
        "service_uptime": "0d 0h 0m",
        "memory_usage_mb": 0,
        "available_models": ["whisper"],
    }

# Additional endpoints expected by tests
@app.post("/transcribe")
async def transcribe_basic(
    file: UploadFile,
    language: str = Form("auto"),
    format: str = Form("wav"),
    enhance: str = Form("false")
):
    """Basic transcription endpoint (alias for main endpoint)"""
    from .services.speech.factory import get_transcription_service, SpeechServiceType
    from .core.config import settings
    
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
        
        # Perform transcription
        result = await transcription_service.transcribe(content, file_ext)
        
        response_data = {
            "text": result.text,
            "confidence": result.confidence,
            "language": result.language,
            "duration": result.duration
        }
        
        # If enhancement is requested, add enhanced text
        if enhance.lower() == "true":
            response_data["enhanced_text"] = result.text  # For now, same as original
            
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e)}
        )

@app.post("/transcribe/stream")
async def transcribe_stream(
    file: UploadFile,
    language: str = "auto",
    format: str = "wav",
    stream: str = "true"
):
    """Streaming transcription endpoint (placeholder)"""
    # For now, return the same as basic transcription
    # In a real implementation, this would use Server-Sent Events or WebSockets
    return {"message": "Streaming transcription not yet implemented", "status": "placeholder"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    log.info(f"Starting {settings.APP_NAME}")
    
    # Configure ffmpeg
    try:
        ffmpeg_path = configure_ffmpeg()
        log.info(f"FFmpeg configured at: {ffmpeg_path}")
    except Exception as e:
        log.error(f"Failed to configure FFmpeg: {str(e)}")
        raise
    
    # Initialize Whisper model on startup
    transcription_service = await get_transcription_service(SpeechServiceType.WHISPER)
    await transcription_service.initialize()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    log.info(f"Shutting down {settings.APP_NAME}")
    # Cleanup will be handled by Python's garbage collection

# Import and include routers
# TODO: Add routers for transcription, chat, and websocket endpoints 