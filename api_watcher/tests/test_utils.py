"""
Тесты для утилит
"""

import pytest
from utils.comparator import Comparator


class TestComparator:
    """Тесты класса Comparator"""
    
    def test_comparator_init(self):
        """Тест инициализации Comparator"""
        comparator = Comparator()
        assert comparator is not None
    
    def test_compare_identical_data(self, sample_json_data):
        """Тест сравнения идентичных данных"""
        comparator = Comparator()
        
        result = comparator.compare(sample_json_data, sample_json_data)
        
        # Идентичные данные не должны иметь различий
        assert result is None or len(result) == 0
    
    def test_compare_different_data(self, sample_json_data, modified_json_data):
        """Тест сравнения различающихся данных"""
        comparator = Comparator()
        
        result = comparator.compare(sample_json_data, modified_json_data)
        
        # Должны быть обнаружены различия
        assert result is not None
        assert len(result) > 0
    
    def test_compare_added_field(self):
        """Тест обнаружения добавленного поля"""
        comparator = Comparator()
        
        old_data = {"name": "API", "version": "1.0"}
        new_data = {"name": "API", "version": "1.0", "description": "New field"}
        
        result = comparator.compare(old_data, new_data)
        
        assert result is not None
        # Проверяем, что обнаружено добавление
        assert any("added" in str(change).lower() for change in result)
    
    def test_compare_removed_field(self):
        """Тест обнаружения удаленного поля"""
        comparator = Comparator()
        
        old_data = {"name": "API", "version": "1.0", "description": "Old field"}
        new_data = {"name": "API", "version": "1.0"}
        
        result = comparator.compare(old_data, new_data)
        
        assert result is not None
        # Проверяем, что обнаружено удаление
        assert any("removed" in str(change).lower() for change in result)
    
    def test_compare_changed_value(self):
        """Тест обнаружения измененного значения"""
        comparator = Comparator()
        
        old_data = {"name": "API", "version": "1.0"}
        new_data = {"name": "API", "version": "2.0"}
        
        result = comparator.compare(old_data, new_data)
        
        assert result is not None
        # Проверяем, что обнаружено изменение
        assert any("changed" in str(change).lower() or "1.0" in str(change) for change in result)
    
    def test_compare_nested_objects(self):
        """Тест сравнения вложенных объектов"""
        comparator = Comparator()
        
        old_data = {
            "api": {
                "version": "1.0",
                "endpoints": ["GET /users", "POST /users"]
            }
        }
        new_data = {
            "api": {
                "version": "1.1",
                "endpoints": ["GET /users", "POST /users", "DELETE /users"]
            }
        }
        
        result = comparator.compare(old_data, new_data)
        
        assert result is not None
        assert len(result) > 0
    
    def test_compare_arrays(self):
        """Тест сравнения массивов"""
        comparator = Comparator()
        
        old_data = {"endpoints": ["GET /users", "POST /users"]}
        new_data = {"endpoints": ["GET /users", "POST /users", "PUT /users"]}
        
        result = comparator.compare(old_data, new_data)
        
        assert result is not None
        # Должно быть обнаружено добавление элемента в массив
        assert any("PUT /users" in str(change) for change in result)
    
    def test_compare_none_values(self):
        """Тест сравнения с None значениями"""
        comparator = Comparator()
        
        # Сравнение None с данными
        result1 = comparator.compare(None, {"test": "data"})
        assert result1 is not None
        
        # Сравнение данных с None
        result2 = comparator.compare({"test": "data"}, None)
        assert result2 is not None
        
        # Сравнение None с None
        result3 = comparator.compare(None, None)
        assert result3 is None or len(result3) == 0
    
    def test_compare_empty_objects(self):
        """Тест сравнения пустых объектов"""
        comparator = Comparator()
        
        result = comparator.compare({}, {})
        
        # Пустые объекты должны быть идентичными
        assert result is None or len(result) == 0
    
    def test_compare_different_types(self):
        """Тест сравнения разных типов данных"""
        comparator = Comparator()
        
        old_data = {"value": "string"}
        new_data = {"value": 123}
        
        result = comparator.compare(old_data, new_data)
        
        assert result is not None
        # Должно быть обнаружено изменение типа
        assert len(result) > 0