#!/usr/bin/env python3
"""
Быстрый тест API Watcher с ограниченным набором источников
"""

import json
import os
import sys
from main import APIWatcher

def create_test_config():
    """Создает тестовую конфигурацию с быстрыми источниками"""
    test_urls = [
        {
            "url": "https://httpbin.org/json",
            "type": "json",
            "name": "HTTPBin JSON Test",
            "description": "Быстрый JSON тест"
        },
        {
            "url": "https://jsonplaceholder.typicode.com/posts/1",
            "type": "json",
            "name": "JSONPlaceholder Post",
            "description": "Тестовый пост"
        },
        {
            "url": "test_api.json",
            "type": "json",
            "name": "Local Test API",
            "description": "Локальный тестовый файл"
        }
    ]
    
    with open('urls_test.json', 'w', encoding='utf-8') as f:
        json.dump(test_urls, f, indent=2, ensure_ascii=False)
    
    return 'urls_test.json'

def run_quick_test():
    """Запускает быстрый тест"""
    print("🚀 Быстрый тест API Watcher...")
    
    # Создаем тестовую конфигурацию
    test_config = create_test_config()
    
    # Временно меняем конфигурацию
    from config import Config
    original_urls_file = Config.URLS_FILE
    Config.URLS_FILE = test_config
    
    try:
        # Запускаем watcher
        watcher = APIWatcher()
        watcher.run()
        
        print("\n✅ Быстрый тест завершен!")
        print("📁 Проверьте директорию snapshots/ для созданных снимков")
        
    finally:
        # Восстанавливаем оригинальную конфигурацию
        Config.URLS_FILE = original_urls_file
        
        # Удаляем тестовый файл
        if os.path.exists(test_config):
            os.remove(test_config)

if __name__ == "__main__":
    run_quick_test()