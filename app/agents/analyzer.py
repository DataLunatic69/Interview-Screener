"""
Analyzer Agent - Analyzes answer quality and identifies key points.

This agent provides detailed analysis of strengths and weaknesses,
helping to create comprehensive summaries.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.llm import get_langchain_llm
from app.services.logger import get_logger

logger = get_logger(__name__)


class AnalyzerOutput(BaseModel):
    """Structured output from the Analyzer Agent."""
    strengths: str = Field(
        ...,
        description="Key strengths identified in the answer"
    )
    weaknesses: str = Field(
        ...,
        description="Key weaknesses or gaps in the answer"
    )
    summary: str = Field(
        ...,
        description="One-line summary capturing the essence of the answer"
    )


ANALYZER_SYSTEM_PROMPT = """You are an expert technical interviewer analyzing candidate answers.

Your task is to provide a balanced analysis identifying:
1. **Strengths**: What the candidate did well (technical accuracy, clarity, approach)
2. **Weaknesses**: What could be improved or what's missing
3. **Summary**: A concise one-line summary (max 200 characters) capturing the essence of the answer

Be specific and actionable. Focus on technical content, not style.

Respond ONLY with valid JSON in this exact format:
{
    "strengths": "<specific strengths>",
    "weaknesses": "<specific weaknesses or gaps>",
    "summary": "<one-line summary, max 200 chars>"
}"""


async def analyze_answer(
    candidate_answer: str,
    question_context: str | None = None,
    score: int | None = None
) -> AnalyzerOutput:
    """
    Analyze a candidate answer for strengths and weaknesses.
    
    Args:
        candidate_answer: The candidate's response
        question_context: Optional context about the question asked
        score: Optional score from evaluator for context
        
    Returns:
        AnalyzerOutput with strengths, weaknesses, and summary
    """
    logger.info(f"Analyzing answer (length={len(candidate_answer)}, score={score})")
    
    llm = get_langchain_llm()
    parser = JsonOutputParser(pydantic_object=AnalyzerOutput)
    
    # Build the user message
    user_content = f"Candidate's Answer:\n{candidate_answer}"
    if question_context:
        user_content = f"Question: {question_context}\n\n{user_content}"
    if score:
        user_content += f"\n\nEvaluator Score: {score}/5"
    
    messages = [
        SystemMessage(content=ANALYZER_SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]
    
    try:
        response = await llm.ainvoke(messages)
        parsed = parser.parse(response.content)
        
        result = AnalyzerOutput(**parsed)
        logger.info("Analysis complete")
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        # Fallback with generic analysis
        return AnalyzerOutput(
            strengths="Unable to analyze strengths",
            weaknesses="Unable to analyze weaknesses",
            summary="Analysis unavailable due to error"
        )


def analyze_answer_sync(
    candidate_answer: str,
    question_context: str | None = None,
    score: int | None = None
) -> AnalyzerOutput:
    """
    Synchronous version of analyze_answer.
    
    Args:
        candidate_answer: The candidate's response
        question_context: Optional context about the question asked
        score: Optional score from evaluator for context
        
    Returns:
        AnalyzerOutput with strengths, weaknesses, and summary
    """
    logger.info(f"Analyzing answer (sync, length={len(candidate_answer)}, score={score})")
    
    llm = get_langchain_llm()
    parser = JsonOutputParser(pydantic_object=AnalyzerOutput)
    
    # Build the user message
    user_content = f"Candidate's Answer:\n{candidate_answer}"
    if question_context:
        user_content = f"Question: {question_context}\n\n{user_content}"
    if score:
        user_content += f"\n\nEvaluator Score: {score}/5"
    
    messages = [
        SystemMessage(content=ANALYZER_SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]
    
    try:
        response = llm.invoke(messages)
        parsed = parser.parse(response.content)
        
        result = AnalyzerOutput(**parsed)
        logger.info("Analysis complete")
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        # Fallback with generic analysis
        return AnalyzerOutput(
            strengths="Unable to analyze strengths",
            weaknesses="Unable to analyze weaknesses",
            summary="Analysis unavailable due to error"
        )

