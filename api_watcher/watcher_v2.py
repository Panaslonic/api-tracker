"""
API Watcher V2 - Enhanced version with DB, ZenRows, Gemini AI and Slack
Улучшенная версия с БД, ZenRows, Gemini AI и Slack интеграцией
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from api_watcher.config import Config
from api_watcher.storage.database import DatabaseManager
from api_watcher.utils.zenrows_client import ZenRowsClient
from api_watcher.utils.gemini_analyzer import GeminiAnalyzer
from api_watcher.utils.openrouter_analyzer import OpenRouterAnalyzer
from api_watcher.utils.smart_comparator import SmartComparator
from api_watcher.utils.docs_finder import find_api_documentation
from api_watcher.notifier.slack_notifier import SlackNotifier
from api_watcher.notifier.webhook_notifier import WebhookNotifier
from api_watcher.parsers.openapi_parser import OpenAPIParser
from api_watcher.parsers.json_parser import JSONParser
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIWatcherV2:
    """Улучшенный мониторинг API с AI-анализом"""
    
    def __init__(self):
        self.config = Config
        self.db = DatabaseManager(self.config.DATABASE_URL)
        self.comparator = SmartComparator()
        
        # Опциональные компоненты
        self.zenrows = None
        if self.config.is_zenrows_configured():
            self.zenrows = ZenRowsClient(self.config.ZENROWS_API_KEY)
            logger.info("✅ ZenRows клиент инициализирован")
        
        # AI Analyzer - приоритет OpenRouter, fallback на Gemini
        self.ai_analyzer = None
        if self.config.is_openrouter_configured():
            self.ai_analyzer = OpenRouterAnalyzer(
                self.config.OPENROUTER_API_KEY,
                self.config.OPENROUTER_MODEL,
                self.config.OPENROUTER_SITE_URL,
                self.config.OPENROUTER_APP_NAME
            )
            logger.info(f"✅ OpenRouter AI инициализирован (модель: {self.config.OPENROUTER_MODEL})")
        elif self.config.is_gemini_configured():
            self.ai_analyzer = GeminiAnalyzer(
                self.config.GEMINI_API_KEY,
                self.config.GEMINI_MODEL
            )
            logger.info("✅ Gemini AI инициализирован (fallback)")
        
        self.slack = None
        if self.config.is_slack_configured():
            self.slack = SlackNotifier(
                self.config.SLACK_BOT_TOKEN,
                self.config.SLACK_CHANNEL
            )
            logger.info("✅ Slack notifier инициализирован")
        
        self.webhook = None
        if self.config.is_webhook_configured():
            self.webhook = WebhookNotifier(self.config.WEBHOOK_URL)
            logger.info("✅ Webhook notifier инициализирован")
            # Тестируем подключение
            if not self.webhook.test_connection():
                logger.warning("⚠️ Webhook недоступен, но будет использоваться")
        
        self.openapi_parser = OpenAPIParser()
        self.json_parser = JSONParser()
    
    def fetch_content(self, url: str) -> Optional[str]:
        """Получает контент URL (через ZenRows если доступен)"""
        if self.zenrows:
            logger.info(f"🌐 Получаем контент через ZenRows: {url}")
            return self.zenrows.fetch_with_fallback(url)
        else:
            logger.info(f"🌐 Получаем контент напрямую: {url}")
            import requests
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"❌ Ошибка получения {url}: {e}")
                return None
    
    def _is_valid_response(self, content: str, url: str) -> bool:
        """
        Проверяет валидность ответа
        
        Args:
            content: Контент ответа
            url: URL запроса
            
        Returns:
            True если ответ валидный, False если нужно искать новую документацию
        """
        if not content:
            return False
        
        # Проверяем на типичные ошибки
        error_indicators = [
            '404',
            'not found',
            'page not found',
            'error',
            'forbidden',
            '403',
            '500',
            'internal server error',
            'service unavailable',
            'bad gateway'
        ]
        
        content_lower = content.lower()
        
        # Если контент слишком короткий (меньше 100 символов) - подозрительно
        if len(content) < 100:
            logger.warning(f"⚠️ Подозрительно короткий ответ ({len(content)} символов)")
            return False
        
        # Проверяем на индикаторы ошибок
        for indicator in error_indicators:
            if indicator in content_lower:
                logger.warning(f"⚠️ Обнаружен индикатор ошибки: {indicator}")
                return False
        
        return True
    
    async def _try_find_new_documentation(
        self,
        url: str,
        api_name: Optional[str],
        method_name: Optional[str]
    ) -> Optional[str]:
        """
        Пытается найти новую документацию для API
        
        Args:
            url: Старый URL
            api_name: Название API
            method_name: Название метода
            
        Returns:
            Новый URL документации или None
        """
        logger.info(f"🔍 Пытаемся найти новую документацию для {api_name or url}")
        
        try:
            docs_info = await find_api_documentation(
                url=url,
                api_name=api_name,
                method_name=method_name,
                serpapi_key=self.config.SERPAPI_KEY
            )
            
            if docs_info and docs_info.get('url'):
                new_url = docs_info['url']
                doc_type = docs_info.get('type', 'unknown')
                
                logger.info(f"✅ Найдена новая документация ({doc_type}): {new_url}")
                
                # Отправляем уведомления
                if self.slack:
                    message = f"🔄 *Обновлена ссылка на документацию*\n\n"
                    message += f"*API:* {api_name or 'Unknown'}\n"
                    if method_name:
                        message += f"*Метод:* {method_name}\n"
                    message += f"*Старый URL:* {url}\n"
                    message += f"*Новый URL:* {new_url}\n"
                    message += f"*Тип:* {doc_type}\n"
                    
                    if docs_info.get('title'):
                        message += f"*Заголовок:* {docs_info['title']}\n"
                    
                    self.slack.send_message(message)
                
                if self.webhook:
                    self.webhook.send_documentation_update(
                        api_name=api_name or 'Unknown',
                        method_name=method_name,
                        old_url=url,
                        new_url=new_url,
                        doc_type=doc_type
                    )
                
                return new_url
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска новой документации: {e}")
        
        return None
    
    def detect_content_type(self, url: str, content: str) -> str:
        """Определяет тип контента"""
        if 'openapi' in url.lower() or 'swagger' in url.lower():
            return 'openapi'
        
        try:
            data = json.loads(content)
            if 'openapi' in data or 'swagger' in data:
                return 'openapi'
            return 'json'
        except:
            return 'html'
    
    def process_url(
        self,
        url: str,
        api_name: Optional[str] = None,
        method_name: Optional[str] = None
    ) -> Dict:
        """
        Обрабатывает один URL: получает контент, сравнивает, анализирует
        
        Returns:
            {
                'url': str,
                'has_changes': bool,
                'summary': str,
                'severity': str
            }
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 Обработка: {api_name or url}")
        logger.info(f"{'='*60}")
        
        # 1. Получаем новый контент
        new_html = self.fetch_content(url)
        if not new_html:
            logger.error(f"❌ Не удалось получить контент для {url}")
            return {'url': url, 'has_changes': False, 'error': 'Failed to fetch'}
        
        # 1.5. Проверяем валидность ответа
        if not self._is_valid_response(new_html, url):
            logger.warning(f"⚠️ Невалидный ответ от {url}, пытаемся найти новую документацию")
            
            # Пытаемся найти новую документацию
            new_url = asyncio.run(self._try_find_new_documentation(url, api_name, method_name))
            
            if new_url:
                # Пробуем получить контент с нового URL
                new_html_from_new_url = self.fetch_content(new_url)
                
                if new_html_from_new_url and self._is_valid_response(new_html_from_new_url, new_url):
                    logger.info(f"✅ Успешно получен контент с нового URL: {new_url}")
                    # Обновляем URL для дальнейшей обработки
                    url = new_url
                    new_html = new_html_from_new_url
                else:
                    logger.error(f"❌ Новый URL также вернул невалидный ответ")
                    return {'url': url, 'has_changes': False, 'error': 'Invalid response, new URL also failed'}
            else:
                logger.error(f"❌ Не удалось найти новую документацию")
                return {'url': url, 'has_changes': False, 'error': 'Invalid response, no alternative found'}
        
        # 2. Определяем тип контента
        content_type = self.detect_content_type(url, new_html)
        logger.info(f"📄 Тип контента: {content_type}")
        
        # 3. Получаем предыдущий снэпшот
        old_snapshot = self.db.get_latest_snapshot(url)
        
        if not old_snapshot:
            logger.info(f"📝 Первый снэпшот для {url}")
            # Сохраняем первый снэпшот
            text_content = self.comparator.html_to_text(new_html) if content_type == 'html' else new_html
            content_hash = self.comparator.calculate_hash(new_html)
            
            self.db.save_snapshot(
                url=url,
                raw_html=new_html,
                text_content=text_content,
                api_name=api_name,
                method_name=method_name,
                content_type=content_type,
                content_hash=content_hash,
                has_changes=False
            )
            
            return {
                'url': url,
                'has_changes': False,
                'is_first_snapshot': True
            }
        
        # 4. Сравниваем контент
        result = self._compare_content(
            old_snapshot,
            new_html,
            content_type,
            url,
            api_name,
            method_name
        )
        
        return result
    
    def _compare_content(
        self,
        old_snapshot,
        new_html: str,
        content_type: str,
        url: str,
        api_name: Optional[str],
        method_name: Optional[str]
    ) -> Dict:
        """Сравнивает контент в зависимости от типа"""
        
        if content_type == 'openapi':
            return self._compare_openapi(
                old_snapshot, new_html, url, api_name, method_name
            )
        elif content_type == 'json':
            return self._compare_json(
                old_snapshot, new_html, url, api_name, method_name
            )
        else:  # html
            return self._compare_html(
                old_snapshot, new_html, url, api_name, method_name
            )
    
    def _compare_openapi(
        self,
        old_snapshot,
        new_html: str,
        url: str,
        api_name: Optional[str],
        method_name: Optional[str]
    ) -> Dict:
        """Сравнение OpenAPI спецификаций"""
        logger.info("🔍 Сравнение OpenAPI спецификации...")
        
        try:
            # Парсим спецификации
            old_spec = json.loads(old_snapshot.structured_data) if old_snapshot.structured_data else json.loads(old_snapshot.raw_html)
            new_spec = json.loads(new_html)
            
            # Структурное сравнение
            has_changes, changes_dict = self.comparator.compare_openapi(old_spec, new_spec)
            
            if not has_changes:
                logger.info("✅ Изменений в OpenAPI не обнаружено")
                return {'url': url, 'has_changes': False}
            
            logger.info("🔍 Обнаружены изменения в OpenAPI")
            
            # Определяем severity на основе категорий (без AI)
            categories = self.comparator.categorize_openapi_changes(changes_dict)
            if categories['breaking_changes']:
                severity = 'major'
            elif categories['new_endpoints'] or categories['removed_endpoints']:
                severity = 'moderate'
            else:
                severity = 'minor'
            
            # AI анализ изменений - ТОЛЬКО если есть значимые изменения
            ai_summary = "Обнаружены изменения в OpenAPI спецификации"
            
            if self.ai_analyzer and changes_dict and (severity in ['moderate', 'major']):
                logger.info(f"🤖 Запускаем AI анализ (severity: {severity})...")
                ai_summary = self.ai_analyzer.analyze_openapi_changes(changes_dict, api_name)
            else:
                if severity == 'minor':
                    logger.info("ℹ️ Незначительные изменения, пропускаем AI анализ")
                    # Простое описание для minor изменений
                    change_count = len(changes_dict.get('modified', []))
                    ai_summary = f"Незначительные изменения в OpenAPI спецификации ({change_count} элементов)"
                

            
            # Сохраняем новый снэпшот
            content_hash = self.comparator.calculate_hash(new_html)
            self.db.save_snapshot(
                url=url,
                raw_html=new_html,
                text_content=json.dumps(new_spec, indent=2),
                api_name=api_name,
                method_name=method_name,
                content_type='openapi',
                structured_data=new_spec,
                content_hash=content_hash,
                has_changes=True,
                ai_summary=ai_summary
            )
            
            # Отправляем уведомления
            if self.slack:
                self.slack.send_change_notification(
                    api_name=api_name or 'Unknown API',
                    method_name=method_name,
                    url=url,
                    summary=ai_summary,
                    severity=severity
                )
            
            if self.webhook:
                self.webhook.send_change_notification(
                    api_name=api_name or 'Unknown API',
                    method_name=method_name,
                    url=url,
                    summary=ai_summary,
                    severity=severity
                )
            
            return {
                'url': url,
                'has_changes': True,
                'summary': ai_summary,
                'severity': severity,
                'changes': changes_dict
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка сравнения OpenAPI: {e}")
            return {'url': url, 'has_changes': False, 'error': str(e)}
    
    def _compare_json(
        self,
        old_snapshot,
        new_html: str,
        url: str,
        api_name: Optional[str],
        method_name: Optional[str]
    ) -> Dict:
        """Сравнение JSON данных"""
        logger.info("🔍 Сравнение JSON данных...")
        
        try:
            old_data = json.loads(old_snapshot.structured_data) if old_snapshot.structured_data else json.loads(old_snapshot.raw_html)
            new_data = json.loads(new_html)
            
            has_changes, changes_dict = self.comparator.compare_json(old_data, new_data)
            
            if not has_changes:
                logger.info("✅ Изменений в JSON не обнаружено")
                return {'url': url, 'has_changes': False}
            
            logger.info("🔍 Обнаружены изменения в JSON")
            
            # Сохраняем новый снэпшот
            content_hash = self.comparator.calculate_hash(new_html)
            summary = f"Обнаружены изменения в JSON структуре: {len(changes_dict)} изменений"
            
            self.db.save_snapshot(
                url=url,
                raw_html=new_html,
                text_content=json.dumps(new_data, indent=2),
                api_name=api_name,
                method_name=method_name,
                content_type='json',
                structured_data=new_data,
                content_hash=content_hash,
                has_changes=True,
                ai_summary=summary
            )
            
            return {
                'url': url,
                'has_changes': True,
                'summary': summary,
                'severity': 'moderate'
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка сравнения JSON: {e}")
            return {'url': url, 'has_changes': False, 'error': str(e)}
    
    def _compare_html(
        self,
        old_snapshot,
        new_html: str,
        url: str,
        api_name: Optional[str],
        method_name: Optional[str]
    ) -> Dict:
        """Сравнение HTML контента с AI анализом"""
        logger.info("🔍 Сравнение HTML контента...")
        
        # Быстрая проверка по хешу
        new_hash = self.comparator.calculate_hash(new_html)
        if old_snapshot.content_hash == new_hash:
            logger.info("✅ Контент не изменился (по хешу)")
            return {'url': url, 'has_changes': False}
        
        # Конвертируем в текст
        has_changes, old_text, new_text = self.comparator.compare_html_text(
            old_snapshot.raw_html,
            new_html
        )
        
        if not has_changes:
            logger.info("✅ Изменений в тексте не обнаружено")
            return {'url': url, 'has_changes': False}
        
        logger.info("🔍 Обнаружены изменения в HTML")
        
        # AI анализ изменений - ТОЛЬКО если настроен AI analyzer
        ai_result = {'has_significant_changes': True, 'summary': 'Обнаружены изменения', 'severity': 'moderate'}
        
        if self.ai_analyzer:
            logger.info("🤖 Запускаем AI анализ для определения значимости...")
            ai_result = self.ai_analyzer.analyze_changes(
                old_text,
                new_text,
                api_name,
                method_name
            )
        else:
            logger.info("ℹ️ AI analyzer не настроен, считаем изменения значимыми")
        
        if not ai_result.get('has_significant_changes'):
            logger.info("ℹ️ AI определил изменения как незначительные")
            # Все равно сохраняем снэпшот, но не отправляем уведомление
            self.db.save_snapshot(
                url=url,
                raw_html=new_html,
                text_content=new_text,
                api_name=api_name,
                method_name=method_name,
                content_type='html',
                content_hash=new_hash,
                has_changes=False,
                ai_summary="Незначительные изменения"
            )
            return {'url': url, 'has_changes': False, 'reason': 'insignificant'}
        
        # Сохраняем снэпшот с изменениями
        summary = ai_result.get('summary', 'Обнаружены существенные изменения')
        severity = ai_result.get('severity', 'moderate')
        
        self.db.save_snapshot(
            url=url,
            raw_html=new_html,
            text_content=new_text,
            api_name=api_name,
            method_name=method_name,
            content_type='html',
            content_hash=new_hash,
            has_changes=True,
            ai_summary=summary
        )
        
        # Отправляем уведомления
        if self.slack:
            self.slack.send_change_notification(
                api_name=api_name or 'Unknown API',
                method_name=method_name,
                url=url,
                summary=summary,
                severity=severity,
                key_changes=ai_result.get('key_changes', [])
            )
        
        if self.webhook:
            self.webhook.send_change_notification(
                api_name=api_name or 'Unknown API',
                method_name=method_name,
                url=url,
                summary=summary,
                severity=severity,
                key_changes=ai_result.get('key_changes', [])
            )
        
        return {
            'url': url,
            'has_changes': True,
            'summary': summary,
            'severity': severity,
            'key_changes': ai_result.get('key_changes', [])
        }
    
    def process_urls_file(self, urls_file: str) -> List[Dict]:
        """Обрабатывает файл с URL-ами"""
        logger.info(f"📂 Загружаем URLs из {urls_file}")
        
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls_data = json.load(f)
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла {urls_file}: {e}")
            return []
        
        results = []
        
        for item in urls_data:
            url = item.get('url')
            api_name = item.get('api_name')
            method_name = item.get('method_name')
            
            if not url:
                continue
            
            result = self.process_url(url, api_name, method_name)
            results.append(result)
        
        return results
    
    def send_weekly_digest(self):
        """Отправляет еженедельную сводку изменений"""
        if not self.slack:
            logger.warning("⚠️ Slack не настроен, пропускаем еженедельную сводку")
            return
        
        logger.info("📊 Формируем еженедельную сводку...")
        
        snapshots = self.db.get_snapshots_with_changes(days=self.config.CHECK_INTERVAL_DAYS)
        
        changes = []
        for snapshot in snapshots:
            changes.append({
                'api_name': snapshot.api_name,
                'method_name': snapshot.method_name,
                'url': snapshot.url,
                'summary': snapshot.ai_summary or 'Обнаружены изменения',
                'created_at': snapshot.created_at
            })
        
        self.slack.send_weekly_digest(changes)
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.db.close()


def main():
    """Главная функция"""
    watcher = APIWatcherV2()
    
    try:
        # Обрабатываем URLs
        results = watcher.process_urls_file(Config.URLS_FILE)
        
        # Статистика
        total = len(results)
        changed = sum(1 for r in results if r.get('has_changes'))
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 СТАТИСТИКА")
        logger.info(f"{'='*60}")
        logger.info(f"Всего проверено: {total}")
        logger.info(f"Обнаружено изменений: {changed}")
        logger.info(f"{'='*60}\n")
        
    finally:
        watcher.cleanup()


if __name__ == '__main__':
    main()
