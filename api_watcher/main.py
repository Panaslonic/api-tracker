#!/usr/bin/env python3
"""
API Watcher - микросервис для мониторинга изменений в API документации
Точка входа приложения
"""

import json
import os
from typing import List, Dict, Any

from config import Config
from parsers.html_parser import HTMLParser
from parsers.openapi_parser import OpenAPIParser
from parsers.json_parser import JSONParser
from parsers.postman_parser import PostmanParser
from parsers.md_parser import MarkdownParser
from storage.snapshot_manager import SnapshotManager
from notifier.console_notifier import ConsoleNotifier
from notifier.telegram_notifier import TelegramNotifier
from utils.comparator import Comparator


class APIWatcher:
    def __init__(self):
        self.parsers = {
            'html': HTMLParser(),
            'openapi': OpenAPIParser(),
            'json': JSONParser(),
            'postman': PostmanParser(),
            'md': MarkdownParser()
        }
        self.snapshot_manager = SnapshotManager(Config.SNAPSHOTS_DIR)
        self.notifier = ConsoleNotifier()
        self.comparator = Comparator()
        
        # Инициализируем Telegram уведомления, если настроены
        if Config.is_telegram_configured():
            self.telegram_notifier = TelegramNotifier(
                Config.TELEGRAM_BOT_TOKEN, 
                Config.TELEGRAM_CHAT_ID
            )
            print("📱 Telegram уведомления включены")
        else:
            self.telegram_notifier = None

    def load_urls(self) -> List[Dict[str, str]]:
        """Загружает список URL из urls.json"""
        try:
            with open(Config.URLS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл {Config.URLS_FILE} не найден!")
            return []
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга {Config.URLS_FILE}: {e}")
            return []

    def process_url(self, url_config: Dict[str, str]) -> None:
        """Обрабатывает один URL"""
        url = url_config['url']
        doc_type = url_config['type']
        name = url_config.get('name', url)
        description = url_config.get('description', '')
        
        print(f"Обрабатываем: {name}")
        print(f"  URL: {url}")
        if description:
            print(f"  Описание: {description}")
        
        if doc_type not in self.parsers:
            print(f"Неподдерживаемый тип документации: {doc_type}")
            return
        
        try:
            # Парсим данные с дополнительными параметрами
            parser = self.parsers[doc_type]
            
            # Передаем дополнительные параметры в зависимости от типа парсера
            if doc_type == 'html':
                selector = url_config.get('selector')
                current_data = parser.parse(url, selector=selector)
            elif doc_type == 'openapi':
                method_filter = url_config.get('method_filter')
                current_data = parser.parse(url, method_filter=method_filter)
            else:
                current_data = parser.parse(url)
            
            # Получаем предыдущий snapshot
            previous_data = self.snapshot_manager.load_snapshot(url)
            
            # Сравниваем данные
            if previous_data is not None:
                diff = self.comparator.compare(previous_data, current_data)
                if diff:
                    self.notifier.notify_changes(url, diff)
                    
                    # Отправляем Telegram уведомление, если настроено
                    if self.telegram_notifier:
                        self.telegram_notifier.notify_changes(url, diff)
                    
                    self.snapshot_manager.save_snapshot(url, current_data)
                    print(f"✅ Обнаружены изменения в {url}")
                else:
                    print(f"📄 Изменений не обнаружено в {url}")
            else:
                # Первый запуск - сохраняем snapshot
                self.snapshot_manager.save_snapshot(url, current_data)
                print(f"💾 Создан первый snapshot для {url}")
                
        except Exception as e:
            print(f"❌ Ошибка при обработке {url}: {e}")

    def run(self) -> None:
        """Основной цикл выполнения"""
        print("🚀 Запуск API Watcher...")
        
        urls = self.load_urls()
        if not urls:
            print("Нет URL для обработки")
            return
        
        for url_config in urls:
            self.process_url(url_config)
        
        print("✨ Обработка завершена")


if __name__ == "__main__":
    watcher = APIWatcher()
    watcher.run()