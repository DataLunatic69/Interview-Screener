"""
Evaluation Service - Business logic for answer evaluation.

Handles caching, orchestration, and error handling for evaluations.
"""
import hashlib
import json
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings
from app.core.graph import evaluation_graph
from app.schemas.request import EvaluateAnswerRequest
from app.schemas.response import EvaluationResponse
from app.services.logger import get_logger

logger = get_logger(__name__)


class EvaluationService:
    """
    Service for evaluating candidate answers.
    
    Handles caching and orchestration of the evaluation workflow.
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.graph = evaluation_graph
    
    async def initialize_redis(self):
        """Initialize Redis connection."""
        if settings.enable_caching:
            try:
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {str(e)}. Caching disabled.")
                self.redis_client = None
    
    async def close_redis(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    def _generate_cache_key(self, answer: str, question: Optional[str]) -> str:
        """
        Generate cache key based on answer and question.
        
        Args:
            answer: Candidate answer
            question: Optional question context
            
        Returns:
            MD5 hash to use as cache key
        """
        content = f"{answer}:{question or ''}"
        return f"eval:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[EvaluationResponse]:
        """
        Retrieve cached evaluation result.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached EvaluationResponse or None
        """
        if not self.redis_client or not settings.enable_caching:
            return None
        
        try:
            cached = await self.redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit: {cache_key}")
                data = json.loads(cached)
                return EvaluationResponse(**data)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {str(e)}")
        
        return None
    
    async def _cache_result(self, cache_key: str, result: EvaluationResponse):
        """
        Cache evaluation result.
        
        Args:
            cache_key: Cache key
            result: Evaluation result to cache
        """
        if not self.redis_client or not settings.enable_caching:
            return
        
        try:
            await self.redis_client.setex(
                cache_key,
                settings.redis_ttl,
                json.dumps(result.model_dump())
            )
            logger.info(f"Result cached: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache write failed: {str(e)}")
    
    async def evaluate(self, request: EvaluateAnswerRequest) -> EvaluationResponse:
        """
        Evaluate a candidate answer.
        
        Args:
            request: Evaluation request
            
        Returns:
            Evaluation response with score, summary, and improvement
        """
        logger.info(
            f"Evaluating answer: length={len(request.candidate_answer)}, "
            f"has_context={request.question_context is not None}"
        )
        
        # Check cache
        cache_key = self._generate_cache_key(
            request.candidate_answer,
            request.question_context
        )
        
        cached_result = await self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Execute workflow
        try:
            initial_state = {
                "candidate_answer": request.candidate_answer,
                "question_context": request.question_context,
                "evaluator_score": None,
                "evaluator_justification": None,
                "analyzer_strengths": None,
                "analyzer_weaknesses": None,
                "improvement_suggestion": None,
                "final_score": None,
                "final_summary": None,
                "final_improvement": None,
                "messages": [],
                "current_agent": None,
                "error": None,
                "cached": False
            }
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            # Extract final results
            response = EvaluationResponse(
                score=result["final_score"],
                summary=result["final_summary"],
                improvement=result["final_improvement"]
            )
            
            # Cache the result
            await self._cache_result(cache_key, response)
            
            logger.info(f"Evaluation complete: score={response.score}")
            return response
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            # Return fallback response
            return EvaluationResponse(
                score=3,
                summary="Evaluation encountered an error",
                improvement="Please try again or contact support"
            )


# Singleton instance
_evaluation_service: Optional[EvaluationService] = None


async def get_evaluation_service() -> EvaluationService:
    """
    Get or create the evaluation service singleton.
    
    Returns:
        EvaluationService instance
    """
    global _evaluation_service
    
    if _evaluation_service is None:
        _evaluation_service = EvaluationService()
        await _evaluation_service.initialize_redis()
    
    return _evaluation_service

