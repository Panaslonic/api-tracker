#!/usr/bin/env python3
"""
Скрипт для проверки доступных якорей на странице Megaplan API
"""

import requests
from bs4 import BeautifulSoup

def check_megaplan_anchors():
    url = 'https://dev.megaplan.ru/apiv3/index.html'
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем все элементы с id
        elements_with_id = soup.find_all(attrs={'id': True})
        
        print(f"Найдено {len(elements_with_id)} якорей на странице:")
        print("-" * 50)
        
        for elem in elements_with_id:
            anchor_id = elem.get('id')
            tag_name = elem.name
            text_content = elem.get_text(strip=True)[:50] + "..." if len(elem.get_text(strip=True)) > 50 else elem.get_text(strip=True)
            
            print(f"#{anchor_id} ({tag_name}) - {text_content}")
            
    except Exception as e:
        print(f"Ошибка при проверке якорей: {e}")

if __name__ == "__main__":
    check_megaplan_anchors()