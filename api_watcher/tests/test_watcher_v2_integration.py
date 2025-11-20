"""
Интеграционные тесты для Watcher V2
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from api_watcher.watcher_v2 import APIWatcherV2


class TestAPIWatcherV2Integration:
    """Интеграционные тесты для APIWatcherV2"""
    
    @patch('api_watcher.watcher_v2.DatabaseManager')
    @patch('api_watcher.watcher_v2.Config')
    def test_init_minimal(self, mock_config, mock_db):
        """Тест инициализации с минимальной конфигурацией"""
        mock_config.DATABASE_URL = 'sqlite:///test.db'
        mock_config.is_zenrows_configured.return_value = False
        mock_config.is_openrouter_configured.return_value = False
        mock_config.is_gemini_configured.return_value = False
        mock_config.is_slack_configured.return_value = False
        mock_config.is_webhook_configured.return_value = False
        
        watcher = APIWatcherV2()
        
        assert watcher.zenrows is None
        assert watcher.ai_analyzer is None
        assert watcher.slack is None
        assert watcher.webhook is None
    
    @patch('api_watcher.watcher_v2.DatabaseManager')
    @patch('api_watcher.watcher_v2.Config')
    @patch('api_watcher.watcher_v2.OpenRouterAnalyzer')
    def test_init_with_openrouter(self, mock_analyzer, mock_config, mock_db):
        """Тест инициализации с OpenRouter"""
        mock_config.DATABASE_URL = 'sqlite:///test.db'
        mock_config.is_zenrows_configured.return_value = False
        mock_config.is_openrouter_configured.return_value = True
        mock_config.OPENROUTER_API_KEY = 'test-key'
        mock_config.OPENROUTER_MODEL = 'test-model'
        mock_config.OPENROUTER_SITE_URL = None
        mock_config.OPENROUTER_APP_NAME = 'Test'
        mock_config.is_gemini_configured.return_value = False
        mock_config.is_slack_configured.return_value = False
        mock_config.is_webhook_configured.return_value = False
        
        watcher = APIWatcherV2()
        
        assert watcher.ai_analyzer is not None
        assert mock_analyzer.called
    
    @patch('api_watcher.watcher_v2.DatabaseManager')
    @patch('api_watcher.watcher_v2.Config')
    def test_is_valid_response_valid(self, mock_config, mock_db):
        """Тест проверки валидного ответа"""
        mock_config.DATABASE_URL = 'sqlite:///test.db'
        mock_config.is_zenrows_configured.return_value = False
        mock_config.is_openrouter_configured.return_value = False
        mock_config.is_gemini_configured.return_value = False
        mock_config.is_slack_configured.return_value = False
        mock_config.is_webhook_configured.return_value = False
        
        watcher = APIWatcherV2()
        
        # Валидный контент
        valid_content = "A" * 200  # Длинный контент
        assert watcher._is_valid_response(valid_content, "https://test.com") is True
    
    @patch('api_watcher.watcher_v2.DatabaseManager')
    @patch('api_watcher.watcher_v2.Config')
    def test_is_valid_response_invalid_short(self, mock_config, mock_db):
        """Тест проверки короткого ответа"""
        mock_config.DATABASE_URL = 'sqlite:///test.db'
        mock_config.is_zenrows_configured.return_value = False
        mock_config.is_openrouter_configured.return_value = False
        mock_config.is_gemini_configured.return_value = False
        mock_config.is_slack_configured.return_value = False
        mock_config.is_webhook_configured.return_value = False
        
        watcher = APIWatcherV2()
        
        # Короткий контент
        short_content = "Short"
        assert watcher._is_valid_response(short_content, "https://test.com") is False
    
    @patch('api_watcher.watcher_v2.DatabaseManager')
    @patch('api_watcher.watcher_v2.Config')
    def test_is_valid_response_invalid_error(self, mock_config, mock_db):
        """Тест проверки ответа с ошибкой"""
        mock_config.DATABASE_URL = 'sqlite:///test.db'
        mock_config.is_zenrows_configured.return_value = False
        mock_config.is_openrouter_configured.return_value = False
        mock_config.is_gemini_configured.return_value = False
        mock_config.is_slack_configured.return_value = False
        mock_config.is_webhook_configured.return_value = False
        
        watcher = APIWatcherV2()
        
        # Контент с ошибкой
        error_content = "404 Not Found - Page not found" * 10
        assert watcher._is_valid_response(error_content, "https://test.com") is False
    
    @patch('api_watcher.watcher_v2.DatabaseManager')
    @patch('api_watcher.watcher_v2.Config')
    def test_detect_content_type_openapi(self, mock_config, mock_db):
        """Тест определения типа контента OpenAPI"""
        mock_config.DATABASE_URL = 'sqlite:///test.db'
        mock_config.is_zenrows_configured.return_value = False
        mock_config.is_openrouter_configured.return_value = False
        mock_config.is_gemini_configured.return_value = False
        mock_config.is_slack_configured.return_value = False
        mock_config.is_webhook_configured.return_value = False
        
        watcher = APIWatcherV2()
        
        # OpenAPI контент
        openapi_content = '{"openapi": "3.0.0", "info": {}}'
        content_type = watcher.detect_content_type(
            "https://api.test.com/openapi.json",
            openapi_content
        )
        
        assert content_type == 'openapi'
    
    @patch('api_watcher.watcher_v2.DatabaseManager')
    @patch('api_watcher.watcher_v2.Config')
    def test_detect_content_type_json(self, mock_config, mock_db):
        """Тест определения типа контента JSON"""
        mock_config.DATABASE_URL = 'sqlite:///test.db'
        mock_config.is_zenrows_configured.return_value = False
        mock_config.is_openrouter_configured.return_value = False
        mock_config.is_gemini_configured.return_value = False
        mock_config.is_slack_configured.return_value = False
        mock_config.is_webhook_configured.return_value = False
        
        watcher = APIWatcherV2()
        
        # JSON контент
        json_content = '{"data": "value"}'
        content_type = watcher.detect_content_type(
            "https://api.test.com/data.json",
            json_content
        )
        
        assert content_type == 'json'
    
    @patch('api_watcher.watcher_v2.DatabaseManager')
    @patch('api_watcher.watcher_v2.Config')
    def test_detect_content_type_html(self, mock_config, mock_db):
        """Тест определения типа контента HTML"""
        mock_config.DATABASE_URL = 'sqlite:///test.db'
        mock_config.is_zenrows_configured.return_value = False
        mock_config.is_openrouter_configured.return_value = False
        mock_config.is_gemini_configured.return_value = False
        mock_config.is_slack_configured.return_value = False
        mock_config.is_webhook_configured.return_value = False
        
        watcher = APIWatcherV2()
        
        # HTML контент
        html_content = '<html><body>Test</body></html>'
        content_type = watcher.detect_content_type(
            "https://api.test.com/docs",
            html_content
        )
        
        assert content_type == 'html'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
