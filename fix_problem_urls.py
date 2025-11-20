#!/usr/bin/env python3
"""
Исправление проблемных URL в urls.json
Удаляет URL, которые возвращают HTML вместо JSON
"""

import json
import sys

# Список проблемных URL (возвращают HTML вместо JSON)
PROBLEM_URLS = [
    "https://direct.i-dgtl.ru/openapi.json",
]

print("=" * 70)
print("Исправление проблемных URL в urls.json")
print("=" * 70)

# Читаем urls.json
with open('urls.json', 'r', encoding='utf-8') as f:
    urls = json.load(f)

print(f"\nВсего URL до очистки: {len(urls)}")

# Находим проблемные записи
problem_entries = [u for u in urls if u['url'] in PROBLEM_URLS]
print(f"\nНайдено проблемных записей: {len(problem_entries)}")

if problem_entries:
    print("\nПроблемные записи:")
    for entry in problem_entries:
        print(f"  - {entry['name']} ({entry['url']})")
    
    # Спрашиваем подтверждение
    response = input("\nУдалить эти записи? (y/n): ").strip().lower()
    
    if response == 'y':
        # Удаляем проблемные записи
        cleaned_urls = [u for u in urls if u['url'] not in PROBLEM_URLS]
        
        # Сохраняем резервную копию
        with open('urls.json.backup', 'w', encoding='utf-8') as f:
            json.dump(urls, f, indent=2, ensure_ascii=False)
        print("\n✅ Создана резервная копия: urls.json.backup")
        
        # Сохраняем очищенный файл
        with open('urls.json', 'w', encoding='utf-8') as f:
            json.dump(cleaned_urls, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Удалено {len(problem_entries)} записей")
        print(f"✅ Осталось URL: {len(cleaned_urls)}")
        print("\nФайл urls.json обновлен!")
    else:
        print("\n❌ Отменено")
else:
    print("\n✅ Проблемных записей не найдено")
