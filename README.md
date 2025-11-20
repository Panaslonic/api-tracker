# 🤖 API Watcher

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Микросервис для мониторинга изменений в API документации с поддержкой HTML, OpenAPI, JSON, Postman и Markdown.

## 🆕 API Watcher V2 - Новая версия!

**Теперь доступна улучшенная версия с AI-анализом и продвинутыми функциями:**

- 🗄️ **База данных** - полная история изменений в SQLite/PostgreSQL
- 🌐 **ZenRows** - обход защиты сайтов (Cloudflare, reCAPTCHA)
- 🤖 **OpenRouter AI** - умный анализ изменений через 100+ моделей (Claude, GPT-4, Llama)
- 💬 **Slack + Webhook** - уведомления в Slack и на любой webhook URL
- 🎯 **Умное сравнение** - структурный анализ OpenAPI + AI только при изменениях
- 🔍 **Автопоиск документации** - автоматический поиск новых ссылок при невалидном ответе

📖 **[Полное руководство по V2](WATCHER_V2_GUIDE.md)**
📖 **[Интеграция поиска документации](DOCS_FINDER_INTEGRATION.md)**
📖 **[OpenRouter и Webhook](OPENROUTER_WEBHOOK_GUIDE.md)**

## ✨ Возможности (V1)

- 🔍 Мониторинг конкретных методов API через CSS селекторы и фильтры
- 📋 Поддержка 5 типов документации: HTML, OpenAPI, JSON, Postman, Markdown
- 💾 Система снимков для отслеживания изменений
- 📢 Уведомления в консоль и Telegram
- 🚀 Готов к продакшену: Docker, cron, CI/CD

## 🚀 Быстрый старт

```bash
git clone https://github.com/yourusername/api-watcher.git
cd api-watcher
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate для Windows
pip install -r api_watcher/requirements.txt
cp api_watcher/.env.example .env
python api_watcher/main.py
```

## ⚙️ Конфигурация

Создайте `urls.json` с источниками для мониторинга:

```json
[
  {
    "url": "https://docs.stripe.com/api/customers#create_customer",
    "type": "html",
    "name": "Stripe - Создание клиента",
    "selector": "#create_customer"
  }
]
```

Для Telegram уведомлений добавьте в `.env`:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 📊 Типы документации

| Тип | Параметры |
|-----|-----------|
| `html` | `selector` - CSS селектор |
| `openapi` | `method_filter` - фильтр путей |
| `json` | - |
| `postman` | - |
| `md` | - |

## 📖 Документация

- [Полная документация](api_watcher/README.md)
- [Руководство по установке](SETUP.md)
- [Обработка ошибок](QUICK_ERROR_GUIDE.md)

## 📝 Лицензия

MIT License - см. [LICENSE](LICENSE)