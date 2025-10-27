"""
Console Notifier - уведомления в консоль
Выводит информацию об изменениях в читаемом формате
"""

from typing import Dict, Any
from datetime import datetime


class ConsoleNotifier:
    def __init__(self):
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }

    def notify_changes(self, url: str, diff: Dict[str, Any]) -> None:
        """Отправляет уведомление об изменениях в консоль"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{self.colors['bold']}{self.colors['yellow']}🔔 ОБНАРУЖЕНЫ ИЗМЕНЕНИЯ{self.colors['end']}")
        print(f"{self.colors['cyan']}URL:{self.colors['end']} {url}")
        print(f"{self.colors['cyan']}Время:{self.colors['end']} {timestamp}")
        print(f"{self.colors['cyan']}{'='*60}{self.colors['end']}")
        
        self._print_diff_details(diff)
        
        print(f"{self.colors['cyan']}{'='*60}{self.colors['end']}\n")

    def _print_diff_details(self, diff: Dict[str, Any]) -> None:
        """Выводит детали изменений"""
        if 'dictionary_item_added' in diff:
            print(f"{self.colors['green']}➕ ДОБАВЛЕНО:{self.colors['end']}")
            for item in diff['dictionary_item_added']:
                print(f"  + {item}")
        
        if 'dictionary_item_removed' in diff:
            print(f"{self.colors['red']}➖ УДАЛЕНО:{self.colors['end']}")
            for item in diff['dictionary_item_removed']:
                print(f"  - {item}")
        
        if 'values_changed' in diff:
            print(f"{self.colors['yellow']}🔄 ИЗМЕНЕНО:{self.colors['end']}")
            for path, change in diff['values_changed'].items():
                old_value = str(change.get('old_value', ''))[:100]
                new_value = str(change.get('new_value', ''))[:100]
                print(f"  📍 {path}")
                print(f"    {self.colors['red']}Было:{self.colors['end']} {old_value}")
                print(f"    {self.colors['green']}Стало:{self.colors['end']} {new_value}")
        
        if 'iterable_item_added' in diff:
            print(f"{self.colors['green']}➕ ДОБАВЛЕНЫ ЭЛЕМЕНТЫ:{self.colors['end']}")
            for path, items in diff['iterable_item_added'].items():
                print(f"  📍 {path}: {items}")
        
        if 'iterable_item_removed' in diff:
            print(f"{self.colors['red']}➖ УДАЛЕНЫ ЭЛЕМЕНТЫ:{self.colors['end']}")
            for path, items in diff['iterable_item_removed'].items():
                print(f"  📍 {path}: {items}")
        
        if 'type_changes' in diff:
            print(f"{self.colors['purple']}🔀 ИЗМЕНЕН ТИП:{self.colors['end']}")
            for path, change in diff['type_changes'].items():
                old_type = change.get('old_type', '')
                new_type = change.get('new_type', '')
                print(f"  📍 {path}: {old_type} → {new_type}")

    def notify_error(self, url: str, error: str) -> None:
        """Отправляет уведомление об ошибке"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{self.colors['bold']}{self.colors['red']}❌ ОШИБКА{self.colors['end']}")
        print(f"{self.colors['cyan']}URL:{self.colors['end']} {url}")
        print(f"{self.colors['cyan']}Время:{self.colors['end']} {timestamp}")
        print(f"{self.colors['red']}Ошибка:{self.colors['end']} {error}")
        print(f"{self.colors['cyan']}{'='*60}{self.colors['end']}\n")

    def notify_success(self, message: str) -> None:
        """Отправляет уведомление об успешном выполнении"""
        print(f"{self.colors['green']}✅ {message}{self.colors['end']}")

    def notify_info(self, message: str) -> None:
        """Отправляет информационное уведомление"""
        print(f"{self.colors['blue']}ℹ️ {message}{self.colors['end']}")