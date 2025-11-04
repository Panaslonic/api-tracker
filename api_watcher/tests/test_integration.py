"""
Интеграционные тесты для API Watcher
"""

import pytest
import json
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from main import APIWatcher
from config import Config


class TestAPIWatcherIntegration:
    """Интеграционные тесты для APIWatcher"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_first_run(self, temp_dir, sample_urls, sample_json_data):
        """Тест полного рабочего процесса при первом запуске"""
        # Создаем файл URLs
        urls_file = os.path.join(temp_dir, "urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(sample_urls[:1], f)  # Используем только один URL для простоты
        
        # Мокаем парсер для возврата тестовых данных
        with patch.object(Config, 'URLS_FILE', urls_file):
            watcher = APIWatcher()
            
            # Мокаем JSON парсер
            watcher.parsers["json"].parse = Mock(return_value=sample_json_data)
            
            # Запускаем обработку
            result = await watcher.run_async()
            
            assert result["status"] in ["healthy", "degraded"]
            assert result["details"]["total_urls"] == 1
            assert result["details"]["successful"] >= 0
            
            # Проверяем, что snapshot был создан
            snapshots_dir = os.environ['API_WATCHER_SNAPSHOTS_DIR']
            snapshot_files = os.listdir(snapshots_dir)
            assert len(snapshot_files) >= 1
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_changes(self, temp_dir, sample_urls, sample_json_data, modified_json_data):
        """Тест полного рабочего процесса с обнаружением изменений"""
        # Создаем файл URLs
        urls_file = os.path.join(temp_dir, "urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(sample_urls[:1], f)
        
        with patch.object(Config, 'URLS_FILE', urls_file):
            watcher = APIWatcher()
            
            # Первый запуск - создаем snapshot
            watcher.parsers["json"].parse = Mock(return_value=sample_json_data)
            result1 = await watcher.run_async()
            
            assert result1["status"] in ["healthy", "degraded"]
            
            # Второй запуск - обнаруживаем изменения
            watcher.parsers["json"].parse = Mock(return_value=modified_json_data)
            
            # Мокаем уведомления
            watcher.notifier.notify_changes = Mock()
            
            result2 = await watcher.run_async()
            
            assert result2["status"] in ["healthy", "degraded"]
            
            # Проверяем, что изменения были обнаружены
            watcher.notifier.notify_changes.assert_called()
    
    @pytest.mark.asyncio
    async def test_multiple_urls_processing(self, temp_dir, sample_urls, sample_json_data):
        """Тест обработки нескольких URL одновременно"""
        # Создаем файл URLs с несколькими записями
        urls_file = os.path.join(temp_dir, "urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(sample_urls, f)
        
        with patch.object(Config, 'URLS_FILE', urls_file):
            watcher = APIWatcher(max_concurrent=2)
            
            # Мокаем парсеры
            watcher.parsers["json"].parse = Mock(return_value=sample_json_data)
            watcher.parsers["openapi"].parse = Mock(return_value={"openapi": "3.0.0", "paths": {}})
            
            result = await watcher.run_async()
            
            assert result["status"] in ["healthy", "degraded"]
            assert result["details"]["total_urls"] == len(sample_urls)
            
            # Проверяем, что все URL были обработаны
            snapshots_dir = os.environ['API_WATCHER_SNAPSHOTS_DIR']
            snapshot_files = os.listdir(snapshots_dir)
            assert len(snapshot_files) >= len(sample_urls)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_retry(self, temp_dir, sample_urls):
        """Тест обработки ошибок и повторных попыток"""
        urls_file = os.path.join(temp_dir, "urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(sample_urls[:1], f)
        
        with patch.object(Config, 'URLS_FILE', urls_file):
            watcher = APIWatcher(max_retries=2, retry_delay=0.01)
            
            # Мокаем парсер для генерации ошибки
            watcher.parsers["json"].parse = Mock(side_effect=Exception("Network error"))
            
            result = await watcher.run_async()
            
            # Должен быть статус с ошибками
            assert result["status"] in ["degraded", "unhealthy"]
            assert result["details"]["failed"] > 0
    
    @pytest.mark.asyncio
    async def test_health_check_updates(self, temp_dir, sample_urls, sample_json_data):
        """Тест обновления health статуса"""
        urls_file = os.path.join(temp_dir, "urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(sample_urls[:1], f)
        
        health_file = os.path.join(temp_dir, "health.json")
        
        with patch.object(Config, 'URLS_FILE', urls_file):
            watcher = APIWatcher()
            watcher.health_checker.health_file = health_file
            
            watcher.parsers["json"].parse = Mock(return_value=sample_json_data)
            
            result = await watcher.run_async()
            
            # Проверяем, что health файл был создан
            assert os.path.exists(health_file)
            
            with open(health_file, 'r', encoding='utf-8') as f:
                health_data = json.load(f)
            
            assert health_data["status"] in ["healthy", "degraded", "unhealthy"]
            assert "details" in health_data
            assert "timestamp" in health_data
    
    def test_synchronous_run_wrapper(self, temp_dir, sample_urls, sample_json_data):
        """Тест синхронной обертки для асинхронного выполнения"""
        urls_file = os.path.join(temp_dir, "urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(sample_urls[:1], f)
        
        with patch.object(Config, 'URLS_FILE', urls_file):
            watcher = APIWatcher()
            watcher.parsers["json"].parse = Mock(return_value=sample_json_data)
            
            # Тестируем синхронный метод run()
            result = watcher.run()
            
            assert isinstance(result, dict)
            assert "status" in result
    
    @pytest.mark.asyncio
    async def test_telegram_integration(self, temp_dir, sample_urls, sample_json_data, modified_json_data):
        """Тест интеграции с Telegram уведомлениями"""
        urls_file = os.path.join(temp_dir, "urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(sample_urls[:1], f)
        
        # Мокаем Telegram конфигурацию
        with patch.dict(os.environ, {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'TELEGRAM_CHAT_ID': 'test_chat_id'
        }):
            with patch.object(Config, 'URLS_FILE', urls_file):
                watcher = APIWatcher()
                
                # Мокаем Telegram notifier
                watcher.telegram_notifier = Mock()
                watcher.telegram_notifier.notify_changes = Mock()
                
                # Первый запуск
                watcher.parsers["json"].parse = Mock(return_value=sample_json_data)
                await watcher.run_async()
                
                # Второй запуск с изменениями
                watcher.parsers["json"].parse = Mock(return_value=modified_json_data)
                await watcher.run_async()
                
                # Проверяем, что Telegram уведомление было отправлено
                watcher.telegram_notifier.notify_changes.assert_called()
    
    @pytest.mark.asyncio
    async def test_concurrent_processing_limit(self, temp_dir, sample_json_data):
        """Тест ограничения количества одновременных запросов"""
        # Создаем много URL для тестирования
        many_urls = [
            {"url": f"https://example{i}.com/api", "type": "json", "name": f"API {i}"}
            for i in range(10)
        ]
        
        urls_file = os.path.join(temp_dir, "urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(many_urls, f)
        
        with patch.object(Config, 'URLS_FILE', urls_file):
            watcher = APIWatcher(max_concurrent=3)  # Ограничиваем до 3 одновременных запросов
            
            # Мокаем парсер с задержкой для имитации реальной работы
            async def slow_parse(*args, **kwargs):
                await asyncio.sleep(0.01)  # Небольшая задержка
                return sample_json_data
            
            watcher.parsers["json"].parse = slow_parse
            
            result = await watcher.run_async()
            
            assert result["details"]["total_urls"] == 10
            # Все URL должны быть обработаны, несмотря на ограничение concurrency
            assert result["details"]["successful"] + result["details"]["failed"] == 10