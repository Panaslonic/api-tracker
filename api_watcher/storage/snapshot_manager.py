"""
Snapshot Manager - управление снимками состояния документации
Сохраняет и загружает snapshot-файлы для сравнения изменений
"""

import json
import os
import hashlib
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

    def _get_snapshot_filename(self, url: str) -> str:
        """Генерирует имя файла для снимка на основе URL"""
        # Создаем хеш от URL для безопасного имени файла
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        return f"{url_hash}.json"

    def save_snapshot(self, url: str, data: Dict[str, Any]) -> None:
        """Сохраняет снимок данных"""
        filename = self._get_snapshot_filename(url)
        filepath = os.path.join(self.snapshots_dir, filename)
        
        snapshot = {
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

    def load_snapshot(self, url: str) -> Optional[Dict[str, Any]]:
        """Загружает предыдущий снимок данных"""
        filename = self._get_snapshot_filename(url)
        filepath = os.path.join(self.snapshots_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            return snapshot.get('data')
        except Exception as e:
            print(f"❌ Ошибка загрузки снимка для {url}: {e}")
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