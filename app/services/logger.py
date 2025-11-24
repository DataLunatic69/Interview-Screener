"""
Structured logging configuration using Loguru.
Provides consistent, structured logging across the application.
"""
import sys
from loguru import logger

from app.core.config import settings


def configure_logger():
    """
    Configure loguru logger with structured output.
    
    Sets up:
    - Log level from settings
    - Structured JSON format for production
    - Human-readable format for development
    - File rotation and retention
    """
    # Remove default handler
    logger.remove()
    
    # Determine format based on environment
    if settings.environment == "production":
        # Structured JSON logging for production
        log_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message} | "
            "{extra}"
        )
    else:
        # Human-readable for development
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level> | "
            "{extra}"
        )
    
    # Add stdout handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=settings.environment != "production",
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler for errors
    logger.add(
        "logs/error.log",
        format=log_format,
        level="ERROR",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    
    # Add file handler for all logs
    logger.add(
        "logs/app.log",
        format=log_format,
        level=settings.log_level,
        rotation="100 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info(
        f"Logger configured: level={settings.log_level}, "
        f"environment={settings.environment}"
    )


def get_logger(name: str = None):
    """
    Get a logger instance with optional name binding.
    
    Args:
        name: Optional name to bind to logger context
        
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(logger_name=name)
    return logger


# Configure on import
configure_logger()

