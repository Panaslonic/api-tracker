"""
Database models and manager for API Watcher
Хранит HTML-снэпшоты с историей изменений
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, List
import json

Base = declarative_base()


class Snapshot(Base):
    """Модель для хранения HTML-снэпшотов"""
    __tablename__ = 'snapshots'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False, index=True)
    api_name = Column(String(200))
    method_name = Column(String(200))
    content_type = Column(String(50))  # html, openapi, json, etc.
    
    # Сырой HTML контент
    raw_html = Column(Text)
    
    # Текстовая версия для AI
    text_content = Column(Text)
    
    # Структурированные данные (для OpenAPI, JSON)
    structured_data = Column(Text)  # JSON string
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    has_changes = Column(Boolean, default=False)
    ai_summary = Column(Text)  # AI-сводка изменений
    
    # Хеш для быстрого сравнения
    content_hash = Column(String(64))


class DatabaseManager:
    """Менеджер для работы с БД"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_snapshot(
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
        """Сохраняет новый снэпшот в БД"""
        snapshot = Snapshot(
            url=url,
            api_name=api_name,
            method_name=method_name,
            content_type=content_type,
            raw_html=raw_html,
            text_content=text_content,
            structured_data=json.dumps(structured_data) if structured_data else None,
            content_hash=content_hash,
            has_changes=has_changes,
            ai_summary=ai_summary
        )
        
        self.session.add(snapshot)
        self.session.commit()
        return snapshot
    
    def get_latest_snapshot(self, url: str) -> Optional[Snapshot]:
        """Получает последний снэпшот для URL"""
        return self.session.query(Snapshot)\
            .filter(Snapshot.url == url)\
            .order_by(Snapshot.created_at.desc())\
            .first()
    
    def get_snapshot_history(self, url: str, limit: int = 10) -> List[Snapshot]:
        """Получает историю снэпшотов для URL"""
        return self.session.query(Snapshot)\
            .filter(Snapshot.url == url)\
            .order_by(Snapshot.created_at.desc())\
            .limit(limit)\
            .all()
    
    def get_all_urls(self) -> List[str]:
        """Получает список всех отслеживаемых URL"""
        result = self.session.query(Snapshot.url).distinct().all()
        return [row[0] for row in result]
    
    def get_snapshots_with_changes(self, days: int = 7) -> List[Snapshot]:
        """Получает снэпшоты с изменениями за последние N дней"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return self.session.query(Snapshot)\
            .filter(Snapshot.has_changes == True)\
            .filter(Snapshot.created_at >= cutoff_date)\
            .order_by(Snapshot.created_at.desc())\
            .all()
    
    def close(self):
        """Закрывает соединение с БД"""
        self.session.close()
