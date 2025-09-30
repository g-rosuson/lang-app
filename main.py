from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.v1.api import api_router
from src.config import settings
from src.services.logging.logging import get_logger
from src.services.language_analysis import get_language_analysis_service

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Language App...")
    
    # Initialize language analysis service if enabled
    if settings.language_analysis_enabled:
        try:
            from src.services.language_analysis import initialize_pipeline
            
            # Create pipeline configuration from settings
            pipeline_config = {
                "max_text_length": settings.max_text_length,
                "stanza_language": settings.stanza_language,
                "stanza_processors": settings.stanza_processors,
                "stanza_model_dir": settings.stanza_model_dir,
                "use_gpu": settings.use_gpu,
                "language_tool_language": settings.language_tool_language,
                "pipeline_timeout_seconds": settings.pipeline_timeout_seconds,
                "enable_parallel_processing": settings.enable_parallel_processing
            }
            
            # Initialize the pipeline
            pipeline = initialize_pipeline(pipeline_config)
            logger.info("Language analysis pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize language analysis pipeline: {e}")
            logger.warning("Language analysis features will not be available")
    else:
        logger.info("Language analysis is disabled")
    
    logger.info("Language App started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Language App...")
    
    # Cleanup language analysis service
    if settings.language_analysis_enabled:
        try:
            pipeline = get_language_analysis_service()
            pipeline.cleanup()
            logger.info("Language analysis pipeline cleaned up")
        except Exception as e:
            logger.error(f"Error during pipeline cleanup: {e}")
    
    logger.info("Language App shutdown complete")


app = FastAPI(
    title=settings.app_name, 
    version=settings.app_version,
    lifespan=lifespan
)

# Include all API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)