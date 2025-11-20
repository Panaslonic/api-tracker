#!/usr/bin/env python3
"""
Weekly check script for API Watcher V2
Скрипт для еженедельной проверки изменений
Запускайте через cron или планировщик задач
"""

import sys
import os

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_watcher.watcher_v2 import APIWatcherV2
from api_watcher.config import Config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_watcher_weekly.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Главная функция еженедельной проверки"""
    logger.info("🚀 Запуск еженедельной проверки API Watcher V2")
    
    watcher = APIWatcherV2()
    
    try:
        # Обрабатываем все URLs
        results = watcher.process_urls_file(Config.URLS_FILE)
        
        # Статистика
        total = len(results)
        changed = sum(1 for r in results if r.get('has_changes'))
        errors = sum(1 for r in results if 'error' in r)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 ИТОГИ ЕЖЕНЕДЕЛЬНОЙ ПРОВЕРКИ")
        logger.info(f"{'='*60}")
        logger.info(f"Всего проверено: {total}")
        logger.info(f"Обнаружено изменений: {changed}")
        logger.info(f"Ошибок: {errors}")
        logger.info(f"{'='*60}\n")
        
        # Отправляем еженедельную сводку
        if changed > 0:
            logger.info("📧 Отправка еженедельной сводки в Slack...")
            watcher.send_weekly_digest()
        
        logger.info("✅ Еженедельная проверка завершена успешно")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении еженедельной проверки: {e}", exc_info=True)
        return 1
        
    finally:
        watcher.cleanup()


if __name__ == '__main__':
    sys.exit(main())
