"""
Gemini AI analyzer for detecting and summarizing changes
Использует Google Gemini для анализа изменений в документации
"""

import google.generativeai as genai
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Анализатор изменений на базе Gemini AI"""
    
    def __init__(self, api_key: str, model_name: str = 'gemini-pro'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def analyze_changes(
        self,
        old_text: str,
        new_text: str,
        api_name: Optional[str] = None,
        method_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Анализирует изменения между двумя версиями текста
        
        Returns:
            {
                'has_significant_changes': bool,
                'summary': str,
                'details': str
            }
        """
        context = ""
        if api_name:
            context += f"API: {api_name}\n"
        if method_name:
            context += f"Method: {method_name}\n"
        
        prompt = f"""Ты - эксперт по анализу изменений в API документации.

{context}

Сравни два текста документации (старый и новый) и определи:

1. Есть ли СУЩЕСТВЕННЫЕ изменения? (игнорируй мелкие правки, опечатки, форматирование)
2. Если есть существенные изменения - дай краткую сводку (2-3 предложения)
3. Перечисли ключевые изменения списком

СТАРАЯ ВЕРСИЯ:
---
{old_text[:15000]}
---

НОВАЯ ВЕРСИЯ:
---
{new_text[:15000]}
---

Ответь в формате JSON:
{{
    "has_significant_changes": true/false,
    "summary": "краткая сводка изменений",
    "key_changes": [
        "изменение 1",
        "изменение 2"
    ],
    "severity": "minor/moderate/major"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Извлекаем JSON из ответа
            import json
            import re
            
            # Ищем JSON в ответе
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback если JSON не найден
                result = {
                    'has_significant_changes': True,
                    'summary': result_text,
                    'key_changes': [],
                    'severity': 'unknown'
                }
            
            logger.info(f"✅ Gemini: анализ завершен, изменения: {result.get('has_significant_changes')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Gemini ошибка: {e}")
            return {
                'has_significant_changes': False,
                'summary': f'Ошибка анализа: {str(e)}',
                'key_changes': [],
                'severity': 'error'
            }
    
    def analyze_openapi_changes(
        self,
        changes_dict: Dict,
        api_name: Optional[str] = None
    ) -> str:
        """
        Создает человекочитаемую сводку изменений OpenAPI
        
        Args:
            changes_dict: Словарь изменений из deepdiff
            api_name: Название API
        
        Returns:
            Текстовая сводка изменений
        """
        context = f"API: {api_name}\n" if api_name else ""
        
        prompt = f"""Ты - эксперт по OpenAPI спецификациям.

{context}

Проанализируй следующие изменения в OpenAPI спецификации и создай краткую, понятную сводку для разработчиков.

Изменения (в формате DeepDiff):
---
{str(changes_dict)[:10000]}
---

Создай сводку, которая включает:
1. Краткое описание (1-2 предложения)
2. Ключевые изменения по категориям:
   - Новые endpoints
   - Удаленные endpoints
   - Измененные параметры
   - Изменения в схемах данных
   - Breaking changes (если есть)

Формат ответа - читаемый текст на русском языке.
"""
        
        try:
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            logger.info(f"✅ Gemini: OpenAPI сводка создана")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Gemini ошибка при анализе OpenAPI: {e}")
            return f"Обнаружены изменения в OpenAPI спецификации. Детали: {str(changes_dict)[:500]}"
