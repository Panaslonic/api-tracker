"""
Base notifier interface and adapter pattern
Базовый интерфейс для всех нотификаторов
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChangeNotification:
    """Данные уведомления об изменениях"""
    api_name: str
    url: str
    summary: str
    severity: str = 'moderate'
    method_name: Optional[str] = None
    key_changes: Optional[List[str]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class DocumentationUpdate:
    """Данные об обновлении документации"""
    api_name: str
    old_url: str
    new_url: str
    doc_type: str
    method_name: Optional[str] = None
    title: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class NotifierAdapter(ABC):
    """Абстрактный адаптер для нотификаций"""
    
    @abstractmethod
    def send_change(self, notification: ChangeNotification) -> bool:
        """Отправляет уведомление об изменениях"""
        pass
    
    @abstractmethod
    def send_digest(self, changes: List[Dict]) -> bool:
        """Отправляет сводку изменений"""
        pass
    
    @abstractmethod
    def send_doc_update(self, update: DocumentationUpdate) -> bool:
        """Отправляет уведомление об обновлении документации"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Тестирует подключение"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Название адаптера"""
        pass


class NotifierManager:
    """Менеджер нотификаторов - агрегирует несколько адаптеров"""
    
    def __init__(self):
        self._adapters: List[NotifierAdapter] = []
    
    def register(self, adapter: NotifierAdapter) -> None:
        """Регистрирует адаптер"""
        self._adapters.append(adapter)
    
    def send_change(self, notification: ChangeNotification) -> Dict[str, bool]:
        """Отправляет уведомление через все адаптеры"""
        results = {}
        for adapter in self._adapters:
            results[adapter.name] = adapter.send_change(notification)
        return results
    
    def send_digest(self, changes: List[Dict]) -> Dict[str, bool]:
        """Отправляет сводку через все адаптеры"""
        results = {}
        for adapter in self._adapters:
            results[adapter.name] = adapter.send_digest(changes)
        return results
    
    def send_doc_update(self, update: DocumentationUpdate) -> Dict[str, bool]:
        """Отправляет обновление документации через все адаптеры"""
        results = {}
        for adapter in self._adapters:
            results[adapter.name] = adapter.send_doc_update(update)
        return results
    
    @property
    def adapters(self) -> List[str]:
        """Список зарегистрированных адаптеров"""
        return [a.name for a in self._adapters]
