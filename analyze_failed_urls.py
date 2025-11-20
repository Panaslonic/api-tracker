#!/usr/bin/env python3
"""
Анализ проблемных URL из urls.json
"""

import json
import sys
from collections import Counter

sys.path.insert(0, 'api_watcher')

# Читаем urls.json
with open('urls.json', 'r', encoding='utf-8') as f:
    urls = json.load(f)

print("=" * 70)
print("Анализ URL в urls.json")
print("=" * 70)

# Статистика по типам
types_count = Counter(url['type'] for url in urls)
print(f"\nВсего URL: {len(urls)}")
print("\nРаспределение по типам:")
for doc_type, count in types_count.most_common():
    print(f"  {doc_type}: {count}")

# Анализ уникальных URL
unique_urls = {}
for url_config in urls:
    url = url_config['url']
    if url in unique_urls:
        unique_urls[url].append(url_config['name'])
    else:
        unique_urls[url] = [url_config['name']]

duplicates = {url: names for url, names in unique_urls.items() if len(names) > 1}

print(f"\nУникальных URL: {len(unique_urls)}")
print(f"Дублирующихся URL: {len(duplicates)}")

if duplicates:
    print("\nТоп-10 дублирующихся URL:")
    sorted_dupes = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for url, names in sorted_dupes:
        print(f"\n  URL: {url}")
        print(f"  Используется {len(names)} раз:")
        for name in names[:5]:  # Показываем первые 5
            print(f"    - {name}")
        if len(names) > 5:
            print(f"    ... и еще {len(names) - 5}")

# Проверяем проблемный URL
problem_url = "https://direct.i-dgtl.ru/openapi.json"
problem_configs = [u for u in urls if u['url'] == problem_url]
if problem_configs:
    print(f"\n{'=' * 70}")
    print(f"Проблемный URL: {problem_url}")
    print(f"Используется {len(problem_configs)} раз:")
    for config in problem_configs:
        print(f"  - {config['name']}")
    print("\n⚠️  Этот URL возвращает HTML вместо JSON!")
    print("   Рекомендация: проверьте правильность URL или удалите эти записи")
