# 🚀 API Watcher V2 - Быстрый старт

## За 5 минут до первого запуска

### 1. Установка (1 минута)

```bash
cd api_watcher
pip install -r requirements.txt
```

### 2. Настройка (2 минуты)

Скопируйте и отредактируйте `.env`:

```bash
cp .env.example .env
nano .env  # или любой редактор
```

**Минимальная конфигурация (работает без внешних сервисов):**

```env
DATABASE_URL=sqlite:///api_watcher.db
```

**Рекомендуемая конфигурация (с AI и уведомлениями):**

```env
DATABASE_URL=sqlite:///api_watcher.db
GEMINI_API_KEY=your_key_here
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=#api-changes
```

### 3. Тестирование (1 минута)

```bash
python test_v2.py
```

### 4. Первый запуск (1 минута)

```bash
python -m watcher_v2
```

## 🎯 Получение API ключей

### Gemini AI (бесплатно, 2 минуты)

1. Откройте https://makersuite.google.com/app/apikey
2. Нажмите "Create API Key"
3. Скопируйте ключ в `.env`

```env
GEMINI_API_KEY=AIzaSy...
```

### Slack (бесплатно, 5 минут)

1. Откройте https://api.slack.com/apps
2. Нажмите "Create New App" → "From scratch"
3. Название: "API Watcher", выберите workspace
4. В разделе "OAuth & Permissions":
   - Добавьте Bot Token Scopes: `chat:write`, `chat:write.public`
   - Нажмите "Install to Workspace"
   - Скопируйте "Bot User OAuth Token"
5. Добавьте бота в канал: `/invite @API Watcher`

```env
SLACK_BOT_TOKEN=xoxb-123456789...
SLACK_CHANNEL=#api-changes
```

### ZenRows (опционально, для сложных сайтов)

1. Зарегистрируйтесь на https://www.zenrows.com/
2. Скопируйте API ключ из dashboard
3. Бесплатный план: 1000 запросов/месяц

```env
ZENROWS_API_KEY=your_key_here
```

## 📝 Настройка URLs

Создайте или отредактируйте `urls.json`:

```json
[
  {
    "url": "https://docs.stripe.com/api",
    "api_name": "Stripe API",
    "method_name": "Documentation"
  },
  {
    "url": "https://api.github.com/openapi",
    "api_name": "GitHub API",
    "method_name": "OpenAPI Spec"
  }
]
```

## 🔄 Автоматизация

### Linux/Mac (cron)

```bash
# Редактировать crontab
crontab -e

# Добавить строку (каждое воскресенье в 10:00)
0 10 * * 0 cd /path/to/api-watcher && /path/to/venv/bin/python api_watcher/weekly_check.py
```

### Windows (Task Scheduler)

1. Откройте Task Scheduler
2. "Create Basic Task"
3. Название: "API Watcher Weekly"
4. Триггер: Weekly, Sunday, 10:00 AM
5. Действие: Start a program
   - Program: `C:\path\to\python.exe`
   - Arguments: `api_watcher\weekly_check.py`
   - Start in: `C:\path\to\api-watcher`

## 🧪 Команды для тестирования

```bash
# Проверка конфигурации
python test_v2.py

# Разовая проверка всех URLs
python -m watcher_v2

# Еженедельная проверка (с дайджестом)
python weekly_check.py

# Проверка одного URL
python -c "
from api_watcher.watcher_v2 import APIWatcherV2
w = APIWatcherV2()
result = w.process_url('https://httpbin.org/json', 'Test API')
print(result)
w.cleanup()
"
```

## 📊 Просмотр результатов

### Через Python

```python
from api_watcher.storage.database import DatabaseManager

db = DatabaseManager('sqlite:///api_watcher.db')

# Все отслеживаемые URLs
urls = db.get_all_urls()
print(f"Отслеживается URLs: {len(urls)}")

# Изменения за неделю
changes = db.get_snapshots_with_changes(days=7)
for change in changes:
    print(f"{change.api_name}: {change.ai_summary}")

db.close()
```

### Через SQLite CLI

```bash
sqlite3 api_watcher.db

# Показать все URLs
SELECT DISTINCT api_name, url FROM snapshots;

# Показать последние изменения
SELECT api_name, method_name, created_at, ai_summary 
FROM snapshots 
WHERE has_changes = 1 
ORDER BY created_at DESC 
LIMIT 10;

# Выход
.quit
```

## 🔧 Troubleshooting

### Ошибка: "No module named 'google.generativeai'"

```bash
pip install google-generativeai
```

### Ошибка: "No module named 'slack_sdk'"

```bash
pip install slack-sdk
```

### Ошибка: "ZenRows API key not configured"

Это предупреждение, не ошибка. ZenRows опционален. Для использования добавьте ключ в `.env`.

### Slack не отправляет сообщения

1. Проверьте токен: `echo $SLACK_BOT_TOKEN`
2. Убедитесь что бот добавлен в канал: `/invite @YourBot`
3. Проверьте права бота: `chat:write`, `chat:write.public`

### Gemini возвращает ошибку квоты

Бесплатный план: 60 запросов/минуту. Если превышен лимит:
- Добавьте задержку между запросами
- Или используйте без AI (структурное сравнение все равно работает)

## 💡 Советы

### Экономия API запросов

1. **ZenRows**: используйте только для сложных сайтов
2. **Gemini**: AI вызывается только при обнаружении изменений
3. **Slack**: группируйте уведомления в еженедельный дайджест

### Оптимизация производительности

```env
# Проверять реже
CHECK_INTERVAL_DAYS=14

# Использовать PostgreSQL для больших объемов
DATABASE_URL=postgresql://user:pass@localhost/api_watcher
```

### Мониторинг нескольких проектов

Создайте отдельные конфигурации:

```bash
# Проект 1
DATABASE_URL=sqlite:///project1.db python -m watcher_v2

# Проект 2
DATABASE_URL=sqlite:///project2.db python -m watcher_v2
```

## 📚 Дальнейшее чтение

- [Полное руководство](WATCHER_V2_GUIDE.md)
- [Примеры использования](api_watcher/README.md)
- [Документация API](api_watcher/)

## 🆘 Поддержка

Если что-то не работает:

1. Запустите тесты: `python test_v2.py`
2. Проверьте логи: `tail -f api_watcher.log`
3. Включите DEBUG: `API_WATCHER_LOG_LEVEL=DEBUG`

---

**Готово! Теперь у вас работает умный мониторинг API с AI-анализом! 🎉**
