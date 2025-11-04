#!/usr/bin/env python3
"""
Скрипт для запуска тестов API Watcher
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"\n🔄 {description}...")
    print(f"Команда: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            if result.stdout:
                print("Вывод:")
                print(result.stdout)
        else:
            print(f"❌ {description} - ошибка (код: {result.returncode})")
            if result.stderr:
                print("Ошибки:")
                print(result.stderr)
            if result.stdout:
                print("Вывод:")
                print(result.stdout)
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print(f"❌ Команда не найдена: {command[0]}")
        return False
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        return False


def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    try:
        import pytest
        import pytest_asyncio
        import pytest_mock
        import pytest_cov
        print("✅ Все необходимые пакеты для тестирования установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует пакет: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False


def main():
    """Основная функция запуска тестов"""
    print("🧪 API Watcher - Запуск тестов")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    # Определяем тип запуска
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"
    
    success = True
    
    if test_type in ["all", "unit"]:
        # Запуск юнит тестов
        unit_tests = [
            "python", "-m", "pytest", 
            "tests/test_config.py",
            "tests/test_utils.py", 
            "tests/test_storage.py",
            "tests/test_notifiers.py",
            "tests/test_parsers.py",
            "-v", "--tb=short"
        ]
        
        if not run_command(unit_tests, "Юнит тесты"):
            success = False
    
    if test_type in ["all", "main"]:
        # Запуск тестов основного модуля
        main_tests = [
            "python", "-m", "pytest", 
            "tests/test_main.py",
            "-v", "--tb=short"
        ]
        
        if not run_command(main_tests, "Тесты основного модуля"):
            success = False
    
    if test_type in ["all", "integration"]:
        # Запуск интеграционных тестов
        integration_tests = [
            "python", "-m", "pytest", 
            "tests/test_integration.py",
            "-v", "--tb=short"
        ]
        
        if not run_command(integration_tests, "Интеграционные тесты"):
            success = False
    
    if test_type == "coverage":
        # Запуск с покрытием кода
        coverage_tests = [
            "python", "-m", "pytest", 
            "tests/",
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-exclude=tests/*",
            "-v"
        ]
        
        if run_command(coverage_tests, "Тесты с покрытием кода"):
            print("\n📊 HTML отчет о покрытии создан в htmlcov/index.html")
        else:
            success = False
    
    if test_type == "quick":
        # Быстрые тесты (без интеграционных)
        quick_tests = [
            "python", "-m", "pytest", 
            "tests/",
            "-x",  # Остановиться на первой ошибке
            "--tb=line",
            "-q"  # Тихий режим
        ]
        
        if not run_command(quick_tests, "Быстрые тесты"):
            success = False
    
    # Итоговый результат
    print("\n" + "=" * 50)
    if success:
        print("🎉 Все тесты выполнены успешно!")
        sys.exit(0)
    else:
        print("💥 Некоторые тесты завершились с ошибками")
        sys.exit(1)


def print_help():
    """Выводит справку по использованию"""
    print("""
Использование: python run_tests.py [тип_тестов]

Типы тестов:
  all         - Все тесты (по умолчанию)
  unit        - Только юнит тесты
  main        - Тесты основного модуля
  integration - Интеграционные тесты
  coverage    - Тесты с отчетом о покрытии кода
  quick       - Быстрые тесты (останавливается на первой ошибке)
  help        - Показать эту справку

Примеры:
  python run_tests.py
  python run_tests.py unit
  python run_tests.py coverage
  python run_tests.py quick
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "help":
        print_help()
    else:
        main()