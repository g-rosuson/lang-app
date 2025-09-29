"""
This module provides a unified logging setup that can be used across the entire
application. It configures loggers with appropriate formatting, levels, and
handlers for both development, production, test environments.

The logging configuration includes:
- Structured logging with timestamps and module names
- Different log levels for different environments
- Console output only (no file logging)
- Proper formatting for readability and parsing
"""

import logging
from typing import Optional
import sys
import os

def __setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> logging.Logger:
    """
    Set up centralized logging configuration for the application.
    
    This function configures the root logger with appropriate handlers,
    formatters, and levels. It can be customized for different environments
    by adjusting the parameters.
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string (Optional[str]): Custom format string for log messages
        
    Returns:
        logging.Logger: The configured root logger
        
    Example:
        >>> logger = setup_logging(level="DEBUG")
        >>> logger.info("Application started")
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Default format string
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger



def __configure_third_party_loggers() -> None:
    """
    Configure logging levels for third-party libraries.
    
    This function sets appropriate logging levels for external libraries
    to reduce noise in the application logs. It can be customized based
    on the specific libraries used and the desired verbosity.
    """
    # Reduce verbosity of third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # PyTorch/ML libraries
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("tokenizers").setLevel(logging.WARNING)
    
    # LanguageTool
    logging.getLogger("language_tool_python").setLevel(logging.WARNING)

    # Stanza
    logging.getLogger("stanza").setLevel(logging.WARNING)
    
    # FastAPI/Uvicorn
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    # File watcher (watchfiles) - suppress debug messages about file changes
    # The watchfiles library generates DEBUG level logs for every file change
    # it detects during auto-reload. These logs are noisy and not useful for
    # application debugging, so we suppress them by setting the level to WARNING.
    # This includes logs like "3 changes detected" and "1 change detected" that
    # appear when Python cache files or model files are created/modified.
    logging.getLogger("watchfiles").setLevel(logging.WARNING)


def __setup_dev_logging() -> logging.Logger:
    """
    Set up logging configuration for development environment.
    
    This function configures logging with more verbose output suitable
    for development, including DEBUG level logging and console output.
    
    Returns:
        logging.Logger: Configured logger for development
    """
    logger = __setup_logging(
        level="DEBUG",
        format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    __configure_third_party_loggers()

    logger.info("Development logging configured")

    return logger


def __setup_prod_logging() -> logging.Logger:
    """
    Set up logging configuration for production environment.
    
    This function configures logging with appropriate settings for production,
    including INFO level logging and reduced third-party verbosity.
    
    Returns:
        logging.Logger: Configured logger for production
    """
    logger = __setup_logging(
        level="INFO",
        format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    __configure_third_party_loggers()

    logger.info("Production logging configured")
    
    return logger


def __setup_test_logging() -> logging.Logger:
    """
    Set up logging configuration for testing environment.
    
    This function configures logging with minimal output suitable for testing,
    focusing on errors and warnings while suppressing most informational messages.
    
    Returns:
        logging.Logger: Configured logger for testing
    """
    logger = __setup_logging(
        level="WARNING",
        format_string="%(levelname)s - %(name)s - %(message)s"
    )

    __configure_third_party_loggers()

    return logger


def __get_logging_for_environment() -> logging.Logger:
    """
    Set up logging based on the specified environment.
    
    This function provides a convenient way to set up logging based on
    the current environment (development, production, testing).
    """

    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "development":
        return __setup_dev_logging()
    elif environment == "production":
        return __setup_prod_logging()
    elif environment == "test":
        return __setup_test_logging()
    else:
        raise ValueError(f"Unknown environment: {environment}")


def get_logger(moduleName: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    This function creates a logger with the specified name, which will
    inherit the configuration from the root logger. This is the recommended
    way to get loggers throughout the application.
    """

    # Configures the global root logger
    __get_logging_for_environment()

    # Get child logger from global root logger
    return logging.getLogger(moduleName)