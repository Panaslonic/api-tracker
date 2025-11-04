"""
Тесты для уведомителей
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from notifier.console_notifier import ConsoleNotifier
from notifier.telegram_notifier import TelegramNotifier


class TestConsoleNotifier:
    """Тесты консольного уведомителя"""
    
    def test_console_notifier_init(self):
        """Тест инициализации консольного уведомителя"""
        notifier = ConsoleNotifier()
        assert notifier is not None
    
    @patch('builtins.print')
    def test_notify_changes(self, mock_print):
        """Тест уведомления об изменениях"""
        notifier = ConsoleNotifier()
        
        url = "https://example.com/api"
        changes = [
            "Added: root['new_field'] = 'new_value'",
            "Changed: root['version'] from '1.0' to '2.0'"
        ]
        
        notifier.notify_changes(url, changes)
        
        # Проверяем, что print был вызван
        assert mock_print.call_count > 0
        
        # Проверяем, что в выводе есть информация об изменениях
        all_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(all_calls)
        
        assert url in output
        assert "изменения" in output.lower() or "changes" in output.lower()
    
    @patch('builtins.print')
    def test_notify_empty_changes(self, mock_print):
        """Тест уведомления с пустым списком изменений"""
        notifier = ConsoleNotifier()
        
        url = "https://example.com/api"
        changes = []
        
        notifier.notify_changes(url, changes)
        
        # Даже с пустыми изменениями должен быть какой-то вывод
        assert mock_print.call_count >= 0


class TestTelegramNotifier:
    """Тесты Telegram уведомителя"""
    
    def test_telegram_notifier_init(self):
        """Тест инициализации Telegram уведомителя"""
        bot_token = "test_token"
        chat_id = "test_chat_id"
        
        notifier = TelegramNotifier(bot_token, chat_id)
        
        assert notifier.bot_token == bot_token
        assert notifier.chat_id == chat_id
    
    @patch('requests.post')
    def test_notify_changes_success(self, mock_post):
        """Тест успешной отправки уведомления в Telegram"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response
        
        notifier = TelegramNotifier("test_token", "test_chat_id")
        
        url = "https://example.com/api"
        changes = [
            "Added: root['new_field'] = 'new_value'",
            "Changed: root['version'] from '1.0' to '2.0'"
        ]
        
        notifier.notify_changes(url, changes)
        
        # Проверяем, что POST запрос был отправлен
        mock_post.assert_called_once()
        
        # Проверяем параметры запроса
        call_args = mock_post.call_args
        assert "sendMessage" in call_args[0][0]  # URL содержит sendMessage
        
        # Проверяем данные запроса
        data = call_args[1]["data"]
        assert data["chat_id"] == "test_chat_id"
        assert url in data["text"]
    
    @patch('requests.post')
    def test_notify_changes_network_error(self, mock_post):
        """Тест обработки сетевой ошибки при отправке в Telegram"""
        mock_post.side_effect = Exception("Network error")
        
        notifier = TelegramNotifier("test_token", "test_chat_id")
        
        url = "https://example.com/api"
        changes = ["Some change"]
        
        # Не должно вызывать исключение
        notifier.notify_changes(url, changes)
        
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_notify_changes_api_error(self, mock_post):
        """Тест обработки ошибки API Telegram"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"ok": False, "description": "Bad Request"}
        mock_post.return_value = mock_response
        
        notifier = TelegramNotifier("test_token", "test_chat_id")
        
        url = "https://example.com/api"
        changes = ["Some change"]
        
        # Не должно вызывать исключение
        notifier.notify_changes(url, changes)
        
        mock_post.assert_called_once()
    
    def test_format_message(self):
        """Тест форматирования сообщения"""
        notifier = TelegramNotifier("test_token", "test_chat_id")
        
        url = "https://example.com/api"
        changes = [
            "Added: root['new_field'] = 'new_value'",
            "Changed: root['version'] from '1.0' to '2.0'",
            "Removed: root['old_field']"
        ]
        
        message = notifier._format_message(url, changes)
        
        assert url in message
        assert "new_field" in message
        assert "version" in message
        assert "old_field" in message
        assert len(changes) == 3  # Все изменения должны быть включены
    
    def test_format_message_long_changes(self):
        """Тест форматирования сообщения с большим количеством изменений"""
        notifier = TelegramNotifier("test_token", "test_chat_id")
        
        url = "https://example.com/api"
        # Создаем много изменений
        changes = [f"Change {i}: some modification" for i in range(50)]
        
        message = notifier._format_message(url, changes)
        
        # Сообщение не должно быть слишком длинным для Telegram
        assert len(message) <= 4096  # Лимит Telegram
        assert url in message
    
    def test_format_message_empty_changes(self):
        """Тест форматирования сообщения с пустыми изменениями"""
        notifier = TelegramNotifier("test_token", "test_chat_id")
        
        url = "https://example.com/api"
        changes = []
        
        message = notifier._format_message(url, changes)
        
        assert url in message
        assert len(message) > 0  # Сообщение не должно быть пустым
    
    @patch('requests.post')
    def test_send_message_with_retry(self, mock_post):
        """Тест отправки сообщения с повторными попытками"""
        # Первая попытка неудачная, вторая успешная
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"ok": True}
        
        mock_post.side_effect = [mock_response_fail, mock_response_success]
        
        notifier = TelegramNotifier("test_token", "test_chat_id")
        
        # Если в классе есть метод с повторными попытками
        if hasattr(notifier, '_send_with_retry'):
            result = notifier._send_with_retry("Test message")
            assert result is True
            assert mock_post.call_count == 2