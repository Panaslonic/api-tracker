"""
Comparator - сравнение данных и формирование diff
Использует DeepDiff для детального сравнения структур данных
"""

from deepdiff import DeepDiff
from typing import Dict, Any, Optional
from config import Config


class Comparator:
    def __init__(self):
        # Настройки для DeepDiff из конфигурации
        self.ignore_order = Config.IGNORE_ORDER
        self.verbose_level = Config.VERBOSE_LEVEL

    def compare(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Сравнивает два набора данных и возвращает различия"""
        if old_data == new_data:
            return None
        
        try:
            diff = DeepDiff(
                old_data, 
                new_data,
                ignore_order=self.ignore_order,
                verbose_level=self.verbose_level,
                exclude_paths=Config.get_exclude_paths()
            )
            
            if diff:
                return self._process_diff(diff)
            return None
            
        except Exception as e:
            print(f"❌ Ошибка при сравнении данных: {e}")
            return {'error': str(e)}



    def _process_diff(self, diff: DeepDiff) -> Dict[str, Any]:
        """Обрабатывает результат DeepDiff для удобного отображения"""
        result = {}
        
        # Добавленные элементы словаря
        if 'dictionary_item_added' in diff:
            result['dictionary_item_added'] = [
                self._clean_path(path) for path in diff['dictionary_item_added']
            ]
        
        # Удаленные элементы словаря
        if 'dictionary_item_removed' in diff:
            result['dictionary_item_removed'] = [
                self._clean_path(path) for path in diff['dictionary_item_removed']
            ]
        
        # Измененные значения
        if 'values_changed' in diff:
            result['values_changed'] = {}
            for path, change in diff['values_changed'].items():
                clean_path = self._clean_path(path)
                result['values_changed'][clean_path] = {
                    'old_value': change.get('old_value'),
                    'new_value': change.get('new_value')
                }
        
        # Добавленные элементы в итерируемых объектах
        if 'iterable_item_added' in diff:
            result['iterable_item_added'] = {}
            for path, items in diff['iterable_item_added'].items():
                clean_path = self._clean_path(path)
                result['iterable_item_added'][clean_path] = items
        
        # Удаленные элементы из итерируемых объектов
        if 'iterable_item_removed' in diff:
            result['iterable_item_removed'] = {}
            for path, items in diff['iterable_item_removed'].items():
                clean_path = self._clean_path(path)
                result['iterable_item_removed'][clean_path] = items
        
        # Изменения типов
        if 'type_changes' in diff:
            result['type_changes'] = {}
            for path, change in diff['type_changes'].items():
                clean_path = self._clean_path(path)
                result['type_changes'][clean_path] = {
                    'old_type': str(change.get('old_type', '')),
                    'new_type': str(change.get('new_type', ''))
                }
        
        return result

    def _clean_path(self, path: str) -> str:
        """Очищает путь от технических деталей DeepDiff"""
        # Убираем "root[" и "]" из начала и конца
        if path.startswith("root["):
            path = path[5:]
        if path.endswith("]"):
            path = path[:-1]
        
        # Убираем кавычки вокруг ключей
        path = path.replace("'", "").replace('"', '')
        
        return path

    def get_summary(self, diff: Dict[str, Any]) -> str:
        """Возвращает краткое описание изменений"""
        if not diff or 'error' in diff:
            return "Ошибка при сравнении"
        
        summary_parts = []
        
        if 'dictionary_item_added' in diff:
            count = len(diff['dictionary_item_added'])
            summary_parts.append(f"добавлено {count} элементов")
        
        if 'dictionary_item_removed' in diff:
            count = len(diff['dictionary_item_removed'])
            summary_parts.append(f"удалено {count} элементов")
        
        if 'values_changed' in diff:
            count = len(diff['values_changed'])
            summary_parts.append(f"изменено {count} значений")
        
        if 'type_changes' in diff:
            count = len(diff['type_changes'])
            summary_parts.append(f"изменен тип у {count} элементов")
        
        return ", ".join(summary_parts) if summary_parts else "обнаружены изменения"