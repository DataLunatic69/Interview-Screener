"""
Response schemas for API endpoints.
Provides standardized response structures for all endpoints.
"""
from typing import List
from pydantic import BaseModel, Field


class EvaluationResponse(BaseModel):
    """
    Response model for /evaluate-answer endpoint.
    
    Returns evaluation results for a single candidate answer.
    """
    
    score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Score from 1-5 indicating answer quality",
        examples=[4]
    )
    
    summary: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="One-line summary of the answer",
        examples=["Solid understanding of hash maps with correct time complexity analysis"]
    )
    
    improvement: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="One specific improvement suggestion",
        examples=["Consider mentioning space complexity and edge cases like duplicate elements"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "score": 4,
                "summary": "Solid understanding of hash maps with correct time complexity analysis",
                "improvement": "Consider mentioning space complexity and edge cases like duplicate elements"
            }
        }


class RankedCandidate(BaseModel):
    """
    Single ranked candidate with evaluation details.
    """
    
    candidate_id: str = Field(
        ...,
        description="Unique identifier for the candidate"
    )
    
    score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Score from 1-5"
    )
    
    summary: str = Field(
        ...,
        description="One-line summary of the answer"
    )
    
    improvement: str = Field(
        ...,
        description="One improvement suggestion"
    )
    
    rank: int = Field(
        ...,
        ge=1,
        description="Rank among all candidates (1 is best)"
    )


class RankingResponse(BaseModel):
    """
    Response model for /rank-candidates endpoint.
    
    Returns all candidates ranked by score.
    """
    
    candidates: List[RankedCandidate] = Field(
        ...,
        description="List of candidates sorted by score (highest first)"
    )
    
    total_candidates: int = Field(
        ...,
        ge=1,
        description="Total number of candidates evaluated"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "candidates": [
                    {
                        "candidate_id": "candidate_001",
                        "score": 5,
                        "summary": "Excellent solution with optimal approach",
                        "improvement": "Could add more edge case handling",
                        "rank": 1
                    },
                    {
                        "candidate_id": "candidate_002",
                        "score": 3,
                        "summary": "Basic understanding but inefficient approach",
                        "improvement": "Study hash map data structures for better time complexity",
                        "rank": 2
                    }
                ],
                "total_candidates": 2
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response for all endpoints.
    """
    
    error: str = Field(
        ...,
        description="Error type or code"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    
    details: dict | None = Field(
        default=None,
        description="Optional additional error details"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Answer must be at least 10 characters",
                "details": {"field": "candidate_answer", "min_length": 10}
            }
        }


class HealthResponse(BaseModel):
    """
    Health check response.
    """
    
    status: str = Field(
        default="healthy",
        description="Service health status"
    )
    
    version: str = Field(
        ...,
        description="API version"
    )
    
    llm_provider: str = Field(
        default="groq",
        description="LLM provider being used"
    )
    
    redis_connected: bool = Field(
        ...,
        description="Redis connection status"
    )

