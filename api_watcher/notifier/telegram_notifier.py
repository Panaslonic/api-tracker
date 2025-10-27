"""
Telegram Notifier - уведомления через Telegram бота
Отправляет сообщения об изменениях в Telegram чат
"""

import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime


class TelegramNotifier:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}" if bot_token else None

    def notify_changes(self, url: str, diff: Dict[str, Any]) -> None:
        """Отправляет уведомление об изменениях в Telegram"""
        if not self._is_configured():
            print("⚠️ Telegram уведомления не настроены (отсутствует bot_token или chat_id)")
            return

        message = self._format_changes_message(url, diff)
        self._send_message(message)

    def notify_error(self, url: str, error: str) -> None:
        """Отправляет уведомление об ошибке в Telegram"""
        if not self._is_configured():
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"❌ *ОШИБКА API WATCHER*\n\n"
        message += f"🔗 URL: `{url}`\n"
        message += f"⏰ Время: {timestamp}\n"
        message += f"💥 Ошибка: {error}"
        
        self._send_message(message)

    def _format_changes_message(self, url: str, diff: Dict[str, Any]) -> str:
        """Форматирует сообщение об изменениях"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"🔔 *ОБНАРУЖЕНЫ ИЗМЕНЕНИЯ*\n\n"
        message += f"🔗 URL: `{url}`\n"
        message += f"⏰ Время: {timestamp}\n\n"
        
        # Добавленные элементы
        if 'dictionary_item_added' in diff:
            message += "➕ *ДОБАВЛЕНО:*\n"
            for item in diff['dictionary_item_added'][:5]:  # Ограничиваем количество
                message += f"  • `{item}`\n"
            if len(diff['dictionary_item_added']) > 5:
                message += f"  ... и еще {len(diff['dictionary_item_added']) - 5} элементов\n"
            message += "\n"
        
        # Удаленные элементы
        if 'dictionary_item_removed' in diff:
            message += "➖ *УДАЛЕНО:*\n"
            for item in diff['dictionary_item_removed'][:5]:
                message += f"  • `{item}`\n"
            if len(diff['dictionary_item_removed']) > 5:
                message += f"  ... и еще {len(diff['dictionary_item_removed']) - 5} элементов\n"
            message += "\n"
        
        # Измененные значения
        if 'values_changed' in diff:
            message += "🔄 *ИЗМЕНЕНО:*\n"
            count = 0
            for path, change in diff['values_changed'].items():
                if count >= 3:  # Ограничиваем количество для читаемости
                    message += f"  ... и еще {len(diff['values_changed']) - 3} изменений\n"
                    break
                
                old_value = str(change.get('old_value', ''))[:50]
                new_value = str(change.get('new_value', ''))[:50]
                message += f"  📍 `{path}`\n"
                message += f"    Было: `{old_value}`\n"
                message += f"    Стало: `{new_value}`\n"
                count += 1
            message += "\n"
        
        return message

    def _send_message(self, message: str) -> bool:
        """Отправляет сообщение в Telegram"""
        if not self._is_configured():
            return False

        url = f"{self.base_url}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                print("📱 Уведомление отправлено в Telegram")
                return True
            else:
                print(f"❌ Ошибка отправки в Telegram: {result.get('description')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка соединения с Telegram API: {e}")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка при отправке в Telegram: {e}")
            return False

    def _is_configured(self) -> bool:
        """Проверяет, настроен ли Telegram уведомитель"""
        return bool(self.bot_token and self.chat_id)

    def test_connection(self) -> bool:
        """Тестирует соединение с Telegram API"""
        if not self._is_configured():
            print("❌ Telegram не настроен")
            return False

        test_message = "🧪 Тест API Watcher - уведомления работают!"
        return self._send_message(test_message)