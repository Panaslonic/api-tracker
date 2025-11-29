"""
Notifier adapters implementation
Реализации адаптеров для различных каналов уведомлений
"""

import logging
from typing import Optional, List, Dict

from api_watcher.notifier.base import (
    NotifierAdapter, 
    ChangeNotification, 
    DocumentationUpdate
)
from api_watcher.notifier.slack_notifier import SlackNotifier
from api_watcher.notifier.webhook_notifier import WebhookNotifier
from api_watcher.notifier.telegram_notifier import TelegramNotifier
from api_watcher.notifier.console_notifier import ConsoleNotifier

logger = logging.getLogger(__name__)


class SlackAdapter(NotifierAdapter):
    """Адаптер для Slack"""
    
    def __init__(self, bot_token: str, channel: str):
        self._notifier = SlackNotifier(bot_token, channel)
    
    @property
    def name(self) -> str:
        return "slack"
    
    def send_change(self, notification: ChangeNotification) -> bool:
        return self._notifier.send_change_notification(
            api_name=notification.api_name,
            method_name=notification.method_name,
            url=notification.url,
            summary=notification.summary,
            severity=notification.severity,
            key_changes=notification.key_changes
        )
    
    def send_digest(self, changes: List[Dict]) -> bool:
        return self._notifier.send_weekly_digest(changes)
    
    def send_doc_update(self, update: DocumentationUpdate) -> bool:
        message = f"🔄 *Обновлена ссылка на документацию*\n\n"
        message += f"*API:* {update.api_name}\n"
        if update.method_name:
            message += f"*Метод:* {update.method_name}\n"
        message += f"*Старый URL:* {update.old_url}\n"
        message += f"*Новый URL:* {update.new_url}\n"
        message += f"*Тип:* {update.doc_type}\n"
        if update.title:
            message += f"*Заголовок:* {update.title}\n"
        return self._notifier.send_message(message)
    
    def test_connection(self) -> bool:
        return self._notifier.send_message("🧪 Тест подключения API Watcher")


class WebhookAdapter(NotifierAdapter):
    """Адаптер для Webhook"""
    
    def __init__(self, webhook_url: str, timeout: int = 10):
        self._notifier = WebhookNotifier(webhook_url, timeout)
    
    @property
    def name(self) -> str:
        return "webhook"
    
    def send_change(self, notification: ChangeNotification) -> bool:
        return self._notifier.send_change_notification(
            api_name=notification.api_name,
            method_name=notification.method_name,
            url=notification.url,
            summary=notification.summary,
            severity=notification.severity,
            key_changes=notification.key_changes
        )
    
    def send_digest(self, changes: List[Dict]) -> bool:
        return self._notifier.send_weekly_digest(changes)
    
    def send_doc_update(self, update: DocumentationUpdate) -> bool:
        return self._notifier.send_documentation_update(
            api_name=update.api_name,
            method_name=update.method_name,
            old_url=update.old_url,
            new_url=update.new_url,
            doc_type=update.doc_type
        )
    
    def test_connection(self) -> bool:
        return self._notifier.test_connection()


class TelegramAdapter(NotifierAdapter):
    """Адаптер для Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self._notifier = TelegramNotifier(bot_token, chat_id)
    
    @property
    def name(self) -> str:
        return "telegram"
    
    def send_change(self, notification: ChangeNotification) -> bool:
        diff = {
            'summary': notification.summary,
            'severity': notification.severity,
            'key_changes': notification.key_changes or []
        }
        self._notifier.notify_changes(notification.url, diff)
        return True
    
    def send_digest(self, changes: List[Dict]) -> bool:
        if not changes:
            return True
        message = f"📊 *Еженедельная сводка*\n\nИзменений: {len(changes)}\n\n"
        for change in changes[:5]:
            message += f"• {change.get('api_name', 'Unknown')}: {change.get('summary', '')[:100]}\n"
        return self._notifier._send_message(message)
    
    def send_doc_update(self, update: DocumentationUpdate) -> bool:
        message = f"🔄 *Обновлена документация*\n\n"
        message += f"API: {update.api_name}\n"
        message += f"Новый URL: {update.new_url}\n"
        return self._notifier._send_message(message)
    
    def test_connection(self) -> bool:
        return self._notifier.test_connection()


class ConsoleAdapter(NotifierAdapter):
    """Адаптер для консольного вывода"""
    
    def __init__(self):
        self._notifier = ConsoleNotifier()
    
    @property
    def name(self) -> str:
        return "console"
    
    def send_change(self, notification: ChangeNotification) -> bool:
        diff = {
            'summary': notification.summary,
            'severity': notification.severity,
            'key_changes': notification.key_changes or []
        }
        self._notifier.notify_changes(notification.url, diff)
        return True
    
    def send_digest(self, changes: List[Dict]) -> bool:
        self._notifier.notify_info(f"📊 Сводка: {len(changes)} изменений")
        return True
    
    def send_doc_update(self, update: DocumentationUpdate) -> bool:
        self._notifier.notify_info(
            f"🔄 Документация обновлена: {update.api_name} -> {update.new_url}"
        )
        return True
    
    def test_connection(self) -> bool:
        self._notifier.notify_success("Тест подключения успешен")
        return True
