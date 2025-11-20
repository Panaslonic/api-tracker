"""
Тесты для модуля поиска документации API
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from api_watcher.utils.docs_finder import APIDocsFinder, find_api_documentation


class TestAPIDocsFinder:
    """Тесты для класса APIDocsFinder"""
    
    @pytest.mark.asyncio
    async def test_extract_base_url(self):
        """Тест извлечения базового URL"""
        # Валидные URL
        assert APIDocsFinder._extract_base_url('https://api.example.com/v1/users') == 'https://api.example.com'
        assert APIDocsFinder._extract_base_url('http://example.com/docs') == 'http://example.com'
        
        # Невалидные URL
        assert APIDocsFinder._extract_base_url('not-a-url') is None
        assert APIDocsFinder._extract_base_url('') is None
    
    @pytest.mark.asyncio
    async def test_find_openapi_direct_success(self):
        """Тест успешного прямого поиска OpenAPI"""
        async with APIDocsFinder() as finder:
            # Мокаем HTTP запрос
            with patch.object(finder.session, 'get') as mock_get:
                # Создаем мок ответа
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.headers = {'Content-Type': 'application/json'}
                mock_response.text = AsyncMock(return_value='{"openapi": "3.0.0"}')
                
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = await finder.find_openapi_direct('https://api.example.com/v1/users')
                
                # Проверяем, что был найден URL
                assert result is not None
                assert 'api.example.com' in result
    
    @pytest.mark.asyncio
    async def test_find_openapi_direct_not_found(self):
        """Тест когда OpenAPI не найден"""
        async with APIDocsFinder() as finder:
            with patch.object(finder.session, 'get') as mock_get:
                # Все запросы возвращают 404
                mock_response = AsyncMock()
                mock_response.status = 404
                
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = await finder.find_openapi_direct('https://api.example.com/v1/users')
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_search_via_serpapi_success(self):
        """Тест успешного поиска через SerpAPI"""
        async with APIDocsFinder(serpapi_key='test_key') as finder:
            with patch.object(finder.session, 'get') as mock_get:
                # Мокаем ответ SerpAPI
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={
                    'organic_results': [
                        {
                            'title': 'Example API Documentation',
                            'link': 'https://docs.example.com',
                            'snippet': 'Official API documentation'
                        }
                    ]
                })
                
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = await finder.search_via_serpapi('Example API', 'Get Users')
                
                assert result is not None
                assert result['link'] == 'https://docs.example.com'
                assert result['title'] == 'Example API Documentation'
    
    @pytest.mark.asyncio
    async def test_search_via_serpapi_no_key(self):
        """Тест поиска через SerpAPI без ключа"""
        async with APIDocsFinder() as finder:
            result = await finder.search_via_serpapi('Example API')
            
            # Без ключа должен вернуть None
            assert result is None
    
    @pytest.mark.asyncio
    async def test_find_documentation_openapi_found(self):
        """Тест комплексного поиска - найден OpenAPI"""
        async with APIDocsFinder() as finder:
            # Мокаем find_openapi_direct
            with patch.object(finder, 'find_openapi_direct', return_value='https://api.example.com/openapi.json'):
                result = await finder.find_documentation(
                    'https://api.example.com/v1/users',
                    'Example API',
                    'Get Users'
                )
                
                assert result is not None
                assert result['type'] == 'openapi'
                assert result['url'] == 'https://api.example.com/openapi.json'
    
    @pytest.mark.asyncio
    async def test_find_documentation_serpapi_fallback(self):
        """Тест комплексного поиска - fallback на SerpAPI"""
        async with APIDocsFinder(serpapi_key='test_key') as finder:
            # OpenAPI не найден
            with patch.object(finder, 'find_openapi_direct', return_value=None):
                # SerpAPI находит результат
                with patch.object(finder, 'search_via_serpapi', return_value={
                    'link': 'https://docs.example.com',
                    'title': 'Example API Docs',
                    'snippet': 'Documentation'
                }):
                    result = await finder.find_documentation(
                        'https://api.example.com/v1/users',
                        'Example API',
                        'Get Users'
                    )
                    
                    assert result is not None
                    assert result['type'] == 'search'
                    assert result['url'] == 'https://docs.example.com'
    
    @pytest.mark.asyncio
    async def test_find_documentation_nothing_found(self):
        """Тест когда ничего не найдено"""
        async with APIDocsFinder() as finder:
            with patch.object(finder, 'find_openapi_direct', return_value=None):
                with patch.object(finder, 'search_via_serpapi', return_value=None):
                    result = await finder.find_documentation(
                        'https://api.example.com/v1/users',
                        'Example API'
                    )
                    
                    assert result is None


class TestFindAPIDocumentation:
    """Тесты для функции find_api_documentation"""
    
    @pytest.mark.asyncio
    async def test_find_api_documentation_success(self):
        """Тест успешного поиска документации"""
        with patch('api_watcher.utils.docs_finder.APIDocsFinder') as MockFinder:
            # Мокаем контекстный менеджер
            mock_finder_instance = AsyncMock()
            mock_finder_instance.find_documentation = AsyncMock(return_value={
                'type': 'openapi',
                'url': 'https://api.example.com/openapi.json'
            })
            
            MockFinder.return_value.__aenter__.return_value = mock_finder_instance
            
            result = await find_api_documentation(
                'https://api.example.com/v1/users',
                'Example API',
                'Get Users',
                'test_key'
            )
            
            assert result is not None
            assert result['type'] == 'openapi'
    
    @pytest.mark.asyncio
    async def test_find_api_documentation_not_found(self):
        """Тест когда документация не найдена"""
        with patch('api_watcher.utils.docs_finder.APIDocsFinder') as MockFinder:
            mock_finder_instance = AsyncMock()
            mock_finder_instance.find_documentation = AsyncMock(return_value=None)
            
            MockFinder.return_value.__aenter__.return_value = mock_finder_instance
            
            result = await find_api_documentation(
                'https://api.example.com/v1/users',
                'Example API'
            )
            
            assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
