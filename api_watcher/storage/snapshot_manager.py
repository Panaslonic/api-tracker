"""
Snapshot Manager - управление снимками состояния документации
Сохраняет и загружает snapshot-файлы для сравнения изменений
"""

import json
import os
import hashlib
import re
from typing import Dict, Any, Optional
from datetime import datetime


class SnapshotManager:
    def __init__(self, snapshots_dir: str = 'snapshots'):
        self.snapshots_dir = snapshots_dir
        self._ensure_snapshots_dir()

    def _ensure_snapshots_dir(self) -> None:
        """Создает директорию для снимков, если она не существует"""
        if not os.path.exists(self.snapshots_dir):
            os.makedirs(self.snapshots_dir)

    def _get_snapshot_filename(self, url: str, api_name: str = None, method_name: str = None, method_filter: str = None) -> str:
        """Генерирует имя файла для снимка на основе URL и метаданных"""
        # Создаем уникальный идентификатор, включающий URL и фильтр метода
        unique_key = url
        if method_filter:
            unique_key += f"#{method_filter}"
        
        url_hash = hashlib.md5(unique_key.encode('utf-8')).hexdigest()[:8]
        
        # Создаем читаемое имя файла
        if api_name and method_name:
            # Очищаем названия от недопустимых символов
            safe_api = re.sub(r'[^\w\-_]', '_', api_name)[:20]
            safe_method = re.sub(r'[^\w\-_]', '_', method_name)[:30]
            return f"{safe_api}_{safe_method}_{url_hash}.json"
        else:
            return f"snapshot_{url_hash}.json"

    def save_snapshot(self, url: str, data: Dict[str, Any], api_name: str = None, method_name: str = None, method_filter: str = None) -> None:
        """Сохраняет снимок данных с метаданными"""
        filename = self._get_snapshot_filename(url, api_name, method_name, method_filter)
        filepath = os.path.join(self.snapshots_dir, filename)
        
        # Извлекаем название метода из данных, если не передано
        if not method_name and isinstance(data, dict):
            method_content = data.get('method_content', {})
            if isinstance(method_content, dict):
                method_name = method_content.get('method_name', 'Unknown Method')
        
        snapshot = {
            'metadata': {
                'api_name': api_name or 'Unknown API',
                'method_name': method_name or 'Unknown Method',
                'snapshot_date': datetime.now().strftime('%Y-%m-%d'),
                'snapshot_time': datetime.now().strftime('%H:%M:%S'),
                'full_timestamp': datetime.now().isoformat()
            },
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
            print(f"💾 Снимок сохранен: {filepath}")
        except Exception as e:
            print(f"❌ Ошибка сохранения снимка для {url}: {e}")

    def load_snapshot(self, url: str, method_filter: str = None) -> Optional[Dict[str, Any]]:
        """Загружает предыдущий снимок данных"""
        # Создаем уникальный ключ, включающий URL и фильтр метода
        unique_key = url
        if method_filter:
            unique_key += f"#{method_filter}"
        
        url_hash = hashlib.md5(unique_key.encode('utf-8')).hexdigest()[:8]
        
        # Ищем файлы, содержащие этот хеш
        if os.path.exists(self.snapshots_dir):
            for filename in os.listdir(self.snapshots_dir):
                if url_hash in filename and filename.endswith('.json'):
                    filepath = os.path.join(self.snapshots_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            snapshot = json.load(f)
                        # Проверяем, что это правильный URL
                        if snapshot.get('url') == url:
                            return snapshot.get('data')
                    except Exception as e:
                        print(f"❌ Ошибка загрузки снимка {filename}: {e}")
                        continue
        
        return None

    def get_snapshot_info(self, url: str) -> Optional[Dict[str, str]]:
        """Получает информацию о снимке (без данных)"""
        filename = self._get_snapshot_filename(url)
        filepath = os.path.join(self.snapshots_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            return {
                'url': snapshot.get('url'),
                'timestamp': snapshot.get('timestamp'),
                'filename': filename
            }
        except Exception as e:
            print(f"❌ Ошибка получения информации о снимке для {url}: {e}")
            return None

    def list_snapshots(self) -> list:
        """Возвращает список всех снимков"""
        snapshots = []
        
        if not os.path.exists(self.snapshots_dir):
            return snapshots
        
        for filename in os.listdir(self.snapshots_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.snapshots_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        snapshot = json.load(f)
                    snapshots.append({
                        'url': snapshot.get('url'),
                        'timestamp': snapshot.get('timestamp'),
                        'filename': filename
                    })
                except Exception as e:
                    print(f"❌ Ошибка чтения снимка {filename}: {e}")
        
        return sorted(snapshots, key=lambda x: x.get('timestamp', ''))

    def delete_snapshot(self, url: str) -> bool:
        """Удаляет снимок для указанного URL"""
        filename = self._get_snapshot_filename(url)
        filepath = os.path.join(self.snapshots_dir, filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"🗑️ Снимок удален: {filepath}")
                return True
            except Exception as e:
                print(f"❌ Ошибка удаления снимка для {url}: {e}")
                return False
        return False