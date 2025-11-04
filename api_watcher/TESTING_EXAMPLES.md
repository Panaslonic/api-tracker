# Примеры использования тестов API Watcher

## Быстрый старт

### 1. Установка зависимостей
```bash
cd api_watcher
pip install -r requirements.txt
```

### 2. Запуск всех тестов
```bash
# Способ 1: Через скрипт
python run_tests.py

# Способ 2: Через Makefile
make test

# Способ 3: Напрямую через pytest
pytest tests/ -v
```

## Примеры запуска различных типов тестов

### Юнит тесты
```bash
# Все юнит тесты
python run_tests.py unit

# Конкретный модуль
pytest tests/test_config.py -v

# Конкретный тест
pytest tests/test_config.py::TestConfig::test_default_values -v
```

### Тесты парсеров
```bash
# Все тесты парсеров
pytest tests/test_parsers.py -v

# Только JSON парсер
pytest tests/test_parsers.py::TestJSONParser -v

# Конкретный тест JSON парсера
pytest tests/test_parsers.py::TestJSONParser::test_parse_valid_json_url -v
```

### Интеграционные тесты
```bash
# Все интеграционные тесты
python run_tests.py integration

# Конкретный интеграционный тест
pytest tests/test_integration.py::TestAPIWatcherIntegration::test_full_workflow_first_run -v
```

## Тестирование с покрытием кода

### Генерация отчета о покрытии
```bash
# HTML отчет
python run_tests.py coverage

# Терминальный отчет
pytest tests/ --cov=. --cov-report=term-missing

# Только покрытие без тестов
pytest tests/ --cov=. --cov-report=term --no-cov-on-fail
```

### Просмотр отчета
```bash
# Открыть HTML отчет (создается в htmlcov/)
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Отладка тестов

### Подробный вывод
```bash
# Максимальная детализация
pytest tests/ -v -s --tb=long

# Показать все print() в тестах
pytest tests/ -s

# Остановиться на первой ошибке
pytest tests/ -x
```

### Использование отладчика
```python
# В коде теста
import pdb; pdb.set_trace()

# Или через pytest
pytest tests/test_main.py --pdb
```

### Фильтрация тестов
```bash
# Запустить тесты по имени
pytest tests/ -k "test_config"

# Исключить определенные тесты
pytest tests/ -k "not integration"

# По маркерам (если используются)
pytest tests/ -m "not slow"
```

## Примеры тестирования конкретных компонентов

### Тестирование конфигурации
```bash
# Все тесты конфигурации
pytest tests/test_config.py -v

# Тест переменных окружения
pytest tests/test_config.py::TestConfig::test_environment_variables -v

# Тест Telegram настроек
pytest tests/test_config.py::TestConfig::test_telegram_configured -v
```

### Тестирование основного модуля
```bash
# Тесты APIWatcher
pytest tests/test_main.py::TestAPIWatcher -v

# Тест обработки URL с повторными попытками
pytest tests/test_main.py::TestAPIWatcher::test_process_url_with_retry_success_after_retries -v

# Тесты HealthChecker
pytest tests/test_main.py::TestHealthChecker -v
```

### Тестирование парсеров
```bash
# JSON парсер
pytest tests/test_parsers.py::TestJSONParser::test_parse_valid_json_url -v

# HTML парсер с селектором
pytest tests/test_parsers.py::TestHTMLParser::test_parse_html_with_selector -v

# OpenAPI парсер с фильтром
pytest tests/test_parsers.py::TestOpenAPIParser::test_parse_openapi_with_method_filter -v
```

### Тестирование хранилища
```bash
# Все тесты SnapshotManager
pytest tests/test_storage.py::TestSnapshotManager -v

# Тест сохранения снимка
pytest tests/test_storage.py::TestSnapshotManager::test_save_snapshot -v

# Тест с фильтром методов
pytest tests/test_storage.py::TestSnapshotManager::test_save_snapshot_with_method_filter -v
```

### Тестирование уведомителей
```bash
# Консольный уведомитель
pytest tests/test_notifiers.py::TestConsoleNotifier -v

# Telegram уведомитель
pytest tests/test_notifiers.py::TestTelegramNotifier -v

# Тест обработки ошибок Telegram
pytest tests/test_notifiers.py::TestTelegramNotifier::test_notify_changes_network_error -v
```

## Создание собственных тестов

### Шаблон простого теста
```python
# tests/test_my_feature.py
import pytest
from my_module import MyClass

class TestMyClass:
    def test_basic_functionality(self):
        """Тест базовой функциональности"""
        # Arrange
        obj = MyClass()
        
        # Act
        result = obj.do_something()
        
        # Assert
        assert result == expected_value
```

### Шаблон теста с моками
```python
import pytest
from unittest.mock import Mock, patch
from my_module import MyClass

class TestMyClassWithMocks:
    @patch('my_module.external_service')
    def test_with_external_dependency(self, mock_service):
        """Тест с внешней зависимостью"""
        # Arrange
        mock_service.return_value = "mocked_response"
        obj = MyClass()
        
        # Act
        result = obj.call_external_service()
        
        # Assert
        assert result == "mocked_response"
        mock_service.assert_called_once()
```

### Шаблон асинхронного теста
```python
import pytest
import asyncio
from my_async_module import MyAsyncClass

class TestMyAsyncClass:
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Тест асинхронной функциональности"""
        # Arrange
        obj = MyAsyncClass()
        
        # Act
        result = await obj.async_method()
        
        # Assert
        assert result is not None
```

## Полезные команды для разработки

### Непрерывное тестирование
```bash
# Запуск тестов при изменении файлов (требует pytest-watch)
pip install pytest-watch
ptw tests/
```

### Параллельное выполнение тестов
```bash
# Установка pytest-xdist
pip install pytest-xdist

# Запуск в несколько процессов
pytest tests/ -n auto
```

### Профилирование тестов
```bash
# Показать самые медленные тесты
pytest tests/ --durations=10

# Профилирование с cProfile
pytest tests/ --profile
```

## Интеграция с IDE

### VS Code
Добавьте в `.vscode/settings.json`:
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "python.testing.autoTestDiscoverOnSaveEnabled": true
}
```

### PyCharm
1. Откройте Settings → Tools → Python Integrated Tools
2. Выберите pytest как Default test runner
3. Укажите путь к тестам: `tests/`

## Troubleshooting

### Проблема: ModuleNotFoundError
```bash
# Решение: добавьте текущую директорию в PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/

# Или используйте -p no:cacheprovider
pytest tests/ -p no:cacheprovider
```

### Проблема: Тесты не находят фикстуры
```bash
# Убедитесь, что conftest.py находится в правильном месте
ls tests/conftest.py

# Запустите с подробным выводом
pytest tests/ -v --tb=short
```

### Проблема: Медленные тесты
```bash
# Найдите медленные тесты
pytest tests/ --durations=0

# Запустите только быстрые тесты
pytest tests/ -m "not slow"
```

## Автоматизация

### Pre-commit хуки
Создайте `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: make test-quick
        language: system
        pass_filenames: false
```

### GitHub Actions
Тесты автоматически запускаются при push и pull request через `.github/workflows/ci.yml`

### Локальная автоматизация
```bash
# Создайте alias для быстрого тестирования
echo "alias test-api='cd api_watcher && python run_tests.py quick'" >> ~/.bashrc
source ~/.bashrc

# Теперь можно использовать
test-api
```