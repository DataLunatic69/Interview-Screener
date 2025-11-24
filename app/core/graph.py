"""
LangGraph Workflow Construction.

Builds the multi-agent evaluation workflow using LangGraph.
"""
from langgraph.graph import StateGraph, END
from functools import lru_cache

from app.schemas.state import AgentState
from app.agents.nodes import (
    evaluator_node,
    analyzer_node,
    improvement_node,
    synthesizer_node,
    should_continue
)
from app.services.logger import get_logger

logger = get_logger(__name__)


@lru_cache()
def build_evaluation_graph():
    """
    Build the LangGraph evaluation workflow.
    
    Workflow:
    1. Evaluator: Score the answer (1-5)
    2. Analyzer: Analyze strengths/weaknesses and create summary
    3. Improvement: Generate improvement suggestion
    4. Synthesizer: Combine results into final output
    
    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Building evaluation graph")
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("improvement", improvement_node)
    workflow.add_node("synthesizer", synthesizer_node)
    
    # Set entry point
    workflow.set_entry_point("evaluator")
    
    # Add edges (sequential workflow)
    workflow.add_edge("evaluator", "analyzer")
    workflow.add_edge("analyzer", "improvement")
    workflow.add_edge("improvement", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("Evaluation graph compiled successfully")
    return app


def get_evaluation_graph():
    """
    Get the cached evaluation graph.
    
    Returns:
        Compiled evaluation graph
    """
    return build_evaluation_graph()


# Export the graph
evaluation_graph = get_evaluation_graph()

