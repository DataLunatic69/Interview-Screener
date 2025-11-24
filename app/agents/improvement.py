"""
Improvement Agent - Provides actionable improvement suggestions.

This agent specializes in generating specific, actionable feedback
to help candidates improve their interview performance.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.llm import get_langchain_llm
from app.services.logger import get_logger

logger = get_logger(__name__)


class ImprovementOutput(BaseModel):
    """Structured output from the Improvement Agent."""
    suggestion: str = Field(
        ...,
        description="One specific, actionable improvement suggestion"
    )


IMPROVEMENT_SYSTEM_PROMPT = """You are an expert technical interviewer providing constructive feedback.

Your task is to provide ONE specific, actionable improvement suggestion.

Guidelines:
- Be **specific** and **actionable** (not generic like "study more")
- Focus on the most impactful improvement
- Keep it concise (max 300 characters)
- Make it constructive and encouraging
- Suggest concrete next steps or concepts to learn

Examples of GOOD suggestions:
- "Consider analyzing space complexity alongside time complexity - your O(n) time solution also uses O(n) space for the hash map"
- "Mention edge cases like empty arrays or negative numbers to show comprehensive thinking"
- "Study the difference between BFS and DFS - your solution would benefit from BFS for shortest path"

Examples of BAD suggestions:
- "Study algorithms more" (too generic)
- "Your answer is wrong" (not constructive)
- "Perfect, no improvements needed" (not helpful)

Respond ONLY with valid JSON in this exact format:
{
    "suggestion": "<one specific improvement suggestion>"
}"""


async def suggest_improvement(
    candidate_answer: str,
    question_context: str | None = None,
    score: int | None = None,
    weaknesses: str | None = None
) -> ImprovementOutput:
    """
    Generate an improvement suggestion for a candidate answer.
    
    Args:
        candidate_answer: The candidate's response
        question_context: Optional context about the question asked
        score: Optional score from evaluator for context
        weaknesses: Optional weaknesses identified by analyzer
        
    Returns:
        ImprovementOutput with suggestion
    """
    logger.info(f"Generating improvement suggestion (score={score})")
    
    llm = get_langchain_llm()
    parser = JsonOutputParser(pydantic_object=ImprovementOutput)
    
    # Build the user message
    user_content = f"Candidate's Answer:\n{candidate_answer}"
    if question_context:
        user_content = f"Question: {question_context}\n\n{user_content}"
    if score:
        user_content += f"\n\nEvaluator Score: {score}/5"
    if weaknesses:
        user_content += f"\n\nIdentified Weaknesses: {weaknesses}"
    
    messages = [
        SystemMessage(content=IMPROVEMENT_SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]
    
    try:
        response = await llm.ainvoke(messages)
        parsed = parser.parse(response.content)
        
        result = ImprovementOutput(**parsed)
        logger.info("Improvement suggestion generated")
        return result
        
    except Exception as e:
        logger.error(f"Improvement suggestion failed: {str(e)}")
        # Fallback with generic suggestion
        return ImprovementOutput(
            suggestion="Review the question requirements and ensure your answer addresses all key points with specific examples."
        )


def suggest_improvement_sync(
    candidate_answer: str,
    question_context: str | None = None,
    score: int | None = None,
    weaknesses: str | None = None
) -> ImprovementOutput:
    """
    Synchronous version of suggest_improvement.
    
    Args:
        candidate_answer: The candidate's response
        question_context: Optional context about the question asked
        score: Optional score from evaluator for context
        weaknesses: Optional weaknesses identified by analyzer
        
    Returns:
        ImprovementOutput with suggestion
    """
    logger.info(f"Generating improvement suggestion (sync, score={score})")
    
    llm = get_langchain_llm()
    parser = JsonOutputParser(pydantic_object=ImprovementOutput)
    
    # Build the user message
    user_content = f"Candidate's Answer:\n{candidate_answer}"
    if question_context:
        user_content = f"Question: {question_context}\n\n{user_content}"
    if score:
        user_content += f"\n\nEvaluator Score: {score}/5"
    if weaknesses:
        user_content += f"\n\nIdentified Weaknesses: {weaknesses}"
    
    messages = [
        SystemMessage(content=IMPROVEMENT_SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]
    
    try:
        response = llm.invoke(messages)
        parsed = parser.parse(response.content)
        
        result = ImprovementOutput(**parsed)
        logger.info("Improvement suggestion generated")
        return result
        
    except Exception as e:
        logger.error(f"Improvement suggestion failed: {str(e)}")
        # Fallback with generic suggestion
        return ImprovementOutput(
            suggestion="Review the question requirements and ensure your answer addresses all key points with specific examples."
        )

