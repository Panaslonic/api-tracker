"""
Тесты для Webhook Notifier
"""

import pytest
from unittest.mock import Mock, patch
from api_watcher.notifier.webhook_notifier import WebhookNotifier


class TestWebhookNotifier:
    """Тесты для класса WebhookNotifier"""
    
    def test_init(self):
        """Тест инициализации"""
        notifier = WebhookNotifier("https://example.com/webhook")
        
        assert notifier.webhook_url == "https://example.com/webhook"
        assert notifier.timeout == 10
    
    @patch('api_watcher.notifier.webhook_notifier.requests.post')
    def test_send_change_notification_success(self, mock_post):
        """Тест успешной отправки уведомления об изменениях"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        notifier = WebhookNotifier("https://example.com/webhook")
        result = notifier.send_change_notification(
            api_name="Test API",
            method_name="Get Users",
            url="https://api.test.com/docs",
            summary="Изменения обнаружены",
            severity="moderate",
            key_changes=["Новый параметр"]
        )
        
        assert result is True
        assert mock_post.called
        
        # Проверяем payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert payload['event'] == 'api_change_detected'
        assert payload['data']['api_name'] == "Test API"
        assert payload['data']['severity'] == "moderate"
    
    @patch('api_watcher.notifier.webhook_notifier.requests.post')
    def test_send_change_notification_failure(self, mock_post):
        """Тест неудачной отправки"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        notifier = WebhookNotifier("https://example.com/webhook")
        result = notifier.send_change_notification(
            api_name="Test API",
            method_name=None,
            url="https://api.test.com/docs",
            summary="Test",
            severity="minor"
        )
        
        assert result is False
    
    @patch('api_watcher.notifier.webhook_notifier.requests.post')
    def test_send_weekly_digest_success(self, mock_post):
        """Тест отправки еженедельной сводки"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        notifier = WebhookNotifier("https://example.com/webhook")
        changes = [
            {
                'api_name': 'API 1',
                'summary': 'Change 1'
            },
            {
                'api_name': 'API 2',
                'summary': 'Change 2'
            }
        ]
        
        result = notifier.send_weekly_digest(changes)
        
        assert result is True
        
        # Проверяем payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert payload['event'] == 'weekly_digest'
        assert payload['data']['total_changes'] == 2
    
    @patch('api_watcher.notifier.webhook_notifier.requests.post')
    def test_send_weekly_digest_empty(self, mock_post):
        """Тест отправки пустой сводки"""
        notifier = WebhookNotifier("https://example.com/webhook")
        result = notifier.send_weekly_digest([])
        
        assert result is True
        assert not mock_post.called
    
    @patch('api_watcher.notifier.webhook_notifier.requests.post')
    def test_send_documentation_update(self, mock_post):
        """Тест отправки уведомления об обновлении URL"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        notifier = WebhookNotifier("https://example.com/webhook")
        result = notifier.send_documentation_update(
            api_name="Test API",
            method_name="Get Users",
            old_url="https://old.com/docs",
            new_url="https://new.com/docs",
            doc_type="openapi"
        )
        
        assert result is True
        
        # Проверяем payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert payload['event'] == 'documentation_url_updated'
        assert payload['data']['old_url'] == "https://old.com/docs"
        assert payload['data']['new_url'] == "https://new.com/docs"
    
    @patch('api_watcher.notifier.webhook_notifier.requests.post')
    def test_send_custom_event(self, mock_post):
        """Тест отправки кастомного события"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        notifier = WebhookNotifier("https://example.com/webhook")
        result = notifier.send_custom_event(
            "custom_event",
            {"key": "value"}
        )
        
        assert result is True
        
        # Проверяем payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert payload['event'] == 'custom_event'
        assert payload['data']['key'] == 'value'
    
    @patch('api_watcher.notifier.webhook_notifier.requests.post')
    def test_test_connection_success(self, mock_post):
        """Тест проверки подключения"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        notifier = WebhookNotifier("https://example.com/webhook")
        result = notifier.test_connection()
        
        assert result is True
    
    @patch('api_watcher.notifier.webhook_notifier.requests.post')
    def test_test_connection_failure(self, mock_post):
        """Тест неудачной проверки подключения"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Connection failed")
        
        notifier = WebhookNotifier("https://example.com/webhook")
        result = notifier.test_connection()
        
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
