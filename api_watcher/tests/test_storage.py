"""
Тесты для модуля хранения снимков
"""

import pytest
import json
import os
from storage.snapshot_manager import SnapshotManager


class TestSnapshotManager:
    """Тесты класса SnapshotManager"""
    
    def test_snapshot_manager_init(self, temp_dir):
        """Тест инициализации SnapshotManager"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        assert manager.snapshots_dir == snapshots_dir
        assert os.path.exists(snapshots_dir)
    
    def test_save_snapshot(self, temp_dir, sample_json_data):
        """Тест сохранения снимка"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        url = "https://example.com/api"
        name = "Test API"
        method_name = "Get Users"
        
        manager.save_snapshot(url, sample_json_data, name, method_name)
        
        # Проверяем, что файл создан
        files = os.listdir(snapshots_dir)
        assert len(files) == 1
        
        # Проверяем содержимое файла
        snapshot_file = os.path.join(snapshots_dir, files[0])
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data["url"] == url
        assert saved_data["name"] == name
        assert saved_data["method_name"] == method_name
        assert saved_data["data"] == sample_json_data
        assert "timestamp" in saved_data
    
    def test_load_snapshot_existing(self, temp_dir, sample_json_data):
        """Тест загрузки существующего снимка"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        url = "https://example.com/api"
        name = "Test API"
        method_name = "Get Users"
        
        # Сначала сохраняем снимок
        manager.save_snapshot(url, sample_json_data, name, method_name)
        
        # Затем загружаем его
        loaded_data = manager.load_snapshot(url)
        
        assert loaded_data == sample_json_data
    
    def test_load_snapshot_nonexistent(self, temp_dir):
        """Тест загрузки несуществующего снимка"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        url = "https://nonexistent.com/api"
        
        loaded_data = manager.load_snapshot(url)
        
        assert loaded_data is None
    
    def test_save_multiple_snapshots(self, temp_dir, sample_json_data, modified_json_data):
        """Тест сохранения нескольких снимков"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        # Сохраняем первый снимок
        manager.save_snapshot("https://api1.com", sample_json_data, "API 1", "Method 1")
        
        # Сохраняем второй снимок
        manager.save_snapshot("https://api2.com", modified_json_data, "API 2", "Method 2")
        
        # Проверяем, что созданы два файла
        files = os.listdir(snapshots_dir)
        assert len(files) == 2
        
        # Проверяем, что можем загрузить оба снимка
        data1 = manager.load_snapshot("https://api1.com")
        data2 = manager.load_snapshot("https://api2.com")
        
        assert data1 == sample_json_data
        assert data2 == modified_json_data
    
    def test_update_existing_snapshot(self, temp_dir, sample_json_data, modified_json_data):
        """Тест обновления существующего снимка"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        url = "https://example.com/api"
        
        # Сохраняем первоначальный снимок
        manager.save_snapshot(url, sample_json_data, "Test API", "Method 1")
        
        # Обновляем снимок новыми данными
        manager.save_snapshot(url, modified_json_data, "Test API Updated", "Method 2")
        
        # Проверяем, что файл один (старый перезаписан)
        files = os.listdir(snapshots_dir)
        assert len(files) == 1
        
        # Проверяем, что загружаются новые данные
        loaded_data = manager.load_snapshot(url)
        assert loaded_data == modified_json_data
    
    def test_generate_filename(self, temp_dir):
        """Тест генерации имени файла"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        url = "https://example.com/api/users?param=value"
        name = "Test API with Special Characters!@#$%"
        method_name = "Get Users / List All"
        
        filename = manager._generate_filename(url, name, method_name)
        
        # Проверяем, что имя файла безопасно для файловой системы
        assert filename.endswith('.json')
        assert '/' not in filename
        assert '\\' not in filename
        assert '?' not in filename
        assert '*' not in filename
    
    def test_save_snapshot_with_method_filter(self, temp_dir, sample_json_data):
        """Тест сохранения снимка с фильтром методов"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        url = "https://example.com/openapi.json"
        name = "OpenAPI"
        method_name = "Users API"
        method_filter = "/users"
        
        manager.save_snapshot(url, sample_json_data, name, method_name, method_filter)
        
        # Проверяем, что снимок сохранен с учетом фильтра
        loaded_data = manager.load_snapshot(url, method_filter)
        assert loaded_data == sample_json_data
        
        # Проверяем, что без фильтра снимок не найден
        loaded_data_no_filter = manager.load_snapshot(url)
        assert loaded_data_no_filter is None
    
    def test_load_snapshot_with_method_filter(self, temp_dir, sample_json_data):
        """Тест загрузки снимка с фильтром методов"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        url = "https://example.com/openapi.json"
        
        # Сохраняем снимки с разными фильтрами
        manager.save_snapshot(url, sample_json_data, "API", "Users", "/users")
        manager.save_snapshot(url, {"different": "data"}, "API", "Posts", "/posts")
        
        # Загружаем с конкретным фильтром
        users_data = manager.load_snapshot(url, "/users")
        posts_data = manager.load_snapshot(url, "/posts")
        
        assert users_data == sample_json_data
        assert posts_data == {"different": "data"}
    
    def test_invalid_json_handling(self, temp_dir):
        """Тест обработки поврежденного JSON файла"""
        snapshots_dir = os.path.join(temp_dir, "snapshots")
        manager = SnapshotManager(snapshots_dir)
        
        # Создаем поврежденный JSON файл
        invalid_file = os.path.join(snapshots_dir, "invalid_snapshot.json")
        with open(invalid_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        # Попытка загрузки должна вернуть None
        loaded_data = manager.load_snapshot("https://example.com")
        assert loaded_data is None