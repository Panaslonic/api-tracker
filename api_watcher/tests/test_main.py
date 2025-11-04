"""
Тесты для основного модуля main.py
"""

import pytest
import json
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from main import APIWatcher, ProcessingResult, HealthChecker
from config import Config


class TestProcessingResult:
    """Тесты класса ProcessingResult"""
    
    def test_processing_result_creation(self):
        """Тест создания ProcessingResult"""
        result = ProcessingResult(
            url="https://example.com",
            name="Test API",
            success=True,
            changes_detected=True,
            processing_time=1.5
        )
        
        assert result.url == "https://example.com"
        assert result.name == "Test API"
        assert result.success is True
        assert result.changes_detected is True
        assert result.processing_time == 1.5
        assert result.error is None
    
    def test_processing_result_with_error(self):
        """Тест ProcessingResult с ошибкой"""
        result = ProcessingResult(
            url="https://example.com",
            name="Test API",
            success=False,
            error="Connection timeout"
        )
        
        assert result.success is False
        assert result.error == "Connection timeout"
        assert result.changes_detected is False


class TestHealthChecker:
    """Тесты класса HealthChecker"""
    
    def test_health_checker_init(self, temp_dir):
        """Тест инициализации HealthChecker"""
        health_file = os.path.join(temp_dir, "health.json")
        checker = HealthChecker(health_file)
        assert checker.health_file == health_file
    
    def test_update_health(self, temp_dir):
        """Тест обновления health файла"""
        health_file = os.path.join(temp_dir, "health.json")
        checker = HealthChecker(health_file)
        
        details = {"total_urls": 5, "successful": 4, "failed": 1}
        checker.update_health("degraded", details)
        
        assert os.path.exists(health_file)
        
        with open(health_file, 'r', encoding='utf-8') as f:
            health_data = json.load(f)
        
        assert health_data["status"] == "degraded"
        assert health_data["details"] == details
        assert "timestamp" in health_data
    
    def test_get_health_existing_file(self, temp_dir):
        """Тест получения health из существующего файла"""
        health_file = os.path.join(temp_dir, "health.json")
        checker = HealthChecker(health_file)
        
        # Создаем health файл
        test_data = {"status": "healthy", "details": {"test": "data"}}
        checker.update_health("healthy", {"test": "data"})
        
        health = checker.get_health()
        assert health["status"] == "healthy"
        assert health["details"]["test"] == "data"
    
    def test_get_health_missing_file(self, temp_dir):
        """Тест получения health из несуществующего файла"""
        health_file = os.path.join(temp_dir, "nonexistent.json")
        checker = HealthChecker(health_file)
        
        health = checker.get_health()
        assert health["status"] == "unknown"
        assert "Health file not found" in health["message"]


class TestAPIWatcher:
    """Тесты класса APIWatcher"""
    
    def test_api_watcher_init(self):
        """Тест инициализации APIWatcher"""
        watcher = APIWatcher(max_retries=5, retry_delay=2.0, max_concurrent=10)
        
        assert watcher.max_retries == 5
        assert watcher.retry_delay == 2.0
        assert watcher.max_concurrent == 10
        assert len(watcher.parsers) == 5
        assert watcher.snapshot_manager is not None
        assert watcher.notifier is not None
        assert watcher.comparator is not None
        assert watcher.health_checker is not None
    
    def test_load_urls_success(self, temp_dir, sample_urls):
        """Тест успешной загрузки URLs"""
        urls_file = os.path.join(temp_dir, "urls.json")
        
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(sample_urls, f)
        
        with patch.object(Config, 'URLS_FILE', urls_file):
            watcher = APIWatcher()
            urls = watcher.load_urls()
        
        assert len(urls) == 2
        assert urls[0]["name"] == "HTTPBin Test API"
        assert urls[1]["name"] == "Petstore API"
    
    def test_load_urls_file_not_found(self, temp_dir):
        """Тест загрузки URLs когда файл не найден"""
        nonexistent_file = os.path.join(temp_dir, "nonexistent.json")
        
        with patch.object(Config, 'URLS_FILE', nonexistent_file):
            watcher = APIWatcher()
            urls = watcher.load_urls()
        
        assert urls == []
    
    def test_load_urls_invalid_json(self, temp_dir):
        """Тест загрузки URLs с невалидным JSON"""
        urls_file = os.path.join(temp_dir, "invalid.json")
        
        with open(urls_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        with patch.object(Config, 'URLS_FILE', urls_file):
            watcher = APIWatcher()
            urls = watcher.load_urls()
        
        assert urls == []
    
    @pytest.mark.asyncio
    async def test_process_single_url_success(self):
        """Тест успешной обработки одного URL"""
        watcher = APIWatcher()
        
        # Мокаем парсер
        mock_parser = Mock()
        mock_parser.parse.return_value = {"test": "data"}
        watcher.parsers["json"] = mock_parser
        
        # Мокаем snapshot manager
        watcher.snapshot_manager.load_snapshot = Mock(return_value=None)
        watcher.snapshot_manager.save_snapshot = Mock()
        
        # Мокаем сессию
        session = Mock()
        
        url_config = {
            "url": "https://example.com/api",
            "type": "json",
            "name": "Test API"
        }
        
        result = await watcher._process_single_url(session, url_config)
        
        assert result.success is True
        assert result.url == "https://example.com/api"
        assert result.name == "Test API"
        assert result.changes_detected is False  # Первый запуск
        mock_parser.parse.assert_called_once()
        watcher.snapshot_manager.save_snapshot.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_single_url_with_changes(self):
        """Тест обработки URL с обнаруженными изменениями"""
        watcher = APIWatcher()
        
        # Мокаем парсер
        mock_parser = Mock()
        mock_parser.parse.return_value = {"test": "new_data"}
        watcher.parsers["json"] = mock_parser
        
        # Мокаем snapshot manager
        watcher.snapshot_manager.load_snapshot = Mock(return_value={"test": "old_data"})
        watcher.snapshot_manager.save_snapshot = Mock()
        
        # Мокаем comparator
        watcher.comparator.compare = Mock(return_value={"changes": "detected"})
        
        # Мокаем notifier
        watcher.notifier.notify_changes = Mock()
        
        session = Mock()
        
        url_config = {
            "url": "https://example.com/api",
            "type": "json",
            "name": "Test API"
        }
        
        result = await watcher._process_single_url(session, url_config)
        
        assert result.success is True
        assert result.changes_detected is True
        watcher.comparator.compare.assert_called_once()
        watcher.notifier.notify_changes.assert_called_once()
        watcher.snapshot_manager.save_snapshot.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_single_url_unsupported_type(self):
        """Тест обработки URL с неподдерживаемым типом"""
        watcher = APIWatcher()
        session = Mock()
        
        url_config = {
            "url": "https://example.com/api",
            "type": "unsupported",
            "name": "Test API"
        }
        
        result = await watcher._process_single_url(session, url_config)
        
        assert result.success is False
        assert "Неподдерживаемый тип документации" in result.error
    
    @pytest.mark.asyncio
    async def test_process_url_with_retry_success_first_attempt(self):
        """Тест успешной обработки с первой попытки"""
        watcher = APIWatcher(max_retries=3)
        
        # Мокаем _process_single_url для возврата успешного результата
        success_result = ProcessingResult(
            url="https://example.com",
            name="Test API",
            success=True
        )
        
        watcher._process_single_url = AsyncMock(return_value=success_result)
        
        session = Mock()
        url_config = {"url": "https://example.com", "type": "json", "name": "Test API"}
        
        result = await watcher.process_url_with_retry(session, url_config)
        
        assert result.success is True
        assert watcher._process_single_url.call_count == 1
    
    @pytest.mark.asyncio
    async def test_process_url_with_retry_success_after_retries(self):
        """Тест успешной обработки после нескольких попыток"""
        watcher = APIWatcher(max_retries=3, retry_delay=0.01)  # Быстрые повторы для тестов
        
        # Первые две попытки неудачные, третья успешная
        failed_result = ProcessingResult(
            url="https://example.com",
            name="Test API",
            success=False,
            error="Temporary error"
        )
        success_result = ProcessingResult(
            url="https://example.com",
            name="Test API",
            success=True
        )
        
        watcher._process_single_url = AsyncMock(side_effect=[failed_result, failed_result, success_result])
        
        session = Mock()
        url_config = {"url": "https://example.com", "type": "json", "name": "Test API"}
        
        result = await watcher.process_url_with_retry(session, url_config)
        
        assert result.success is True
        assert watcher._process_single_url.call_count == 3
    
    @pytest.mark.asyncio
    async def test_process_url_with_retry_all_attempts_failed(self):
        """Тест когда все попытки неудачные"""
        watcher = APIWatcher(max_retries=2, retry_delay=0.01)
        
        failed_result = ProcessingResult(
            url="https://example.com",
            name="Test API",
            success=False,
            error="Persistent error"
        )
        
        watcher._process_single_url = AsyncMock(return_value=failed_result)
        
        session = Mock()
        url_config = {"url": "https://example.com", "type": "json", "name": "Test API"}
        
        result = await watcher.process_url_with_retry(session, url_config)
        
        assert result.success is False
        assert "Превышено количество попыток" in result.error
        assert watcher._process_single_url.call_count == 2
    
    def test_extract_method_name_html(self):
        """Тест извлечения названия метода для HTML"""
        watcher = APIWatcher()
        
        data = {
            "method_content": {
                "method_name": "Get User Profile\nReturns user information"
            }
        }
        
        result = watcher._extract_method_name(data)
        assert result == "Get User Profile Returns user information"
    
    def test_extract_method_name_openapi(self):
        """Тест извлечения названия метода для OpenAPI"""
        watcher = APIWatcher()
        
        data = {
            "paths": {
                "/users/{id}": {"get": {"summary": "Get user"}},
                "/users": {"post": {"summary": "Create user"}}
            }
        }
        
        result = watcher._extract_method_name(data)
        assert result.startswith("OpenAPI:")
        assert "/users/{id}" in result or "/users" in result
    
    def test_extract_method_name_json(self):
        """Тест извлечения названия метода для JSON"""
        watcher = APIWatcher()
        
        data = {"structure": {"endpoints": []}}
        
        result = watcher._extract_method_name(data)
        assert result == "JSON API"
    
    def test_extract_method_name_markdown(self):
        """Тест извлечения названия метода для Markdown"""
        watcher = APIWatcher()
        
        data = {"sections": [{"title": "API Documentation"}]}
        
        result = watcher._extract_method_name(data)
        assert result == "Markdown Doc"
    
    def test_extract_method_name_unknown(self):
        """Тест извлечения названия метода для неизвестного формата"""
        watcher = APIWatcher()
        
        data = {"unknown": "format"}
        
        result = watcher._extract_method_name(data)
        assert result == "Unknown Method"