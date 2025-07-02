from fastapi import FastAPI
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