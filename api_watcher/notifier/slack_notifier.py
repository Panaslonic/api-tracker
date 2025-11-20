"""
Slack notifier for API changes
Отправляет уведомления об изменениях в Slack
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Отправка уведомлений в Slack"""
    
    def __init__(self, bot_token: str, channel: str):
        self.client = WebClient(token=bot_token)
        self.channel = channel
    
    def send_message(self, text: str) -> bool:
        """
        Отправляет простое текстовое сообщение в Slack
        
        Args:
            text: Текст сообщения (поддерживает Markdown)
        
        Returns:
            True если успешно отправлено
        """
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=text,
                mrkdwn=True
            )
            
            logger.info(f"✅ Slack: сообщение отправлено в {self.channel}")
            return True
            
        except SlackApiError as e:
            logger.error(f"❌ Slack ошибка: {e.response['error']}")
            return False
    
    def send_change_notification(
        self,
        api_name: str,
        method_name: Optional[str],
        url: str,
        summary: str,
        severity: str = 'moderate',
        key_changes: Optional[List[str]] = None
    ) -> bool:
        """
        Отправляет уведомление об изменениях
        
        Args:
            api_name: Название API
            method_name: Название метода
            url: URL документации
            summary: Краткая сводка изменений
            severity: Уровень важности (minor/moderate/major)
            key_changes: Список ключевых изменений
        
        Returns:
            True если успешно отправлено
        """
        # Выбираем эмодзи в зависимости от важности
        emoji_map = {
            'minor': '🔵',
            'moderate': '🟡',
            'major': '🔴',
            'unknown': '⚪'
        }
        emoji = emoji_map.get(severity, '⚪')
        
        # Формируем заголовок
        title = f"{emoji} Изменения в API"
        if method_name:
            title += f": {api_name} - {method_name}"
        else:
            title += f": {api_name}"
        
        # Формируем блоки сообщения
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Сводка изменений:*\n{summary}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*API:*\n{api_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Важность:*\n{severity.upper()}"
                    }
                ]
            }
        ]
        
        # Добавляем ключевые изменения
        if key_changes:
            changes_text = "\n".join([f"• {change}" for change in key_changes[:5]])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Ключевые изменения:*\n{changes_text}"
                }
            })
        
        # Добавляем ссылку
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<{url}|Открыть документацию>"
            }
        })
        
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text=f"Изменения в {api_name}"  # Fallback text
            )
            
            logger.info(f"✅ Slack: уведомление отправлено в {self.channel}")
            return True
            
        except SlackApiError as e:
            logger.error(f"❌ Slack ошибка: {e.response['error']}")
            return False
    
    def send_weekly_digest(self, changes: List[Dict]) -> bool:
        """
        Отправляет еженедельную сводку изменений
        
        Args:
            changes: Список изменений за неделю
        
        Returns:
            True если успешно отправлено
        """
        if not changes:
            logger.info("📭 Нет изменений для еженедельной сводки")
            return True
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Еженедельная сводка изменений API"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Обнаружено изменений: *{len(changes)}*"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Добавляем каждое изменение
        for change in changes[:10]:  # Максимум 10 изменений
            api_name = change.get('api_name', 'Unknown')
            method_name = change.get('method_name', '')
            summary = change.get('summary', 'Нет описания')
            url = change.get('url', '')
            
            title = f"*{api_name}*"
            if method_name:
                title += f" - {method_name}"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{title}\n{summary[:200]}..."
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Открыть"
                    },
                    "url": url
                }
            })
        
        if len(changes) > 10:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_И еще {len(changes) - 10} изменений..._"
                    }
                ]
            })
        
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text="Еженедельная сводка изменений API"
            )
            
            logger.info(f"✅ Slack: еженедельная сводка отправлена")
            return True
            
        except SlackApiError as e:
            logger.error(f"❌ Slack ошибка при отправке сводки: {e.response['error']}")
            return False
