"""
LLM client initialization and management.
Handles Groq API client creation with proper configuration.
"""
from functools import lru_cache

from langchain_groq import ChatGroq

from app.core.config import settings
from app.services.logger import get_logger

logger = get_logger(__name__)


@lru_cache()
def get_langchain_llm() -> ChatGroq:
    """
    Get cached LangChain-compatible Groq instance.
    
    This is the primary LLM instance used by LangGraph agents.
    
    Returns:
        Configured ChatGroq instance
    """
    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Please set it in your environment variables. "
            "Get your API key from https://console.groq.com"
        )
    
    logger.info(
        f"Initializing LangChain LLM: model={settings.llm_model}, "
        f"temperature={settings.llm_temperature}, max_tokens={settings.llm_max_tokens}"
    )
    
    return ChatGroq(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        groq_api_key=settings.groq_api_key,
    )


class LLMManager:
    """
    Centralized LLM management with helper methods.
    
    Provides convenience methods for common LLM operations
    with built-in error handling and logging.
    """
    
    def __init__(self):
        self.llm = get_langchain_llm()
    
    async def ainvoke(self, prompt: str, **kwargs) -> str:
        """
        Async invoke LLM with prompt.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional LLM parameters
            
        Returns:
            LLM response as string
        """
        try:
            response = await self.llm.ainvoke(prompt, **kwargs)
            logger.debug(f"LLM invoked successfully, prompt_length={len(prompt)}")
            return response.content
        except Exception as e:
            logger.error(f"LLM invocation failed: {str(e)}, prompt={prompt[:100]}")
            raise
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """
        Sync invoke LLM with prompt.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional LLM parameters
            
        Returns:
            LLM response as string
        """
        try:
            response = self.llm.invoke(prompt, **kwargs)
            logger.debug(f"LLM invoked successfully, prompt_length={len(prompt)}")
            return response.content
        except Exception as e:
            logger.error(f"LLM invocation failed: {str(e)}, prompt={prompt[:100]}")
            raise


@lru_cache()
def get_llm_manager() -> LLMManager:
    """
    Get cached LLM manager instance.
    
    Returns:
        LLMManager instance
    """
    return LLMManager()


# Export for convenience
llm_manager = get_llm_manager()
llm = get_langchain_llm()