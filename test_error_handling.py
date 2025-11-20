#!/usr/bin/env python3
"""
Тест обработки ошибок в парсерах
"""

import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api_watcher'))

from parsers.json_parser import JSONParser
from parsers.openapi_parser import OpenAPIParser
from parsers.html_parser import HTMLParser


def test_json_parser_errors():
    """Тест обработки ошибок в JSON парсере"""
    parser = JSONParser()
    
    print("🧪 Тестирование JSON Parser...")
    
    # Тест 1: Несуществующий файл
    try:
        parser.parse("file://nonexistent.json")
        print("❌ FAIL: Должна быть ошибка для несуществующего файла")
    except Exception as e:
        if "Файл не найден" in str(e):
            print("✅ PASS: Корректная обработка несуществующего файла")
        else:
            print(f"⚠️ WARN: Неожиданное сообщение: {e}")
    
    # Тест 2: Timeout
    try:
        parser.parse("https://httpstat.us/200?sleep=35000")
        print("❌ FAIL: Должна быть ошибка timeout")
    except Exception as e:
        if "Timeout" in str(e) or "timeout" in str(e).lower():
            print("✅ PASS: Корректная обработка timeout")
        else:
            print(f"⚠️ WARN: Неожиданное сообщение: {e}")
    
    # Тест 3: HTTP 404
    try:
        parser.parse("https://httpbin.org/status/404")
        print("❌ FAIL: Должна быть ошибка 404")
    except Exception as e:
        if "404" in str(e):
            print("✅ PASS: Корректная обработка HTTP 404")
        else:
            print(f"⚠️ WARN: Неожиданное сообщение: {e}")
    
    # Тест 4: Невалидный JSON
    try:
        parser.parse("https://httpbin.org/html")
        print("❌ FAIL: Должна быть ошибка парсинга JSON")
    except Exception as e:
        if "парсинга JSON" in str(e) or "HTML вместо JSON" in str(e):
            print("✅ PASS: Корректная обработка невалидного JSON")
        else:
            print(f"⚠️ WARN: Неожиданное сообщение: {e}")


def test_openapi_parser_errors():
    """Тест обработки ошибок в OpenAPI парсере"""
    parser = OpenAPIParser()
    
    print("\n🧪 Тестирование OpenAPI Parser...")
    
    # Тест 1: HTTP 404
    try:
        parser.parse("https://httpbin.org/status/404")
        print("❌ FAIL: Должна быть ошибка 404")
    except Exception as e:
        if "404" in str(e):
            print("✅ PASS: Корректная обработка HTTP 404")
        else:
            print(f"⚠️ WARN: Неожиданное сообщение: {e}")
    
    # Тест 2: Невалидный JSON
    try:
        parser.parse("https://httpbin.org/html")
        print("❌ FAIL: Должна быть ошибка парсинга")
    except Exception as e:
        if "парсинга" in str(e):
            print("✅ PASS: Корректная обработка невалидного формата")
        else:
            print(f"⚠️ WARN: Неожиданное сообщение: {e}")


def test_html_parser_errors():
    """Тест обработки ошибок в HTML парсере"""
    parser = HTMLParser()
    
    print("\n🧪 Тестирование HTML Parser...")
    
    # Тест 1: HTTP 404
    try:
        parser.parse("https://httpbin.org/status/404")
        print("❌ FAIL: Должна быть ошибка 404")
    except Exception as e:
        if "404" in str(e):
            print("✅ PASS: Корректная обработка HTTP 404")
        else:
            print(f"⚠️ WARN: Неожиданное сообщение: {e}")
    
    # Тест 2: HTTP 403
    try:
        parser.parse("https://httpbin.org/status/403")
        print("❌ FAIL: Должна быть ошибка 403")
    except Exception as e:
        if "403" in str(e):
            print("✅ PASS: Корректная обработка HTTP 403")
        else:
            print(f"⚠️ WARN: Неожиданное сообщение: {e}")


def main():
    print("=" * 60)
    print("Тестирование обработки ошибок в парсерах")
    print("=" * 60)
    
    test_json_parser_errors()
    test_openapi_parser_errors()
    test_html_parser_errors()
    
    print("\n" + "=" * 60)
    print("✨ Тестирование завершено!")
    print("=" * 60)


if __name__ == "__main__":
    main()
