#!/usr/bin/env python3
"""
Тестовый скрипт для отправки уведомления на webhook
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api_watcher'))

from notifier.webhook_notifier import WebhookNotifier

def main():
    # Укажите ваш webhook URL
    webhook_url = input("Введите webhook URL (или нажмите Enter для webhook.site): ").strip()
    
    if not webhook_url:
        # Используем webhook.site для тестирования
        webhook_url = "https://webhook.site/unique-id"
        print(f"\n⚠️  Используется тестовый URL: {webhook_url}")
        print("💡 Создайте свой webhook на https://webhook.site и замените 'unique-id'\n")
    
    # Создаем notifier
    notifier = WebhookNotifier(webhook_url=webhook_url, timeout=10)
    
    print("🔄 Отправка тестового уведомления...")
    
    # Тест 1: Проверка подключения
    print("\n1️⃣ Тест подключения...")
    if notifier.test_connection():
        print("✅ Подключение успешно!")
    else:
        print("❌ Ошибка подключения")
        return
    
    # Тест 2: Уведомление об изменении API
    print("\n2️⃣ Отправка уведомления об изменении API...")
    success = notifier.send_change_notification(
        api_name="Test API",
        method_name="GET /users",
        url="https://api.example.com/docs",
        summary="Добавлен новый параметр 'filter' для фильтрации пользователей",
        severity="moderate",
        key_changes=[
            "Добавлен параметр query 'filter'",
            "Обновлена схема ответа",
            "Добавлена пагинация"
        ]
    )
    
    if success:
        print("✅ Уведомление отправлено!")
    else:
        print("❌ Ошибка отправки")
    
    # Тест 3: Еженедельная сводка
    print("\n3️⃣ Отправка еженедельной сводки...")
    changes = [
        {
            "api_name": "User API",
            "method": "GET /users",
            "date": "2024-11-18",
            "summary": "Добавлена пагинация"
        },
        {
            "api_name": "Auth API",
            "method": "POST /login",
            "date": "2024-11-19",
            "summary": "Обновлена схема токена"
        }
    ]
    
    if notifier.send_weekly_digest(changes):
        print("✅ Сводка отправлена!")
    else:
        print("❌ Ошибка отправки сводки")
    
    print("\n✨ Тестирование завершено!")
    print(f"📊 Проверьте webhook на: {webhook_url}")

if __name__ == "__main__":
    main()
