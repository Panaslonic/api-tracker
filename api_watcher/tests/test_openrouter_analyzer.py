"""
Тесты для OpenRouter AI Analyzer
"""

import pytest
from unittest.mock import Mock, patch
from api_watcher.utils.openrouter_analyzer import OpenRouterAnalyzer


class TestOpenRouterAnalyzer:
    """Тесты для класса OpenRouterAnalyzer"""
    
    def test_init(self):
        """Тест инициализации"""
        analyzer = OpenRouterAnalyzer(
            api_key="test-key",
            model="anthropic/claude-3.5-sonnet"
        )
        
        assert analyzer.api_key == "test-key"
        assert analyzer.model == "anthropic/claude-3.5-sonnet"
        assert analyzer.api_url == "https://openrouter.ai/api/v1/chat/completions"
    
    @patch('api_watcher.utils.openrouter_analyzer.requests.post')
    def test_make_request_success(self, mock_post):
        """Тест успешного запроса к OpenRouter"""
        # Мокаем ответ
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'Test response'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        analyzer = OpenRouterAnalyzer(api_key="test-key")
        result = analyzer._make_request([{"role": "user", "content": "test"}])
        
        assert result == 'Test response'
        assert mock_post.called
    
    @patch('api_watcher.utils.openrouter_analyzer.requests.post')
    def test_make_request_failure(self, mock_post):
        """Тест неудачного запроса"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        analyzer = OpenRouterAnalyzer(api_key="test-key")
        result = analyzer._make_request([{"role": "user", "content": "test"}])
        
        assert result is None
    
    @patch.object(OpenRouterAnalyzer, '_make_request')
    def test_analyze_changes_with_json_response(self, mock_request):
        """Тест анализа изменений с JSON ответом"""
        mock_request.return_value = '''```json
{
    "has_significant_changes": true,
    "summary": "Добавлен новый параметр",
    "severity": "moderate",
    "key_changes": ["Новый параметр: email"]
}
```'''
        
        analyzer = OpenRouterAnalyzer(api_key="test-key")
        result = analyzer.analyze_changes(
            "old text",
            "new text",
            "Test API"
        )
        
        assert result['has_significant_changes'] is True
        assert result['summary'] == "Добавлен новый параметр"
        assert result['severity'] == "moderate"
        assert len(result['key_changes']) == 1
    
    @patch.object(OpenRouterAnalyzer, '_make_request')
    def test_analyze_changes_without_ai(self, mock_request):
        """Тест анализа когда AI недоступен"""
        mock_request.return_value = None
        
        analyzer = OpenRouterAnalyzer(api_key="test-key")
        result = analyzer.analyze_changes(
            "old text",
            "new text",
            "Test API"
        )
        
        assert result['has_significant_changes'] is True
        assert 'AI анализ недоступен' in result['summary']
        assert result['severity'] == 'moderate'
    
    @patch.object(OpenRouterAnalyzer, '_make_request')
    def test_analyze_openapi_changes(self, mock_request):
        """Тест анализа OpenAPI изменений"""
        mock_request.return_value = "Добавлен новый endpoint GET /users"
        
        analyzer = OpenRouterAnalyzer(api_key="test-key")
        changes = {
            'added': ['paths./users.get'],
            'removed': [],
            'modified': []
        }
        
        result = analyzer.analyze_openapi_changes(changes, "Test API")
        
        assert result == "Добавлен новый endpoint GET /users"
        assert mock_request.called
    
    @patch.object(OpenRouterAnalyzer, '_make_request')
    def test_analyze_openapi_changes_fallback(self, mock_request):
        """Тест fallback для OpenAPI анализа"""
        mock_request.return_value = None
        
        analyzer = OpenRouterAnalyzer(api_key="test-key")
        changes = {
            'added': ['path1', 'path2'],
            'removed': ['path3'],
            'modified': []
        }
        
        result = analyzer.analyze_openapi_changes(changes, "Test API")
        
        assert "Добавлено: 2 элементов" in result
        assert "Удалено: 1 элементов" in result
    
    def test_get_model_info(self):
        """Тест получения информации о модели"""
        analyzer = OpenRouterAnalyzer(
            api_key="test-key",
            model="anthropic/claude-3.5-sonnet"
        )
        
        info = analyzer.get_model_info()
        
        assert info['model'] == "anthropic/claude-3.5-sonnet"
        assert info['provider'] == "OpenRouter"
        assert 'api_url' in info


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
