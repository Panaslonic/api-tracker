"""
JSON Parser - парсер для произвольных JSON Schema
Сравнивает ключи и значения структуры
"""

import requests
import json
from typing import Dict, Any


class JSONParser:
    def __init__(self):
        self.session = requests.Session()

    def parse(self, url: str, **kwargs) -> Dict[str, Any]:
        """Парсит JSON документ"""
        if url.startswith('file://') or not url.startswith('http'):
            # Локальный файл
            import urllib.parse
            import os
            if url.startswith('file://'):
                file_path = urllib.parse.unquote(url[7:])  # Убираем file://
            else:
                file_path = url
            
            # Если путь относительный, делаем его абсолютным
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Удаленный файл
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
        
        return {
            'url': url,
            'structure': self._analyze_structure(data),
            'keys': self._extract_all_keys(data),
            'data': data  # Сохраняем полные данные для сравнения
        }

    def _analyze_structure(self, data: Any, path: str = '') -> Dict[str, Any]:
        """Анализирует структуру JSON"""
        if isinstance(data, dict):
            return {
                'type': 'object',
                'keys': list(data.keys()),
                'children': {
                    key: self._analyze_structure(value, f"{path}.{key}" if path else key)
                    for key, value in data.items()
                }
            }
        elif isinstance(data, list):
            return {
                'type': 'array',
                'length': len(data),
                'item_types': list(set(type(item).__name__ for item in data)) if data else []
            }
        else:
            return {
                'type': type(data).__name__,
                'value': str(data) if len(str(data)) < 100 else str(data)[:100] + '...'
            }

    def _extract_all_keys(self, data: Any, keys: set = None) -> list:
        """Извлекает все ключи из JSON структуры"""
        if keys is None:
            keys = set()
        
        if isinstance(data, dict):
            keys.update(data.keys())
            for value in data.values():
                self._extract_all_keys(value, keys)
        elif isinstance(data, list):
            for item in data:
                self._extract_all_keys(item, keys)
        
        return sorted(list(keys))