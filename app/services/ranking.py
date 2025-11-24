"""
Ranking Service - Business logic for ranking multiple candidates.

Handles batch evaluation and ranking of candidates.
"""
import asyncio
from typing import List

from app.schemas.request import RankCandidatesRequest, CandidateAnswer
from app.schemas.response import RankingResponse, RankedCandidate
from app.services.evaluation import get_evaluation_service
from app.schemas.request import EvaluateAnswerRequest
from app.services.logger import get_logger

logger = get_logger(__name__)


class RankingService:
    """
    Service for ranking multiple candidates.
    
    Evaluates candidates in parallel and ranks them by score.
    """
    
    async def rank_candidates(self, request: RankCandidatesRequest) -> RankingResponse:
        """
        Rank multiple candidates based on their answers.
        
        Args:
            request: Ranking request with candidate answers
            
        Returns:
            RankingResponse with sorted candidates
        """
        logger.info(f"Ranking {len(request.candidates)} candidates")
        
        evaluation_service = await get_evaluation_service()
        
        # Evaluate all candidates in parallel
        eval_tasks = []
        for candidate in request.candidates:
            eval_request = EvaluateAnswerRequest(
                candidate_answer=candidate.answer,
                question_context=request.question_context
            )
            eval_tasks.append(
                self._evaluate_candidate(
                    evaluation_service,
                    candidate.candidate_id,
                    eval_request
                )
            )
        
        # Wait for all evaluations to complete
        evaluated_candidates = await asyncio.gather(*eval_tasks)
        
        # Sort by score (highest first)
        evaluated_candidates.sort(key=lambda x: x.score, reverse=True)
        
        # Assign ranks
        ranked_candidates = []
        current_rank = 1
        for candidate in evaluated_candidates:
            ranked_candidates.append(
                RankedCandidate(
                    candidate_id=candidate.candidate_id,
                    score=candidate.score,
                    summary=candidate.summary,
                    improvement=candidate.improvement,
                    rank=current_rank
                )
            )
            current_rank += 1
        
        logger.info(f"Ranking complete: {len(ranked_candidates)} candidates ranked")
        
        return RankingResponse(
            candidates=ranked_candidates,
            total_candidates=len(ranked_candidates)
        )
    
    async def _evaluate_candidate(
        self,
        evaluation_service,
        candidate_id: str,
        eval_request: EvaluateAnswerRequest
    ) -> RankedCandidate:
        """
        Evaluate a single candidate.
        
        Args:
            evaluation_service: Evaluation service instance
            candidate_id: Candidate identifier
            eval_request: Evaluation request
            
        Returns:
            RankedCandidate (without rank assigned yet)
        """
        try:
            result = await evaluation_service.evaluate(eval_request)
            return RankedCandidate(
                candidate_id=candidate_id,
                score=result.score,
                summary=result.summary,
                improvement=result.improvement,
                rank=0  # Will be assigned later
            )
        except Exception as e:
            logger.error(f"Failed to evaluate candidate {candidate_id}: {str(e)}")
            # Return fallback evaluation
            return RankedCandidate(
                candidate_id=candidate_id,
                score=3,
                summary="Evaluation failed",
                improvement="Unable to provide feedback",
                rank=0
            )


# Singleton instance
_ranking_service: RankingService | None = None


def get_ranking_service() -> RankingService:
    """
    Get or create the ranking service singleton.
    
    Returns:
        RankingService instance
    """
    global _ranking_service
    
    if _ranking_service is None:
        _ranking_service = RankingService()
    
    return _ranking_service

