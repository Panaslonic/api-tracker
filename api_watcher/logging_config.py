"""
Logging configuration for API Watcher
Provides structured logging with JSON output and optional Sentry integration
"""

import os
import sys
import logging
from typing import Any

import structlog
from structlog.types import EventDict, Processor

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to log events"""
    event_dict["app"] = "api_watcher"
    return event_dict


def configure_logging(
    log_format: str = "json",
    log_level: str = "INFO",
    sentry_dsn: str = None,
    sentry_environment: str = "production"
) -> None:
    """
    Configure structured logging with structlog and optional Sentry
    
    Args:
        log_format: 'json' for JSON output, 'console' for human-readable output
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        sentry_dsn: Sentry DSN for error tracking (optional)
        sentry_environment: Sentry environment name
    """
    
    # Configure Sentry if DSN is provided
    if sentry_dsn and SENTRY_AVAILABLE:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors and above as events
        )
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=sentry_environment,
            integrations=[sentry_logging],
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,
        )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    
    # Shared processors for both formats
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_app_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
    ]
    
    # Choose renderer based on format
    if log_format == "json":
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ]
    else:  # console format
        processors = shared_processors + [
            structlog.processors.ExceptionRenderer(),
            structlog.dev.ConsoleRenderer()
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def setup_from_config(config_class: Any = None) -> None:
    """
    Setup logging from Config class
    
    Args:
        config_class: Config class with logging settings
    """
    if config_class is None:
        from api_watcher.config import Config
        config_class = Config
    
    log_format = getattr(config_class, 'LOG_FORMAT', 'json')
    log_level = getattr(config_class, 'LOG_LEVEL', 'INFO')
    sentry_dsn = getattr(config_class, 'SENTRY_DSN', None)
    sentry_env = getattr(config_class, 'SENTRY_ENVIRONMENT', 'production')
    
    configure_logging(
        log_format=log_format,
        log_level=log_level,
        sentry_dsn=sentry_dsn,
        sentry_environment=sentry_env
    )
