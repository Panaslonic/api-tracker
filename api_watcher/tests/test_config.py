"""
Тесты для модуля конфигурации
"""

import pytest
import os
from unittest.mock import patch
from config import Config


class TestConfig:
    """Тесты класса Config"""
    
    def test_default_values(self):
        """Тест значений по умолчанию"""
        # Проверяем значения по умолчанию или из переменных окружения
        assert Config.SNAPSHOTS_DIR is not None
        assert Config.URLS_FILE is not None
        assert Config.REQUEST_TIMEOUT == 30
        assert Config.IGNORE_ORDER is True
        assert Config.VERBOSE_LEVEL == 2
        assert Config.LOG_LEVEL == 'INFO'
    
    @patch.dict(os.environ, {
        'API_WATCHER_SNAPSHOTS_DIR': '/custom/snapshots',
        'API_WATCHER_URLS_FILE': '/custom/urls.json',
        'API_WATCHER_TIMEOUT': '60',
        'API_WATCHER_LOG_LEVEL': 'DEBUG'
    })
    def test_environment_variables(self):
        """Тест переопределения через переменные окружения"""
        # Перезагружаем модуль для применения новых переменных
        import importlib
        import config
        importlib.reload(config)
        
        assert config.Config.SNAPSHOTS_DIR == '/custom/snapshots'
        assert config.Config.URLS_FILE == '/custom/urls.json'
        assert config.Config.REQUEST_TIMEOUT == 60
        assert config.Config.LOG_LEVEL == 'DEBUG'
    
    def test_telegram_not_configured(self):
        """Тест когда Telegram не настроен"""
        with patch.dict(os.environ, {}, clear=True):
            assert not Config.is_telegram_configured()
    
    @patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'TELEGRAM_CHAT_ID': 'test_chat_id'
    })
    def test_telegram_configured(self):
        """Тест когда Telegram настроен"""
        assert Config.is_telegram_configured()
    
    @patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token'
        # TELEGRAM_CHAT_ID отсутствует
    })
    def test_telegram_partially_configured(self):
        """Тест когда Telegram настроен частично"""
        assert not Config.is_telegram_configured()
    
    def test_get_exclude_paths(self):
        """Тест получения путей для исключения"""
        exclude_paths = Config.get_exclude_paths()
        assert isinstance(exclude_paths, list)
        assert "root['url']" in exclude_paths
        assert "root['timestamp']" in exclude_paths