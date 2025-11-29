# API Watcher

Мониторинг изменений в API документации с AI-анализом.

## Возможности

- Мониторинг HTML, OpenAPI, JSON, Postman, Markdown
- AI-анализ изменений через OpenRouter (Claude, GPT-4)
- Уведомления в Slack, Telegram, Webhook
- PostgreSQL для хранения истории
- ZenRows для обхода защиты сайтов

## Деплой через Docker

### 1. Клонирование

```bash
git clone https://github.com/yourusername/api-watcher.git
cd api-watcher
```

### 2. Настройка

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```bash
# БД (можно оставить по умолчанию)
POSTGRES_USER=api_watcher
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=api_watcher

# AI анализ (опционально)
OPENROUTER_API_KEY=sk-or-v1-xxx

# Уведомления (опционально)
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_CHANNEL=#api-changes
WEBHOOK_URL=https://your-webhook.com
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx

# Обход защиты (опционально)
ZENROWS_API_KEY=xxx
```

### 3. Настройка URLs

Создайте `urls.json`:

```json
[
  {
    "url": "https://docs.stripe.com/api/customers",
    "api_name": "Stripe API",
    "method_name": "Customers"
  }
]
```

### 4. Запуск

```bash
docker-compose up -d
```

### 5. Проверка

```bash
docker-compose logs -f watcher
docker-compose ps
```

### 6. Остановка

```bash
docker-compose down
```

Для удаления данных:
```bash
docker-compose down -v
```

## Запуск по расписанию

Добавьте в crontab:

```bash
# Каждые 30 минут
*/30 * * * * cd /path/to/api-watcher && docker-compose run --rm watcher
```

Или используйте systemd timer.

## Локальная разработка

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r api_watcher/requirements.txt
cp .env.example .env
python -m api_watcher.watcher
```

## Структура

```
api_watcher/
├── config.py          # Конфигурация
├── watcher.py         # Главный модуль
├── parsers/           # Парсеры документации
├── notifier/          # Уведомления
├── storage/           # БД
├── services/          # Бизнес-логика
└── utils/             # Утилиты
```

## Лицензия

MIT
