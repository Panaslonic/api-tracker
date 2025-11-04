# Тесты API Watcher

Этот каталог содержит полный набор тестов для проекта API Watcher.

## Структура тестов

```
tests/
├── __init__.py              # Пакет тестов
├── conftest.py             # Конфигурация pytest и фикстуры
├── test_config.py          # Тесты конфигурации
├── test_main.py            # Тесты основного модуля
├── test_parsers.py         # Тесты парсеров
├── test_utils.py           # Тесты утилит
├── test_storage.py         # Тесты системы хранения
├── test_notifiers.py       # Тесты уведомителей
├── test_integration.py     # Интеграционные тесты
└── README.md               # Этот файл
```

## Типы тестов

### 1. Юнит тесты
- **test_config.py** - тестирование конфигурации приложения
- **test_utils.py** - тестирование утилит сравнения
- **test_storage.py** - тестирование системы хранения снимков
- **test_notifiers.py** - тестирование уведомителей
- **test_parsers.py** - тестирование парсеров различных форматов

### 2. Тесты основного модуля
- **test_main.py** - тестирование основной логики APIWatcher

### 3. Интеграционные тесты
- **test_integration.py** - тестирование полного рабочего процесса

## Запуск тестов

### Быстрый старт
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск всех тестов
python run_tests.py

# Или с помощью Makefile
make test
```

### Различные способы запуска

#### 1. Все тесты
```bash
python run_tests.py all
# или
make test
```

#### 2. Только юнит тесты
```bash
python run_tests.py unit
# или
make test-unit
```

#### 3. Тесты основного модуля
```bash
python run_tests.py main
# или
make test-main
```

#### 4. Интеграционные тесты
```bash
python run_tests.py integration
# или
make test-integration
```

#### 5. Тесты с покрытием кода
```bash
python run_tests.py coverage
# или
make test-coverage
```

#### 6. Быстрые тесты (остановка на первой ошибке)
```bash
python run_tests.py quick
# или
make test-quick
```

### Прямой запуск через pytest
```bash
# Все тесты
pytest tests/ -v

# Конкретный файл
pytest tests/test_config.py -v

# Конкретный тест
pytest tests/test_config.py::TestConfig::test_default_values -v

# С покрытием кода
pytest tests/ --cov=. --cov-report=html
```

## Фикстуры

В `conftest.py` определены следующие фикстуры:

- **temp_dir** - временная директория для тестов
- **sample_urls** - тестовые URL конфигурации
- **sample_json_data** - тестовые JSON данные
- **modified_json_data** - модифицированные JSON данные
- **mock_aiohttp_session** - мок для aiohttp сессии
- **mock_response** - мок для HTTP ответа
- **setup_test_env** - автоматическая настройка тестового окружения

## Моки и заглушки

Тесты используют моки для:
- HTTP запросов (requests, aiohttp)
- Файловых операций
- Внешних API (Telegram)
- Парсеров документации
- Системы уведомлений

## Покрытие кода

Для генерации отчета о покрытии кода:

```bash
make test-coverage
```

HTML отчет будет создан в `htmlcov/index.html`

## Переменные окружения для тестов

Тесты автоматически настраивают следующие переменные:
- `API_WATCHER_SNAPSHOTS_DIR` - временная директория для снимков
- `API_WATCHER_URLS_FILE` - временный файл URLs
- `TELEGRAM_BOT_TOKEN` - токен для тестов Telegram (если нужен)
- `TELEGRAM_CHAT_ID` - ID чата для тестов Telegram (если нужен)

## Отладка тестов

### Запуск с подробным выводом
```bash
pytest tests/ -v -s
```

### Запуск конкретного теста с отладкой
```bash
pytest tests/test_main.py::TestAPIWatcher::test_load_urls_success -v -s --tb=long
```

### Использование pdb для отладки
```python
import pdb; pdb.set_trace()
```

## Добавление новых тестов

### Структура теста
```python
import pytest
from unittest.mock import Mock, patch

class TestNewFeature:
    """Тесты новой функциональности"""
    
    def test_basic_functionality(self):
        """Тест базовой функциональности"""
        # Arrange
        # Act
        # Assert
        pass
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Тест асинхронной функциональности"""
        # Arrange
        # Act
        # Assert
        pass
```

### Рекомендации
1. Используйте описательные имена тестов
2. Следуйте паттерну Arrange-Act-Assert
3. Мокайте внешние зависимости
4. Тестируйте как успешные, так и ошибочные сценарии
5. Используйте фикстуры для повторяющихся данных

## Непрерывная интеграция

Для CI/CD используйте:
```bash
make ci
```

Эта команда выполняет:
1. Очистку временных файлов
2. Проверку линтером
3. Запуск всех тестов с покрытием

## Требования

- Python 3.7+
- pytest >= 7.4.0
- pytest-asyncio >= 0.21.0
- pytest-mock >= 3.11.0
- pytest-cov >= 4.1.0

## Полезные команды

```bash
# Показать все доступные команды
make help

# Настроить среду разработки
make setup-dev

# Очистить временные файлы
make clean

# Проверить код линтером
make lint

# Форматировать код
make format
```