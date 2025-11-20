#!/usr/bin/env python3
"""
Тест интеграции webhook уведомлений
"""

import sys
import os
sys.path.insert(0, 'api_watcher')

from config import Config
from notifier.webhook_notifier import WebhookNotifier

print("=" * 60)
print("Тест Webhook уведомлений")
print("=" * 60)

# Проверяем конфигурацию
if Config.is_webhook_configured():
    print(f"✅ Webhook настроен: {Config.WEBHOOK_URL}")
    
    # Создаем notifier
    notifier = WebhookNotifier(Config.WEBHOOK_URL)
    
    # Отправляем тестовое уведомление
    print("\nОтправка тестового уведомления...")
    success = notifier.send_change_notification(
        api_name="Test API",
        method_name="Test Method",
        url="https://example.com/api/docs",
        summary="Тестовое уведомление об изменениях",
        severity="moderate",
        key_changes=["Изменение 1", "Изменение 2"]
    )
    
    if success:
        print("✅ Уведомление успешно отправлено!")
    else:
        print("❌ Ошибка при отправке уведомления")
else:
    print("❌ Webhook не настроен в .env")
    print("Добавьте WEBHOOK_URL в файл .env")
