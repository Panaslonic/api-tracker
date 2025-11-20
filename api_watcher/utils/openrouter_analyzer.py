"""
OpenRouter AI Analyzer for API changes
Анализ изменений через OpenRouter API
"""

import logging
import json
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)


class OpenRouterAnalyzer:
    """Анализ изменений API через OpenRouter"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3.5-sonnet",
        site_url: Optional[str] = None,
        app_name: Optional[str] = "API Watcher"
    ):
        """
        Инициализация OpenRouter analyzer
        
        Args:
            api_key: OpenRouter API ключ
            model: Модель для использования (по умолчанию Claude 3.5 Sonnet)
            site_url: URL вашего сайта (опционально)
            app_name: Название приложения
        """
        self.api_key = api_key
        self.model = model
        self.site_url = site_url
        self.app_name = app_name
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def _make_request(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Выполняет запрос к OpenRouter API
        
        Args:
            messages: Список сообщений для модели
            
        Returns:
            Ответ модели или None при ошибке
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Добавляем опциональные заголовки
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-Title"] = self.app_name
        
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка запроса к OpenRouter: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"❌ Ошибка парсинга ответа OpenRouter: {e}")
            return None
    
    def analyze_changes(
        self,
        old_text: str,
        new_text: str,
        api_name: Optional[str] = None,
        method_name: Optional[str] = None
    ) -> Dict:
        """
        Анализирует изменения в HTML/текстовом контенте
        
        Args:
            old_text: Старая версия текста
            new_text: Новая версия текста
            api_name: Название API
            method_name: Название метода
            
        Returns:
            {
                'has_significant_changes': bool,
                'summary': str,
                'severity': str,
                'key_changes': List[str]
            }
        """
        context = f"API: {api_name}" if api_name else "API Documentation"
        if method_name:
            context += f", Method: {method_name}"
        
        prompt = f"""Проанализируй изменения в документации API.

{context}

СТАРАЯ ВЕРСИЯ:
{old_text[:3000]}

НОВАЯ ВЕРСИЯ:
{new_text[:3000]}

Ответь в формате JSON:
{{
    "has_significant_changes": true/false,
    "summary": "краткое описание изменений на русском",
    "severity": "minor/moderate/major",
    "key_changes": ["изменение 1", "изменение 2", ...]
}}

Критерии значимости:
- major: breaking changes, удаление методов, изменение параметров
- moderate: новые методы, изменение поведения
- minor: исправления опечаток, форматирование

Если изменения незначительные (даты, версии, мелкие правки) - has_significant_changes: false"""

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self._make_request(messages)
        
        if not response:
            return {
                'has_significant_changes': True,
                'summary': 'Обнаружены изменения (AI анализ недоступен)',
                'severity': 'moderate',
                'key_changes': []
            }
        
        try:
            # Пытаемся извлечь JSON из ответа
            # Модель может обернуть JSON в markdown блок
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            else:
                json_str = response.strip()
            
            result = json.loads(json_str)
            
            # Валидация результата
            if 'has_significant_changes' not in result:
                result['has_significant_changes'] = True
            if 'summary' not in result:
                result['summary'] = 'Обнаружены изменения'
            if 'severity' not in result:
                result['severity'] = 'moderate'
            if 'key_changes' not in result:
                result['key_changes'] = []
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON ответа: {e}")
            logger.debug(f"Ответ модели: {response}")
            
            return {
                'has_significant_changes': True,
                'summary': 'Обнаружены изменения (ошибка парсинга AI ответа)',
                'severity': 'moderate',
                'key_changes': []
            }
    
    def analyze_openapi_changes(
        self,
        changes: Dict,
        api_name: Optional[str] = None
    ) -> str:
        """
        Анализирует изменения в OpenAPI спецификации
        
        Args:
            changes: Словарь с изменениями из SmartComparator
            api_name: Название API
            
        Returns:
            Текстовое описание изменений
        """
        context = f"API: {api_name}" if api_name else "OpenAPI Specification"
        
        prompt = f"""Проанализируй изменения в OpenAPI спецификации.

{context}

ИЗМЕНЕНИЯ:
{json.dumps(changes, indent=2, ensure_ascii=False)[:4000]}

Создай краткую сводку изменений на русском языке (2-3 предложения).
Укажи самые важные изменения: новые/удаленные endpoints, изменения в параметрах, breaking changes.
Ответь только текстом, без JSON."""

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self._make_request(messages)
        
        if not response:
            # Fallback на простое описание
            summary_parts = []
            if 'added' in changes and changes['added']:
                summary_parts.append(f"Добавлено: {len(changes['added'])} элементов")
            if 'removed' in changes and changes['removed']:
                summary_parts.append(f"Удалено: {len(changes['removed'])} элементов")
            if 'modified' in changes and changes['modified']:
                summary_parts.append(f"Изменено: {len(changes['modified'])} элементов")
            
            return "Обнаружены изменения в OpenAPI спецификации. " + ", ".join(summary_parts)
        
        return response.strip()
    
    def get_model_info(self) -> Dict:
        """
        Возвращает информацию о текущей модели
        
        Returns:
            Словарь с информацией о модели
        """
        return {
            'model': self.model,
            'provider': 'OpenRouter',
            'api_url': self.api_url
        }
