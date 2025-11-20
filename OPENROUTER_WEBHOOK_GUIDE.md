# OpenRouter и Webhook интеграция

## Обзор изменений

### 1. OpenRouter AI
Используется OpenRouter для AI анализа изменений с поддержкой множества моделей.

### 2. Webhook уведомления
Добавлена отправка уведомлений на webhook URL в дополнение к Slack.

## 🤖 OpenRouter AI

### Преимущества
- ✅ Доступ к множеству моделей (Claude, GPT-4, Llama и др.)
- ✅ Единый API для всех моделей
- ✅ Гибкое ценообразование
- ✅ Простая интеграция

### Настройка

1. **Получите API ключ**
   - Зарегистрируйтесь на https://openrouter.ai/
   - Перейдите в https://openrouter.ai/keys
   - Создайте новый ключ

2. **Добавьте в .env**
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_SITE_URL=https://your-site.com  # опционально
OPENROUTER_APP_NAME=API Watcher
```

3. **Выберите модель**

Рекомендуемые модели:

| Модель | Цена (за 1M токенов) | Качество | Скорость |
|--------|---------------------|----------|----------|
| `anthropic/claude-3.5-sonnet` | $3 / $15 | ⭐⭐⭐⭐⭐ | Быстро |
| `openai/gpt-4-turbo` | $10 / $30 | ⭐⭐⭐⭐⭐ | Средне |
| `google/gemini-pro-1.5` | $0.35 / $1.05 | ⭐⭐⭐⭐ | Быстро |
| `meta-llama/llama-3.1-70b` | $0.35 / $0.40 | ⭐⭐⭐ | Очень быстро |

Полный список: https://openrouter.ai/models

### Пример использования

```python
from api_watcher.utils.openrouter_analyzer import OpenRouterAnalyzer

analyzer = OpenRouterAnalyzer(
    api_key="sk-or-v1-...",
    model="anthropic/claude-3.5-sonnet"
)

# Анализ изменений
result = analyzer.analyze_changes(
    old_text="старая версия",
    new_text="новая версия",
    api_name="Stripe API",
    method_name="Create Customer"
)

print(result)
# {
#     'has_significant_changes': True,
#     'summary': 'Добавлен новый параметр email',
#     'severity': 'moderate',
#     'key_changes': ['Новый параметр: email']
# }
```

### Работа без AI

Если OpenRouter не настроен, система работает без AI анализа:

```
⚠️ OpenRouter не настроен
ℹ️ Система работает без AI анализа
✅ Все изменения считаются значимыми
```

## 🔔 Webhook уведомления

### Формат уведомлений

Все уведомления отправляются в формате JSON:

#### 1. Изменения в API
```json
{
  "event": "api_change_detected",
  "timestamp": "2024-11-20T10:30:00.000Z",
  "data": {
    "api_name": "Stripe API",
    "method_name": "Create Customer",
    "url": "https://stripe.com/docs/api/customers",
    "summary": "Добавлен новый параметр email",
    "severity": "moderate",
    "key_changes": [
      "Новый параметр: email",
      "Изменен тип параметра: phone"
    ]
  }
}
```

#### 2. Обновление URL документации
```json
{
  "event": "documentation_url_updated",
  "timestamp": "2024-11-20T10:30:00.000Z",
  "data": {
    "api_name": "Stripe API",
    "method_name": "Create Customer",
    "old_url": "https://stripe.com/docs/api/old",
    "new_url": "https://stripe.com/openapi.json",
    "doc_type": "openapi"
  }
}
```

#### 3. Еженедельная сводка
```json
{
  "event": "weekly_digest",
  "timestamp": "2024-11-20T10:30:00.000Z",
  "data": {
    "total_changes": 5,
    "changes": [
      {
        "api_name": "Stripe API",
        "method_name": "Create Customer",
        "url": "https://stripe.com/docs/api/customers",
        "summary": "Изменения в параметрах",
        "created_at": "2024-11-19T15:20:00.000Z"
      }
    ]
  }
}
```

### Настройка webhook

1. **Создайте endpoint**

Пример на Node.js/Express:
```javascript
app.post('/api/notifications', (req, res) => {
  const { event, timestamp, data } = req.body;
  
  console.log(`Получено событие: ${event}`);
  console.log('Данные:', data);
  
  // Обработка события
  switch(event) {
    case 'api_change_detected':
      handleAPIChange(data);
      break;
    case 'documentation_url_updated':
      handleURLUpdate(data);
      break;
    case 'weekly_digest':
      handleWeeklyDigest(data);
      break;
  }
  
  res.status(200).json({ success: true });
});
```

Пример на Python/Flask:
```python
@app.route('/api/notifications', methods=['POST'])
def handle_notification():
    data = request.json
    event = data.get('event')
    
    print(f"Получено событие: {event}")
    
    if event == 'api_change_detected':
        handle_api_change(data['data'])
    elif event == 'documentation_url_updated':
        handle_url_update(data['data'])
    elif event == 'weekly_digest':
        handle_weekly_digest(data['data'])
    
    return jsonify({'success': True})
```

2. **Добавьте URL в .env**
```bash
WEBHOOK_URL=https://your-domain.com/api/notifications
```

3. **Тест подключения**
```python
from api_watcher.notifier.webhook_notifier import WebhookNotifier

webhook = WebhookNotifier("https://your-domain.com/api/notifications")
if webhook.test_connection():
    print("✅ Webhook работает!")
else:
    print("❌ Webhook недоступен")
```

### Безопасность webhook

Рекомендации:
1. Используйте HTTPS
2. Добавьте аутентификацию (токен в заголовке)
3. Проверяйте IP адрес отправителя
4. Используйте rate limiting

Пример с токеном:
```python
# В webhook_notifier.py можно добавить
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {your_secret_token}'
}
```

## 🚀 Быстрый старт

### 1. Установка
```bash
cd api_watcher
pip install -r requirements.txt
```

### 2. Настройка .env
```bash
# OpenRouter (рекомендуется)
OPENROUTER_API_KEY=sk-or-v1-your-key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Webhook
WEBHOOK_URL=https://your-webhook.com/api/notifications

# Slack (опционально)
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=#api-changes

# ZenRows (опционально)
ZENROWS_API_KEY=your-key
```

### 3. Запуск
```bash
python -m api_watcher.watcher_v2
```

### 4. Проверка логов
```
✅ ZenRows клиент инициализирован
✅ OpenRouter AI инициализирован (модель: anthropic/claude-3.5-sonnet)
✅ Slack notifier инициализирован
✅ Webhook notifier инициализирован
✅ Webhook: тест подключения успешен (200)
```

## 📊 Сравнение моделей

### По качеству анализа
1. Claude 3.5 Sonnet - лучший для технической документации
2. GPT-4 Turbo - отличное качество, дороже
3. Llama 3.1 70B - хорошее качество, очень дешево
4. Mixtral 8x7B - быстрый и дешевый

### По скорости
1. Llama 3.1 70B - ~1-2 сек
2. Mixtral 8x7B - ~2-3 сек
3. Claude 3.5 Sonnet - ~3-4 сек
4. GPT-4 Turbo - ~4-6 сек

### По цене (за 1000 запросов, ~500 токенов каждый)
1. Llama 3.1 70B - ~$0.20
2. Mixtral 8x7B - ~$0.30
3. Claude 3.5 Sonnet - ~$2.00
4. GPT-4 Turbo - ~$6.00

## 🔧 Продвинутая настройка

### Кастомные модели
```bash
# Используйте любую модель из OpenRouter
OPENROUTER_MODEL=openai/gpt-4-turbo-preview
OPENROUTER_MODEL=meta-llama/llama-3.1-70b
OPENROUTER_MODEL=meta-llama/llama-3.1-405b
OPENROUTER_MODEL=anthropic/claude-3-opus
```

### Множественные webhook
Если нужно отправлять на несколько webhook, можно расширить код:

```python
# В config.py
WEBHOOK_URLS = os.getenv('WEBHOOK_URLS', '').split(',')

# В watcher_v2.py
self.webhooks = []
for url in self.config.WEBHOOK_URLS:
    if url.strip():
        self.webhooks.append(WebhookNotifier(url.strip()))
```

### Фильтрация событий
```python
# Отправлять только major изменения
if severity == 'major':
    webhook.send_change_notification(...)
```

## 📝 Примеры интеграций

### Discord webhook
```bash
WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN
```

### Slack webhook (альтернатива)
```bash
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Microsoft Teams
```bash
WEBHOOK_URL=https://outlook.office.com/webhook/YOUR_WEBHOOK_URL
```

### Telegram bot
Создайте свой endpoint, который пересылает в Telegram:
```python
@app.route('/api/notifications', methods=['POST'])
def forward_to_telegram():
    data = request.json
    
    # Отправка в Telegram
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=format_message(data)
    )
    
    return jsonify({'success': True})
```

## 🐛 Отладка

### Проверка OpenRouter
```python
from api_watcher.utils.openrouter_analyzer import OpenRouterAnalyzer

analyzer = OpenRouterAnalyzer(
    api_key="your-key",
    model="anthropic/claude-3.5-sonnet"
)

result = analyzer.analyze_changes(
    "старый текст",
    "новый текст",
    "Test API"
)

print(result)
```

### Проверка webhook
```bash
curl -X POST https://your-webhook.com/api/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "event": "test_connection",
    "timestamp": "2024-11-20T10:30:00.000Z",
    "data": {"message": "Test"}
  }'
```

### Логи
```bash
# Включить подробное логирование
export LOG_LEVEL=DEBUG
python -m api_watcher.watcher_v2
```

## ❓ FAQ

**Q: Можно ли использовать несколько моделей одновременно?**  
A: Нет, используется одна модель, указанная в OPENROUTER_MODEL.

**Q: Что если webhook недоступен?**  
A: Система продолжит работу, ошибки будут залогированы.

**Q: Сколько стоит OpenRouter?**  
A: Зависит от модели. Claude 3.5 Sonnet: $3 за 1M входных токенов.

**Q: Можно ли отключить Slack и использовать только webhook?**  
A: Да, просто не настраивайте SLACK_BOT_TOKEN.

**Q: Поддерживаются ли другие AI провайдеры?**  
A: Через OpenRouter доступны 100+ моделей от разных провайдеров.

## 📚 Дополнительные ресурсы

- [OpenRouter документация](https://openrouter.ai/docs)
- [Список моделей OpenRouter](https://openrouter.ai/models)
- [Цены OpenRouter](https://openrouter.ai/models)
- [Webhook best practices](https://webhooks.fyi/)
