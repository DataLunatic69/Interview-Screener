"""
LangGraph Node Definitions.

These nodes wrap individual agents and handle state updates
in the LangGraph workflow.
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage

from app.schemas.state import AgentState
from app.agents.evaluator import evaluate_answer_sync
from app.agents.analyzer import analyze_answer_sync
from app.agents.improvement import suggest_improvement_sync
from app.services.logger import get_logger

logger = get_logger(__name__)


def evaluator_node(state: AgentState) -> Dict[str, Any]:
    """
    Evaluator node - scores the candidate answer.
    
    Args:
        state: Current agent state
        
    Returns:
        State updates with evaluator results
    """
    logger.info("Executing evaluator node")
    
    try:
        result = evaluate_answer_sync(
            candidate_answer=state["candidate_answer"],
            question_context=state.get("question_context")
        )
        
        return {
            "evaluator_score": result.score,
            "evaluator_justification": result.justification,
            "current_agent": "evaluator",
            "messages": [HumanMessage(content=f"Score: {result.score}, Justification: {result.justification}")]
        }
    except Exception as e:
        logger.error(f"Evaluator node failed: {str(e)}")
        return {
            "evaluator_score": 3,
            "evaluator_justification": "Evaluation error",
            "error": str(e),
            "current_agent": "evaluator"
        }


def analyzer_node(state: AgentState) -> Dict[str, Any]:
    """
    Analyzer node - analyzes answer for strengths and weaknesses.
    
    Args:
        state: Current agent state
        
    Returns:
        State updates with analyzer results
    """
    logger.info("Executing analyzer node")
    
    try:
        result = analyze_answer_sync(
            candidate_answer=state["candidate_answer"],
            question_context=state.get("question_context"),
            score=state.get("evaluator_score")
        )
        
        return {
            "analyzer_strengths": result.strengths,
            "analyzer_weaknesses": result.weaknesses,
            "final_summary": result.summary,
            "current_agent": "analyzer",
            "messages": [HumanMessage(content=f"Summary: {result.summary}")]
        }
    except Exception as e:
        logger.error(f"Analyzer node failed: {str(e)}")
        return {
            "analyzer_strengths": "Analysis unavailable",
            "analyzer_weaknesses": "Analysis unavailable",
            "final_summary": "Unable to generate summary",
            "error": str(e),
            "current_agent": "analyzer"
        }


def improvement_node(state: AgentState) -> Dict[str, Any]:
    """
    Improvement node - generates improvement suggestions.
    
    Args:
        state: Current agent state
        
    Returns:
        State updates with improvement results
    """
    logger.info("Executing improvement node")
    
    try:
        result = suggest_improvement_sync(
            candidate_answer=state["candidate_answer"],
            question_context=state.get("question_context"),
            score=state.get("evaluator_score"),
            weaknesses=state.get("analyzer_weaknesses")
        )
        
        return {
            "improvement_suggestion": result.suggestion,
            "final_improvement": result.suggestion,
            "current_agent": "improvement",
            "messages": [HumanMessage(content=f"Improvement: {result.suggestion}")]
        }
    except Exception as e:
        logger.error(f"Improvement node failed: {str(e)}")
        return {
            "improvement_suggestion": "Unable to generate suggestion",
            "final_improvement": "Unable to generate suggestion",
            "error": str(e),
            "current_agent": "improvement"
        }


def synthesizer_node(state: AgentState) -> Dict[str, Any]:
    """
    Synthesizer node - combines all agent outputs into final response.
    
    Args:
        state: Current agent state
        
    Returns:
        State updates with final synthesized results
    """
    logger.info("Executing synthesizer node")
    
    try:
        # Ensure we have all required fields
        final_score = state.get("evaluator_score", 3)
        final_summary = state.get("final_summary", "No summary available")
        final_improvement = state.get("final_improvement", "No improvement suggestion available")
        
        # Truncate if needed to meet length requirements
        if len(final_summary) > 200:
            final_summary = final_summary[:197] + "..."
        
        if len(final_improvement) > 300:
            final_improvement = final_improvement[:297] + "..."
        
        return {
            "final_score": final_score,
            "final_summary": final_summary,
            "final_improvement": final_improvement,
            "current_agent": "synthesizer",
            "messages": [HumanMessage(content="Synthesis complete")]
        }
    except Exception as e:
        logger.error(f"Synthesizer node failed: {str(e)}")
        return {
            "final_score": 3,
            "final_summary": "Synthesis error",
            "final_improvement": "Unable to provide feedback",
            "error": str(e),
            "current_agent": "synthesizer"
        }


def should_continue(state: AgentState) -> str:
    """
    Decision function to determine next step in workflow.
    
    Args:
        state: Current agent state
        
    Returns:
        Name of next node to execute or "end"
    """
    current = state.get("current_agent")
    
    if current is None:
        return "evaluator"
    elif current == "evaluator":
        return "analyzer"
    elif current == "analyzer":
        return "improvement"
    elif current == "improvement":
        return "synthesizer"
    elif current == "synthesizer":
        return "end"
    
    return "end"

