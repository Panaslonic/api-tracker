"""
Webhook notifier for API changes
Отправляет уведомления на webhook URL
"""

import logging
import requests
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class WebhookNotifier:
    """Отправка уведомлений на webhook"""
    
    def __init__(self, webhook_url: str, timeout: int = 10):
        """
        Инициализация webhook notifier
        
        Args:
            webhook_url: URL webhook для отправки уведомлений
            timeout: Таймаут запроса в секундах
        """
        self.webhook_url = webhook_url
        self.timeout = timeout
    
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
        payload = {
            'event': 'api_change_detected',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'api_name': api_name,
                'method_name': method_name,
                'url': url,
                'summary': summary,
                'severity': severity,
                'key_changes': key_changes or []
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            logger.info(f"✅ Webhook: уведомление отправлено ({response.status_code})")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Webhook ошибка: {e}")
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
        
        payload = {
            'event': 'weekly_digest',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'total_changes': len(changes),
                'changes': changes
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            logger.info(f"✅ Webhook: еженедельная сводка отправлена ({response.status_code})")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Webhook ошибка при отправке сводки: {e}")
            return False
    
    def send_documentation_update(
        self,
        api_name: str,
        method_name: Optional[str],
        old_url: str,
        new_url: str,
        doc_type: str
    ) -> bool:
        """
        Отправляет уведомление об обновлении ссылки на документацию
        
        Args:
            api_name: Название API
            method_name: Название метода
            old_url: Старый URL
            new_url: Новый URL
            doc_type: Тип документации (openapi/search)
        
        Returns:
            True если успешно отправлено
        """
        payload = {
            'event': 'documentation_url_updated',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'api_name': api_name,
                'method_name': method_name,
                'old_url': old_url,
                'new_url': new_url,
                'doc_type': doc_type
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            logger.info(f"✅ Webhook: уведомление об обновлении URL отправлено")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Webhook ошибка: {e}")
            return False
    
    def send_custom_event(self, event_name: str, data: Dict) -> bool:
        """
        Отправляет кастомное событие
        
        Args:
            event_name: Название события
            data: Данные события
        
        Returns:
            True если успешно отправлено
        """
        payload = {
            'event': event_name,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            logger.info(f"✅ Webhook: событие '{event_name}' отправлено")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Webhook ошибка: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Тестирует подключение к webhook
        
        Returns:
            True если webhook доступен
        """
        payload = {
            'event': 'test_connection',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'message': 'Test connection from API Watcher'
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            logger.info(f"✅ Webhook: тест подключения успешен ({response.status_code})")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Webhook: тест подключения не удался: {e}")
            return False
