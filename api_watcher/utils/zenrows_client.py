"""
ZenRows client for fetching web content
Обходит защиту и получает чистый HTML
"""

import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class ZenRowsClient:
    """Клиент для работы с ZenRows API"""
    
    BASE_URL = "https://api.zenrows.com/v1/"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def fetch_html(
        self,
        url: str,
        js_render: bool = True,
        premium_proxy: bool = False,
        antibot: bool = True
    ) -> Optional[str]:
        """
        Получает HTML контент через ZenRows
        
        Args:
            url: URL для получения
            js_render: Рендерить JavaScript
            premium_proxy: Использовать премиум прокси
            antibot: Обход антибот защиты
        
        Returns:
            HTML контент или None при ошибке
        """
        params = {
            'apikey': self.api_key,
            'url': url,
        }
        
        if js_render:
            params['js_render'] = 'true'
        
        if premium_proxy:
            params['premium_proxy'] = 'true'
        
        if antibot:
            params['antibot'] = 'true'
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=60)
            response.raise_for_status()
            
            logger.info(f"✅ ZenRows: успешно получен контент для {url}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ ZenRows ошибка для {url}: {e}")
            return None
    
    def fetch_with_fallback(self, url: str) -> Optional[str]:
        """
        Получает контент с fallback стратегией:
        1. Попытка с базовыми настройками
        2. Попытка с премиум прокси
        3. Попытка без JS рендеринга
        """
        # Попытка 1: базовые настройки
        html = self.fetch_html(url, js_render=True, premium_proxy=False)
        if html:
            return html
        
        logger.warning(f"⚠️ ZenRows: первая попытка не удалась, пробуем с премиум прокси")
        
        # Попытка 2: с премиум прокси
        html = self.fetch_html(url, js_render=True, premium_proxy=True)
        if html:
            return html
        
        logger.warning(f"⚠️ ZenRows: вторая попытка не удалась, пробуем без JS")
        
        # Попытка 3: без JS рендеринга
        html = self.fetch_html(url, js_render=False, premium_proxy=False)
        return html
