"""
Request schemas for API endpoints.
Provides validation and documentation for incoming requests.
"""
from typing import List

from pydantic import BaseModel, Field, validator


class EvaluateAnswerRequest(BaseModel):
    """
    Request model for /evaluate-answer endpoint.
    
    Evaluates a single candidate's answer.
    """
    
    candidate_answer: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The candidate's answer to evaluate",
        examples=["I would use a hash map to solve this problem because..."]
    )
    
    question_context: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional: The question that was asked",
        examples=["Explain how you would optimize a database query"]
    )
    
    @validator("candidate_answer")
    def validate_answer(cls, v):
        """Ensure answer is meaningful."""
        if len(v.strip()) < 10:
            raise ValueError("Answer must be at least 10 characters")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "candidate_answer": "I would use a hash map to solve this problem because it provides O(1) lookup time. First, I'd iterate through the array once to build the hash map, then check for the complement of each element.",
                "question_context": "How would you find two numbers in an array that sum to a target value?"
            }
        }


class CandidateAnswer(BaseModel):
    """
    Single candidate answer for ranking.
    """
    
    candidate_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique identifier for the candidate",
        examples=["candidate_001", "john_doe_2024"]
    )
    
    answer: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="The candidate's answer",
        examples=["I would approach this by..."]
    )
    
    @validator("answer")
    def validate_answer(cls, v):
        """Ensure answer is meaningful."""
        if len(v.strip()) < 10:
            raise ValueError("Answer must be at least 10 characters")
        return v.strip()


class RankCandidatesRequest(BaseModel):
    """
    Request model for /rank-candidates endpoint.
    
    Ranks multiple candidates based on their answers.
    """
    
    candidates: List[CandidateAnswer] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of candidate answers to rank"
    )
    
    question_context: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional: The question that was asked"
    )
    
    @validator("candidates")
    def validate_candidates(cls, v):
        """Ensure unique candidate IDs."""
        candidate_ids = [c.candidate_id for c in v]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("Candidate IDs must be unique")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "candidates": [
                    {
                        "candidate_id": "candidate_001",
                        "answer": "I would use a hash map for O(1) lookups..."
                    },
                    {
                        "candidate_id": "candidate_002",
                        "answer": "A nested loop would work but it's O(n²)..."
                    }
                ],
                "question_context": "Find two numbers that sum to target"
            }
        }