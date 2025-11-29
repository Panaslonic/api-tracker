# API Watcher V2

Микросервис для мониторинга изменений в API документации с AI-анализом.

## Возможности

- 🗄️ **База данных** - полная история изменений в SQLite/PostgreSQL
- 🌐 **ZenRows** - обход защиты сайтов (Cloudflare, reCAPTCHA)
- 🤖 **OpenRouter AI** - умный анализ изменений через 100+ моделей
- 💬 **Slack + Webhook** - уведомления с форматированием
- 🎯 **Умное сравнение** - структурный анализ OpenAPI + AI
- 🔍 **Автопоиск документации** - поиск новых ссылок при ошибках
- 📋 **5 типов документации** - HTML, OpenAPI, JSON, Postman, Markdown

## Установка

```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate для Windows
pip install -r requirements.txt
cp .env.example ../.env
```

## Настройка

### .env файл

```bash
# База данных
DATABASE_URL=sqlite:///api_watcher.db

# AI анализ (рекомендуется)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Уведомления
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#api-changes
WEBHOOK_URL=https://your-webhook.com/endpoint

# Опционально
ZENROWS_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

### urls.json

```json
[
  {
    "url": "https://docs.stripe.com/api/customers",
    "api_name": "Stripe API",
    "method_name": "Customers"
  },
  {
    "url": "https://petstore3.swagger.io/api/v3/openapi.json",
    "api_name": "Petstore",
    "method_name": "Pets"
  }
]
```

## Запуск

```bash
# Основной запуск
python -m api_watcher.watcher_v2

# Еженедельная проверка с дайджестом
python weekly_check.py

# Тестирование конфигурации
python test_v2.py
```

## Структура проекта

```
api_watcher/
├── watcher_v2.py              # Основной модуль V2
├── weekly_check.py            # Еженедельная проверка
├── test_v2.py                 # Тесты конфигурации
├── config.py                  # Конфигурация
├── parsers/                   # Парсеры документации
│   ├── html_parser.py
│   ├── openapi_parser.py
│   ├── json_parser.py
│   ├── postman_parser.py
│   └── md_parser.py
├── storage/
│   └── database.py            # SQLite/PostgreSQL хранилище
├── notifier/
│   ├── slack_notifier.py      # Slack уведомления
│   ├── webhook_notifier.py    # Webhook уведомления
│   ├── telegram_notifier.py   # Telegram уведомления
│   └── console_notifier.py    # Консольные уведомления
├── utils/
│   ├── smart_comparator.py    # Умное сравнение
│   ├── openrouter_analyzer.py # OpenRouter AI
│   ├── gemini_analyzer.py     # Gemini AI (fallback)
│   ├── zenrows_client.py      # ZenRows клиент
│   └── docs_finder.py         # Поиск документации
├── tests/                     # Тесты
├── archive_v1/                # Архив старой версии
└── crontab_v2.example         # Пример cron
```

## Автоматизация

### Linux/Mac (cron)

```bash
# Копируем пример
cp crontab_v2.example /tmp/api-watcher-cron

# Редактируем пути
nano /tmp/api-watcher-cron

# Устанавливаем
crontab /tmp/api-watcher-cron
```

### Windows (Task Scheduler)

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "-m api_watcher.watcher_v2" -WorkingDirectory "C:\path\to\api-watcher"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 10:00
Register-ScheduledTask -TaskName "APIWatcherV2" -Action $action -Trigger $trigger
```

## Документация

- [Полное руководство](../WATCHER_V2_GUIDE.md)
- [Быстрый старт](../QUICKSTART_V2.md)
- [Архитектура](../ARCHITECTURE_V2.md)
- [OpenRouter и Webhook](../OPENROUTER_WEBHOOK_GUIDE.md)
- [Миграция с V1](../MIGRATION_V1_TO_V2.md)

## Архив V1

Старая версия перемещена в `archive_v1/`. См. [README архива](archive_v1/README.md).

## Лицензия

MIT License
