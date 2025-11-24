"""
FastAPI Dependencies.

Provides dependency injection for services and shared resources.
"""
from app.services.evaluation import get_evaluation_service, EvaluationService
from app.services.ranking import get_ranking_service, RankingService


async def get_evaluation_service_dep() -> EvaluationService:
    """
    Dependency for getting evaluation service.
    
    Returns:
        EvaluationService instance
    """
    return await get_evaluation_service()


def get_ranking_service_dep() -> RankingService:
    """
    Dependency for getting ranking service.
    
    Returns:
        RankingService instance
    """
    return get_ranking_service()

