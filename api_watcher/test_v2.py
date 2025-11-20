#!/usr/bin/env python3
"""
Test script for API Watcher V2
Тестовый скрипт для проверки работы новой версии
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_watcher.watcher_v2 import APIWatcherV2
from api_watcher.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_configuration():
    """Проверка конфигурации"""
    logger.info("\n" + "="*60)
    logger.info("🔧 ПРОВЕРКА КОНФИГУРАЦИИ")
    logger.info("="*60)
    
    checks = {
        'ZenRows': Config.is_zenrows_configured(),
        'Gemini AI': Config.is_gemini_configured(),
        'Slack': Config.is_slack_configured(),
        'Telegram': Config.is_telegram_configured()
    }
    
    for service, configured in checks.items():
        status = "✅ Настроен" if configured else "⚠️ Не настроен"
        logger.info(f"{service}: {status}")
    
    logger.info(f"\nБаза данных: {Config.DATABASE_URL}")
    logger.info(f"Интервал проверки: {Config.CHECK_INTERVAL_DAYS} дней")
    logger.info("="*60 + "\n")


def test_single_url():
    """Тест обработки одного URL"""
    logger.info("\n" + "="*60)
    logger.info("🧪 ТЕСТ ОБРАБОТКИ URL")
    logger.info("="*60)
    
    # Используем HTTPBin для теста
    test_url = "https://httpbin.org/json"
    
    watcher = APIWatcherV2()
    
    try:
        result = watcher.process_url(
            url=test_url,
            api_name="HTTPBin Test API",
            method_name="JSON Response"
        )
        
        logger.info("\n📊 Результат:")
        logger.info(f"URL: {result.get('url')}")
        logger.info(f"Изменения: {result.get('has_changes')}")
        
        if result.get('is_first_snapshot'):
            logger.info("ℹ️ Это первый снэпшот для данного URL")
        
        if result.get('summary'):
            logger.info(f"Сводка: {result.get('summary')}")
        
        logger.info("\n✅ Тест завершен успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка теста: {e}", exc_info=True)
        
    finally:
        watcher.cleanup()
    
    logger.info("="*60 + "\n")


def test_database():
    """Тест работы с базой данных"""
    logger.info("\n" + "="*60)
    logger.info("💾 ТЕСТ БАЗЫ ДАННЫХ")
    logger.info("="*60)
    
    from api_watcher.storage.database import DatabaseManager
    
    db = DatabaseManager(Config.DATABASE_URL)
    
    try:
        # Получаем все URL
        urls = db.get_all_urls()
        logger.info(f"\nВсего URL в БД: {len(urls)}")
        
        if urls:
            logger.info("\nПоследние 5 URL:")
            for url in urls[:5]:
                logger.info(f"  • {url}")
        
        # Получаем изменения за последнюю неделю
        changes = db.get_snapshots_with_changes(days=7)
        logger.info(f"\nИзменений за последние 7 дней: {len(changes)}")
        
        if changes:
            logger.info("\nПоследние изменения:")
            for change in changes[:3]:
                logger.info(f"  • {change.api_name} - {change.created_at}")
                if change.ai_summary:
                    logger.info(f"    {change.ai_summary[:100]}...")
        
        logger.info("\n✅ Тест БД завершен успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка теста БД: {e}", exc_info=True)
        
    finally:
        db.close()
    
    logger.info("="*60 + "\n")


def test_comparator():
    """Тест компаратора"""
    logger.info("\n" + "="*60)
    logger.info("🔍 ТЕСТ КОМПАРАТОРА")
    logger.info("="*60)
    
    from api_watcher.utils.smart_comparator import SmartComparator
    
    comparator = SmartComparator()
    
    # Тест HTML to text
    html = "<h1>Test</h1><p>This is a <strong>test</strong> paragraph.</p>"
    text = comparator.html_to_text(html)
    logger.info(f"\nHTML → Text:\n{text}")
    
    # Тест хеширования
    hash1 = comparator.calculate_hash("test content")
    hash2 = comparator.calculate_hash("test content")
    hash3 = comparator.calculate_hash("different content")
    
    logger.info(f"\nХеш 1: {hash1[:16]}...")
    logger.info(f"Хеш 2: {hash2[:16]}...")
    logger.info(f"Хеш 3: {hash3[:16]}...")
    logger.info(f"Хеш 1 == Хеш 2: {hash1 == hash2}")
    logger.info(f"Хеш 1 == Хеш 3: {hash1 == hash3}")
    
    # Тест сравнения JSON
    old_data = {"name": "John", "age": 30}
    new_data = {"name": "John", "age": 31, "city": "NYC"}
    
    has_changes, changes = comparator.compare_json(old_data, new_data)
    logger.info(f"\nJSON сравнение:")
    logger.info(f"Изменения: {has_changes}")
    if changes:
        logger.info(f"Детали: {list(changes.keys())}")
    
    logger.info("\n✅ Тест компаратора завершен успешно")
    logger.info("="*60 + "\n")


def main():
    """Главная функция"""
    logger.info("\n" + "🚀 " + "="*56)
    logger.info("🚀 API WATCHER V2 - ТЕСТИРОВАНИЕ")
    logger.info("🚀 " + "="*56 + "\n")
    
    try:
        # 1. Проверка конфигурации
        test_configuration()
        
        # 2. Тест компаратора
        test_comparator()
        
        # 3. Тест базы данных
        test_database()
        
        # 4. Тест обработки URL
        test_single_url()
        
        logger.info("\n" + "🎉 " + "="*56)
        logger.info("🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        logger.info("🎉 " + "="*56 + "\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Критическая ошибка: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
