"""
LangGraph state definitions.
Defines the state structure for the multi-agent workflow.
"""
from typing import TypedDict, Annotated, Sequence
from operator import add

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    State shared across all agents in the LangGraph workflow.
    
    This state is passed between nodes and updated as agents execute.
    """
    
    # Input
    candidate_answer: str
    question_context: str | None
    
    # Agent outputs
    evaluator_score: int | None
    evaluator_justification: str | None
    
    analyzer_strengths: str | None
    analyzer_weaknesses: str | None
    
    improvement_suggestion: str | None
    
    # Final output
    final_score: int | None
    final_summary: str | None
    final_improvement: str | None
    
    # Metadata
    messages: Annotated[Sequence[BaseMessage], add]
    current_agent: str | None
    error: str | None
    cached: bool


class EvaluatorOutput(TypedDict):
    """Output from the Evaluator Agent."""
    score: int
    justification: str


class AnalyzerOutput(TypedDict):
    """Output from the Analyzer Agent."""
    strengths: str
    weaknesses: str


class ImprovementOutput(TypedDict):
    """Output from the Improvement Agent."""
    suggestion: str


class SupervisorDecision(TypedDict):
    """Decision from the Supervisor Agent."""
    next_agent: str  # "evaluator", "analyzer", "improvement", "synthesize", "end"
    reason: str