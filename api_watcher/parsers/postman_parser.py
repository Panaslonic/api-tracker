"""
Postman Parser - парсер для Postman коллекций
Извлекает информацию о запросах: name, method, url
"""

import requests
import json
from typing import Dict, Any, List, Optional

from api_watcher.config import Config


class PostmanParser:
    def __init__(self, user_agent: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or Config.USER_AGENT
        })

    def parse(self, url: str, **kwargs) -> Dict[str, Any]:
        """Парсит Postman коллекцию"""
        response = self.session.get(url, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Проверяем, что ответ не пустой
        if not response.text or not response.text.strip():
            raise Exception(f"Сервер вернул пустой ответ для {url}")
        
        # Проверяем, что это не HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type or response.text.strip().startswith(('<html', '<!DOCTYPE', '<!doctype')):
            raise Exception(f"Сервер вернул HTML вместо JSON для {url}. Content-Type: {content_type}")
        
        try:
            collection = response.json()
        except json.JSONDecodeError as e:
            preview = response.text[:200].strip()
            raise Exception(f"Ошибка парсинга JSON: {str(e)}. Начало ответа: {preview}")
        
        return {
            'url': url,
            'info': collection.get('info', {}),
            'items': self._extract_items(collection.get('item', []))
        }

    def _extract_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Извлекает информацию о запросах из коллекции"""
        result = []
        
        for item in items:
            if 'item' in item:
                # Это папка с подэлементами
                folder_items = self._extract_items(item['item'])
                result.extend([
                    {**sub_item, 'folder': item.get('name', 'Unnamed folder')}
                    for sub_item in folder_items
                ])
            else:
                # Это запрос
                request_info = self._extract_request_info(item)
                if request_info:
                    result.append(request_info)
        
        return result

    def _extract_request_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает информацию о конкретном запросе"""
        request = item.get('request', {})
        
        if not request:
            return None
        
        # Извлекаем URL
        url_info = request.get('url', {})
        if isinstance(url_info, str):
            url = url_info
        else:
            raw_url = url_info.get('raw', '')
            host = url_info.get('host', [])
            path = url_info.get('path', [])
            
            if isinstance(host, list):
                host = '.'.join(host)
            if isinstance(path, list):
                path = '/'.join(path)
            
            url = raw_url or f"{host}/{path}"
        
        return {
            'name': item.get('name', 'Unnamed request'),
            'method': request.get('method', 'GET'),
            'url': url,
            'description': item.get('description', ''),
            'headers': self._extract_headers(request.get('header', [])),
            'body': self._extract_body(request.get('body', {}))
        }

    def _extract_headers(self, headers: List[Dict[str, Any]]) -> Dict[str, str]:
        """Извлекает заголовки запроса"""
        result = {}
        for header in headers:
            if isinstance(header, dict) and not header.get('disabled', False):
                key = header.get('key', '')
                value = header.get('value', '')
                if key:
                    result[key] = value
        return result

    def _extract_body(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает информацию о теле запроса"""
        if not body:
            return {}
        
        mode = body.get('mode', '')
        result = {'mode': mode}
        
        if mode == 'raw':
            result['content'] = body.get('raw', '')
        elif mode == 'formdata':
            result['formdata'] = body.get('formdata', [])
        elif mode == 'urlencoded':
            result['urlencoded'] = body.get('urlencoded', [])
        
        return result