"""
Конфигурация pytest для тестов API Watcher
"""

import pytest
import tempfile
import shutil
import os
import json
from unittest.mock import Mock, patch
from typing import Dict, Any

@pytest.fixture
def temp_dir():
    """Создает временную директорию для тестов"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_urls():
    """Возвращает тестовые URL конфигурации"""
    return [
        {
            "url": "https://httpbin.org/json",
            "type": "json",
            "name": "HTTPBin Test API"
        },
        {
            "url": "https://petstore.swagger.io/v2/swagger.json",
            "type": "openapi",
            "name": "Petstore API"
        }
    ]

@pytest.fixture
def sample_json_data():
    """Возвращает тестовые JSON данные"""
    return {
        "version": "1.0.0",
        "name": "Test API",
        "endpoints": [
            {"path": "/users", "method": "GET"},
            {"path": "/users/{id}", "method": "GET"}
        ]
    }

@pytest.fixture
def modified_json_data():
    """Возвращает модифицированные JSON данные"""
    return {
        "version": "1.1.0",
        "name": "Test API Enhanced",
        "endpoints": [
            {"path": "/users", "method": "GET"},
            {"path": "/users/{id}", "method": "GET"},
            {"path": "/users", "method": "POST"}
        ]
    }

@pytest.fixture
def mock_aiohttp_session():
    """Мок для aiohttp сессии"""
    session = Mock()
    return session

@pytest.fixture
def mock_response():
    """Мок для HTTP ответа"""
    response = Mock()
    response.status = 200
    response.text = Mock(return_value='{"test": "data"}')
    response.json = Mock(return_value={"test": "data"})
    return response

@pytest.fixture(autouse=True)
def setup_test_env(temp_dir):
    """Автоматически настраивает тестовое окружение"""
    # Сохраняем оригинальные переменные окружения
    original_env = {}
    test_env_vars = [
        'API_WATCHER_SNAPSHOTS_DIR',
        'API_WATCHER_URLS_FILE',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    for var in test_env_vars:
        original_env[var] = os.environ.get(var)
    
    # Устанавливаем тестовые переменные
    os.environ['API_WATCHER_SNAPSHOTS_DIR'] = os.path.join(temp_dir, 'snapshots')
    os.environ['API_WATCHER_URLS_FILE'] = os.path.join(temp_dir, 'urls.json')
    
    # Создаем необходимые директории
    os.makedirs(os.environ['API_WATCHER_SNAPSHOTS_DIR'], exist_ok=True)
    
    yield
    
    # Восстанавливаем оригинальные переменные
    for var, value in original_env.items():
        if value is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = value