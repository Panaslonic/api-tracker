"""
Tests for logging configuration
"""

import pytest
import json
import structlog
from unittest.mock import patch, MagicMock
from api_watcher.logging_config import configure_logging, get_logger, setup_from_config


class TestLoggingConfig:
    """Tests for logging configuration"""
    
    def test_get_logger_returns_structlog_logger(self):
        """Test that get_logger returns a structlog logger"""
        configure_logging(log_format="json", log_level="INFO")
        logger = get_logger("test")
        # Logger should be a structlog logger (BoundLoggerLazyProxy or BoundLogger)
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
    
    def test_configure_logging_json_format(self):
        """Test JSON format configuration"""
        configure_logging(log_format="json", log_level="INFO")
        logger = get_logger("test_json")
        # Logger should be configured without errors
        assert logger is not None
    
    def test_configure_logging_console_format(self):
        """Test console format configuration"""
        configure_logging(log_format="console", log_level="DEBUG")
        logger = get_logger("test_console")
        assert logger is not None
    
    @patch('api_watcher.logging_config.sentry_sdk')
    def test_configure_logging_with_sentry(self, mock_sentry):
        """Test Sentry integration"""
        configure_logging(
            log_format="json",
            log_level="INFO",
            sentry_dsn="https://test@sentry.io/123",
            sentry_environment="test"
        )
        # Sentry init should be called
        mock_sentry.init.assert_called_once()
    
    def test_configure_logging_without_sentry(self):
        """Test configuration without Sentry DSN"""
        # Should not raise any errors
        configure_logging(log_format="json", log_level="INFO", sentry_dsn=None)
        logger = get_logger("test_no_sentry")
        assert logger is not None
    
    def test_setup_from_config(self):
        """Test setup from Config class"""
        # Create a mock config class
        class MockConfig:
            LOG_FORMAT = 'json'
            LOG_LEVEL = 'DEBUG'
            SENTRY_DSN = None
            SENTRY_ENVIRONMENT = 'test'
        
        setup_from_config(MockConfig)
        logger = get_logger("test_from_config")
        assert logger is not None
    
    def test_logger_context_binding(self):
        """Test that logger can bind context"""
        configure_logging(log_format="json", log_level="INFO")
        logger = get_logger("test_context")
        
        # Bind context
        bound_logger = logger.bind(request_id="123", user_id="456")
        assert bound_logger is not None
    
    def test_log_levels(self):
        """Test different log levels"""
        configure_logging(log_format="json", log_level="DEBUG")
        logger = get_logger("test_levels")
        
        # Should not raise errors
        logger.debug("debug message", test_field="value")
        logger.info("info message", test_field="value")
        logger.warning("warning message", test_field="value")
        logger.error("error message", test_field="value")
