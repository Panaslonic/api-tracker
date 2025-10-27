#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Telegram уведомлений
"""

from notifier.telegram_notifier import TelegramNotifier

def test_telegram():
    # Замените на ваши реальные значения
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    CHAT_ID = "YOUR_CHAT_ID_HERE"
    
    print("🧪 Тестирование Telegram уведомлений...")
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("❌ Пожалуйста, укажите реальные BOT_TOKEN и CHAT_ID в файле test_telegram.py")
        print("📋 Инструкция:")
        print("1. Создайте бота через @BotFather в Telegram")
        print("2. Получите токен бота")
        print("3. Узнайте свой chat_id (можно через @userinfobot)")
        print("4. Замените значения в этом файле")
        return
    
    notifier = TelegramNotifier(BOT_TOKEN, CHAT_ID)
    
    # Тест соединения
    if notifier.test_connection():
        print("✅ Telegram уведомления настроены корректно!")
        
        # Тест уведомления об изменениях
        test_diff = {
            'values_changed': {
                'version': {'old_value': '1.0.0', 'new_value': '1.1.0'},
                'description': {'old_value': 'Old API', 'new_value': 'New API'}
            },
            'dictionary_item_added': ['new_endpoint', 'new_feature']
        }
        
        notifier.notify_changes("https://example.com/api", test_diff)
        print("📱 Тестовое уведомление отправлено!")
        
    else:
        print("❌ Ошибка настройки Telegram уведомлений")

if __name__ == "__main__":
    test_telegram()