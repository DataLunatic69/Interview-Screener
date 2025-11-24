"""
Main Application Entry Point.

Initializes and configures the FastAPI application.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings
from app.services.evaluation import get_evaluation_service
from app.services.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Model: {settings.llm_model}")
    
    # Initialize services
    eval_service = await get_evaluation_service()
    logger.info("Services initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await eval_service.close_redis()
    logger.info("Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    # AI Interview Screener API
    
    A multi-agent AI system for evaluating and ranking candidate interview answers.
    
    ## Features
    
    - **Multi-Agent Architecture**: Specialized agents for scoring, analysis, and feedback
    - **Intelligent Caching**: Redis-based caching for performance and cost optimization
    - **Parallel Processing**: Evaluate multiple candidates simultaneously
    - **Structured Output**: Consistent JSON responses with scores, summaries, and improvements
    
    ## Technology Stack
    
    - **LLM Provider**: Groq (llama-3.3-70b-versatile)
    - **Framework**: LangGraph for multi-agent orchestration
    - **Cache**: Redis for intelligent caching
    - **API**: FastAPI for high-performance async endpoints
    
    ## Endpoints
    
    - `POST /evaluate-answer`: Evaluate a single candidate answer
    - `POST /rank-candidates`: Evaluate and rank multiple candidates
    - `GET /health`: Service health check
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Global exception handler: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"error": str(exc)} if settings.debug else None
        }
    )


if __name__ == "__main__":
    import os
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
