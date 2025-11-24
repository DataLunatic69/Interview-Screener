"""
Evaluator Agent - Scores candidate answers from 1-5.

This agent specializes in objective evaluation and scoring,
analyzing technical accuracy, clarity, and completeness.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.core.llm import get_langchain_llm
from app.services.logger import get_logger

logger = get_logger(__name__)


class EvaluatorOutput(BaseModel):
    """Structured output from the Evaluator Agent."""
    score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Score from 1-5 where 1=poor, 3=average, 5=excellent"
    )
    justification: str = Field(
        ...,
        description="Brief justification for the score"
    )


EVALUATOR_SYSTEM_PROMPT = """You are an expert technical interviewer evaluating candidate answers.

Your task is to score the candidate's answer on a scale of 1-5:
- **5**: Exceptional - Demonstrates deep understanding, optimal solution, considers edge cases
- **4**: Strong - Correct approach with good explanation, minor gaps
- **3**: Average - Basic understanding, workable solution, but lacks depth
- **2**: Weak - Shows some knowledge but significant gaps or errors
- **1**: Poor - Incorrect or demonstrates lack of understanding

Consider:
1. **Technical Accuracy**: Is the answer technically correct?
2. **Clarity**: Is the explanation clear and well-structured?
3. **Completeness**: Does it address all aspects of the question?
4. **Depth**: Does it show deep understanding or just surface knowledge?

Respond ONLY with valid JSON in this exact format:
{
    "score": <number 1-5>,
    "justification": "<brief explanation of the score>"
}"""


async def evaluate_answer(
    candidate_answer: str,
    question_context: str | None = None
) -> EvaluatorOutput:
    """
    Evaluate a candidate answer and assign a score.
    
    Args:
        candidate_answer: The candidate's response
        question_context: Optional context about the question asked
        
    Returns:
        EvaluatorOutput with score and justification
    """
    logger.info(f"Evaluating answer (length={len(candidate_answer)})")
    
    llm = get_langchain_llm()
    parser = JsonOutputParser(pydantic_object=EvaluatorOutput)
    
    # Build the user message
    user_content = f"Candidate's Answer:\n{candidate_answer}"
    if question_context:
        user_content = f"Question: {question_context}\n\n{user_content}"
    
    messages = [
        SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]
    
    try:
        response = await llm.ainvoke(messages)
        parsed = parser.parse(response.content)
        
        result = EvaluatorOutput(**parsed)
        logger.info(f"Evaluation complete: score={result.score}")
        return result
        
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        # Fallback to neutral score on error
        return EvaluatorOutput(
            score=3,
            justification=f"Evaluation error occurred: {str(e)[:100]}"
        )


def evaluate_answer_sync(
    candidate_answer: str,
    question_context: str | None = None
) -> EvaluatorOutput:
    """
    Synchronous version of evaluate_answer.
    
    Args:
        candidate_answer: The candidate's response
        question_context: Optional context about the question asked
        
    Returns:
        EvaluatorOutput with score and justification
    """
    logger.info(f"Evaluating answer (sync, length={len(candidate_answer)})")
    
    llm = get_langchain_llm()
    parser = JsonOutputParser(pydantic_object=EvaluatorOutput)
    
    # Build the user message
    user_content = f"Candidate's Answer:\n{candidate_answer}"
    if question_context:
        user_content = f"Question: {question_context}\n\n{user_content}"
    
    messages = [
        SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]
    
    try:
        response = llm.invoke(messages)
        parsed = parser.parse(response.content)
        
        result = EvaluatorOutput(**parsed)
        logger.info(f"Evaluation complete: score={result.score}")
        return result
        
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        # Fallback to neutral score on error
        return EvaluatorOutput(
            score=3,
            justification=f"Evaluation error occurred: {str(e)[:100]}"
        )

