"""
FastAPI Routes.

Defines all API endpoints for the interview screener.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas.request import EvaluateAnswerRequest, RankCandidatesRequest
from app.schemas.response import (
    EvaluationResponse,
    RankingResponse,
    ErrorResponse,
    HealthResponse
)
from app.services.evaluation import EvaluationService
from app.services.ranking import RankingService
from app.api.dependencies import get_evaluation_service_dep, get_ranking_service_dep
from app.core.config import settings
from app.services.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Interview Screener API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health"
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(
    evaluation_service: EvaluationService = Depends(get_evaluation_service_dep)
):
    """
    Health check endpoint.
    
    Returns service status and configuration information.
    """
    # Check Redis connection
    redis_connected = False
    if evaluation_service.redis_client:
        try:
            await evaluation_service.redis_client.ping()
            redis_connected = True
        except Exception:
            redis_connected = False
    
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        llm_provider="groq",
        redis_connected=redis_connected
    )


@router.post(
    "/evaluate-answer",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Evaluation"],
    summary="Evaluate a single candidate answer",
    description="""
    Evaluates a candidate's answer using a multi-agent AI system.
    
    Returns:
    - **score**: Integer from 1-5 indicating answer quality
    - **summary**: One-line summary of the answer
    - **improvement**: One specific improvement suggestion
    
    The evaluation uses specialized AI agents for scoring, analysis, and feedback generation.
    Results are cached for performance.
    """
)
async def evaluate_answer(
    request: EvaluateAnswerRequest,
    evaluation_service: EvaluationService = Depends(get_evaluation_service_dep)
):
    """
    Evaluate a single candidate answer.
    
    Args:
        request: Evaluation request with candidate answer
        evaluation_service: Injected evaluation service
        
    Returns:
        EvaluationResponse with score, summary, and improvement
    """
    try:
        logger.info("Received evaluation request")
        result = await evaluation_service.evaluate(request)
        logger.info(f"Evaluation successful: score={result.score}")
        return result
        
    except Exception as e:
        logger.error(f"Evaluation endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "EvaluationError",
                "message": "Failed to evaluate answer",
                "details": {"error": str(e)}
            }
        )


@router.post(
    "/rank-candidates",
    response_model=RankingResponse,
    status_code=status.HTTP_200_OK,
    tags=["Ranking"],
    summary="Rank multiple candidates",
    description="""
    Evaluates and ranks multiple candidates based on their answers.
    
    Candidates are evaluated in parallel for performance, then sorted by score
    (highest to lowest). Each candidate receives:
    - **score**: Integer from 1-5
    - **summary**: One-line summary
    - **improvement**: One improvement suggestion
    - **rank**: Their rank among all candidates (1 is best)
    
    Results are cached for performance.
    """
)
async def rank_candidates(
    request: RankCandidatesRequest,
    ranking_service: RankingService = Depends(get_ranking_service_dep)
):
    """
    Rank multiple candidates based on their answers.
    
    Args:
        request: Ranking request with multiple candidate answers
        ranking_service: Injected ranking service
        
    Returns:
        RankingResponse with ranked candidates
    """
    try:
        logger.info(f"Received ranking request for {len(request.candidates)} candidates")
        result = await ranking_service.rank_candidates(request)
        logger.info(f"Ranking successful: {result.total_candidates} candidates ranked")
        return result
        
    except Exception as e:
        logger.error(f"Ranking endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "RankingError",
                "message": "Failed to rank candidates",
                "details": {"error": str(e)}
            }
        )


# Error handlers

async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with standardized error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail.get("error", "HTTPException"),
            message=exc.detail.get("message", str(exc.detail)),
            details=exc.detail.get("details")
        ).model_dump()
    )



async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions with standardized error response."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"error": str(exc)}
        ).model_dump()
    )

