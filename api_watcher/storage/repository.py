"""
Repository pattern for API Watcher
Абстракция над хранилищем данных
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Protocol
from datetime import datetime, timedelta

from api_watcher.storage.database import Snapshot, DatabaseManager


class SnapshotRepository(ABC):
    """Абстрактный репозиторий для работы со снэпшотами"""
    
    @abstractmethod
    def save(
        self,
        url: str,
        raw_html: str,
        text_content: str,
        api_name: Optional[str] = None,
        method_name: Optional[str] = None,
        content_type: str = 'html',
        structured_data: Optional[dict] = None,
        content_hash: Optional[str] = None,
        has_changes: bool = False,
        ai_summary: Optional[str] = None
    ) -> Snapshot:
        """Сохраняет снэпшот"""
        pass
    
    @abstractmethod
    def get_latest(self, url: str) -> Optional[Snapshot]:
        """Получает последний снэпшот для URL"""
        pass
    
    @abstractmethod
    def get_history(self, url: str, limit: int = 10) -> List[Snapshot]:
        """Получает историю снэпшотов"""
        pass
    
    @abstractmethod
    def get_all_urls(self) -> List[str]:
        """Получает все отслеживаемые URL"""
        pass
    
    @abstractmethod
    def get_with_changes(self, days: int = 7) -> List[Snapshot]:
        """Получает снэпшоты с изменениями за период"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Закрывает соединение"""
        pass


class SQLAlchemySnapshotRepository(SnapshotRepository):
    """SQLAlchemy реализация репозитория"""
    
    def __init__(self, database_url: str):
        self._db = DatabaseManager(database_url)
    
    def save(
        self,
        url: str,
        raw_html: str,
        text_content: str,
        api_name: Optional[str] = None,
        method_name: Optional[str] = None,
        content_type: str = 'html',
        structured_data: Optional[dict] = None,
        content_hash: Optional[str] = None,
        has_changes: bool = False,
        ai_summary: Optional[str] = None
    ) -> Snapshot:
        return self._db.save_snapshot(
            url=url,
            raw_html=raw_html,
            text_content=text_content,
            api_name=api_name,
            method_name=method_name,
            content_type=content_type,
            structured_data=structured_data,
            content_hash=content_hash,
            has_changes=has_changes,
            ai_summary=ai_summary
        )
    
    def get_latest(self, url: str) -> Optional[Snapshot]:
        return self._db.get_latest_snapshot(url)
    
    def get_history(self, url: str, limit: int = 10) -> List[Snapshot]:
        return self._db.get_snapshot_history(url, limit)
    
    def get_all_urls(self) -> List[str]:
        return self._db.get_all_urls()
    
    def get_with_changes(self, days: int = 7) -> List[Snapshot]:
        return self._db.get_snapshots_with_changes(days)
    
    def close(self) -> None:
        self._db.close()
