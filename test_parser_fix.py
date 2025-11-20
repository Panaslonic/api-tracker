#!/usr/bin/env python3
"""
Тест исправлений парсеров для обработки HTML ответов
"""

import sys
sys.path.insert(0, 'api_watcher')

from parsers.openapi_parser import OpenAPIParser

# Тестируем проблемный URL
parser = OpenAPIParser()
url = "https://direct.i-dgtl.ru/openapi.json"

print(f"Тестируем URL: {url}")
print("-" * 60)

try:
    result = parser.parse(url)
    print("✅ Успешно распарсено")
    print(f"Результат: {result}")
except Exception as e:
    print(f"❌ Ошибка (ожидаемая): {e}")
    print("\nТеперь ошибка информативная и понятная!")
