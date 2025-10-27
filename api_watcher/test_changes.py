#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации обнаружения изменений
"""

import json
import time
import os
import sys

def modify_test_api():
    """Модифицирует тестовый API файл для демонстрации изменений"""
    
    # Исходная версия
    original_api = {
        "version": "1.0.0",
        "name": "Test API",
        "endpoints": [
            {
                "path": "/users",
                "method": "GET",
                "description": "Get all users"
            },
            {
                "path": "/users/{id}",
                "method": "GET", 
                "description": "Get user by ID"
            }
        ],
        "last_updated": "2024-10-24"
    }
    
    # Модифицированная версия
    modified_api = {
        "version": "1.1.0",
        "name": "Test API Enhanced",
        "endpoints": [
            {
                "path": "/users",
                "method": "GET",
                "description": "Get all users with pagination support"
            },
            {
                "path": "/users/{id}",
                "method": "GET", 
                "description": "Get user by ID"
            },
            {
                "path": "/users",
                "method": "POST",
                "description": "Create new user"
            },
            {
                "path": "/users/{id}",
                "method": "PUT",
                "description": "Update existing user"
            }
        ],
        "features": [
            "User management",
            "Pagination support",
            "CRUD operations"
        ],
        "last_updated": "2024-10-24",
        "changelog": "Added POST and PUT methods for user management"
    }
    
    print("🧪 Тестирование обнаружения изменений...")
    
    # Создаем исходную версию
    print("1️⃣ Создаем исходную версию API...")
    with open('../test_api.json', 'w', encoding='utf-8') as f:
        json.dump(original_api, f, indent=2, ensure_ascii=False)
    
    # Запускаем первый скан
    print("2️⃣ Запускаем первый скан (создание snapshot)...")
    original_dir = os.getcwd()
    os.chdir('..')
    os.system('python api_watcher/main.py')
    os.chdir(original_dir)
    
    print("\n⏳ Ждем 2 секунды...")
    time.sleep(2)
    
    # Модифицируем API
    print("3️⃣ Модифицируем API...")
    with open('../test_api.json', 'w', encoding='utf-8') as f:
        json.dump(modified_api, f, indent=2, ensure_ascii=False)
    
    # Запускаем второй скан
    print("4️⃣ Запускаем второй скан (обнаружение изменений)...")
    os.chdir('..')
    os.system('python api_watcher/main.py')
    os.chdir(original_dir)
    
    print("\n✅ Тест завершен!")
    print("📊 Результат: Система должна была обнаружить изменения в test_api.json")

def test_multiple_changes():
    """Тестирует несколько последовательных изменений"""
    
    versions = [
        {
            "version": "1.0.0",
            "endpoints": ["GET /users", "GET /users/{id}"]
        },
        {
            "version": "1.1.0", 
            "endpoints": ["GET /users", "GET /users/{id}", "POST /users"]
        },
        {
            "version": "1.2.0",
            "endpoints": ["GET /users", "GET /users/{id}", "POST /users", "PUT /users/{id}", "DELETE /users/{id}"]
        }
    ]
    
    print("🔄 Тестирование множественных изменений...")
    
    for i, version_data in enumerate(versions, 1):
        print(f"\n📝 Версия {version_data['version']}...")
        
        with open('../test_api.json', 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
        
        print(f"🔍 Сканирование версии {i}...")
        original_dir = os.getcwd()
        os.chdir('..')
        os.system('python api_watcher/main.py')
        os.chdir(original_dir)
        
        if i < len(versions):
            print("⏳ Пауза перед следующей версией...")
            time.sleep(1)
    
    print("\n✅ Тест множественных изменений завершен!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "multiple":
        test_multiple_changes()
    else:
        modify_test_api()