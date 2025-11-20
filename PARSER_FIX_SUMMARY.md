# Исправления парсеров и добавление Webhook уведомлений

## Проблема
Приложение падало с ошибкой `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` когда сервер возвращал:
- Пустой ответ
- HTML вместо JSON/YAML
- Некорректные данные

## Решение

### 1. Улучшена обработка ошибок в парсерах

Добавлены проверки в файлы:
- `api_watcher/parsers/openapi_parser.py`
- `api_watcher/parsers/json_parser.py`
- `api_watcher/parsers/postman_parser.py`

**Что добавлено:**
- Проверка на пустой ответ
- Проверка Content-Type на HTML
- Проверка начала ответа на HTML теги
- Информативные сообщения об ошибках с превью ответа (первые 200 символов)

**Пример новой ошибки:**
```
❌ Сервер вернул HTML вместо JSON для https://example.com/api.json. Content-Type: text/html
```

Вместо непонятной:
```
❌ JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

### 2. Добавлена поддержка Webhook уведомлений

**Изменения в `api_watcher/main.py`:**
- Добавлен импорт `WebhookNotifier`
- Инициализация webhook notifier при наличии `WEBHOOK_URL` в .env
- Отправка уведомлений при обнаружении изменений

**Конфигурация:**
Добавьте в `.env`:
```bash
WEBHOOK_URL=https://your-webhook-url.com/api/notifications
```

**Формат webhook payload:**
```json
{
  "event": "api_change_detected",
  "timestamp": "2025-11-20T11:13:58.325Z",
  "data": {
    "api_name": "API Name",
    "method_name": "Method Name",
    "url": "https://api.example.com/docs",
    "summary": "Обнаружены изменения в API Name",
    "severity": "moderate",
    "key_changes": []
  }
}
```

## Проблемные URL

URL `https://direct.i-dgtl.ru/openapi.json` возвращает HTML вместо JSON.
Возможные причины:
- Требуется авторизация
- Неправильный URL
- Блокировка запросов

**Рекомендация:** Проверьте правильность URL или добавьте заголовки авторизации.

## Тестирование

Запустите тест:
```bash
python test_parser_fix.py
```

Ожидаемый результат:
```
❌ Ошибка (ожидаемая): Сервер вернул HTML вместо JSON/YAML для https://direct.i-dgtl.ru/openapi.json. Content-Type: text/html

Теперь ошибка информативная и понятная!
```


## Тестирование

### 1. Тест парсера
```bash
python test_parser_fix.py
```

Ожидаемый результат:
```
❌ Ошибка (ожидаемая): Сервер вернул HTML вместо JSON/YAML для https://direct.i-dgtl.ru/openapi.json. Content-Type: text/html

Теперь ошибка информативная и понятная!
```

### 2. Тест webhook
```bash
# Установите WEBHOOK_URL в .env
python test_webhook_integration.py
```

### 3. Анализ проблемных URL
```bash
python analyze_failed_urls.py
```

Показывает статистику по URL и находит дубликаты.

### 4. Очистка проблемных URL
```bash
python fix_problem_urls.py
```

Удаляет URL, которые возвращают HTML вместо JSON.

## Важно

После исправлений нужно очистить кэш Python:
```bash
# PowerShell
Get-ChildItem -Path "api_watcher" -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
```

Или просто перезапустите приложение.

## Статистика

Из анализа urls.json:
- Всего URL: 541
- Уникальных URL: 378
- Дублирующихся URL: 90
- Проблемных URL (возвращают HTML): 3

Основные проблемы:
1. URL `https://direct.i-dgtl.ru/openapi.json` возвращает HTML вместо JSON
2. Много дублирующихся URL с одинаковым адресом
3. 51 из 541 URL обрабатываются с ошибками

Рекомендации:
- Удалите проблемные URL с помощью `fix_problem_urls.py`
- Проверьте дублирующиеся URL - возможно, они используют разные method_filter
- Убедитесь, что WEBHOOK_URL настроен в .env для получения уведомлений
