"""
Тесты для парсеров API документации
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from parsers.json_parser import JSONParser
from parsers.html_parser import HTMLParser
from parsers.openapi_parser import OpenAPIParser
from parsers.postman_parser import PostmanParser
from parsers.md_parser import MarkdownParser


class TestJSONParser:
    """Тесты JSON парсера"""
    
    def test_json_parser_init(self):
        """Тест инициализации JSON парсера"""
        parser = JSONParser()
        assert parser is not None
    
    @patch('requests.get')
    def test_parse_valid_json_url(self, mock_get):
        """Тест парсинга валидного JSON по URL"""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data", "version": "1.0"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = JSONParser()
        result = parser.parse("https://example.com/api.json")
        
        assert result["test"] == "data"
        assert result["version"] == "1.0"
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_parse_invalid_json_url(self, mock_get):
        """Тест парсинга невалидного JSON"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "invalid json"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = JSONParser()
        
        with pytest.raises(ValueError, match="Не удалось распарсить JSON"):
            parser.parse("https://example.com/invalid.json")
    
    @patch('requests.get')
    def test_parse_network_error(self, mock_get):
        """Тест обработки сетевой ошибки"""
        mock_get.side_effect = Exception("Network error")
        
        parser = JSONParser()
        
        with pytest.raises(Exception, match="Network error"):
            parser.parse("https://example.com/api.json")
    
    def test_parse_local_file(self, temp_dir):
        """Тест парсинга локального JSON файла"""
        json_file = f"{temp_dir}/test.json"
        test_data = {"local": "file", "test": True}
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        parser = JSONParser()
        result = parser.parse(f"file://{json_file}")
        
        assert result["local"] == "file"
        assert result["test"] is True


class TestHTMLParser:
    """Тесты HTML парсера"""
    
    def test_html_parser_init(self):
        """Тест инициализации HTML парсера"""
        parser = HTMLParser()
        assert parser is not None
    
    @patch('requests.get')
    def test_parse_html_with_selector(self, mock_get):
        """Тест парсинга HTML с селектором"""
        html_content = """
        <html>
            <body>
                <div class="api-method">
                    <h2>Get User</h2>
                    <p>Returns user information</p>
                </div>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = HTMLParser()
        result = parser.parse("https://example.com/docs", selector=".api-method")
        
        assert "method_content" in result
        assert "Get User" in result["method_content"]["method_name"]
    
    @patch('requests.get')
    def test_parse_html_without_selector(self, mock_get):
        """Тест парсинга HTML без селектора"""
        html_content = "<html><body><h1>API Documentation</h1></body></html>"
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = HTMLParser()
        result = parser.parse("https://example.com/docs")
        
        assert "full_content" in result
        assert "API Documentation" in result["full_content"]


class TestOpenAPIParser:
    """Тесты OpenAPI парсера"""
    
    def test_openapi_parser_init(self):
        """Тест инициализации OpenAPI парсера"""
        parser = OpenAPIParser()
        assert parser is not None
    
    @patch('requests.get')
    def test_parse_openapi_json(self, mock_get):
        """Тест парсинга OpenAPI JSON"""
        openapi_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {"summary": "Get users"},
                    "post": {"summary": "Create user"}
                }
            }
        }
        
        mock_response = Mock()
        mock_response.json.return_value = openapi_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = OpenAPIParser()
        result = parser.parse("https://example.com/openapi.json")
        
        assert result["info"]["title"] == "Test API"
        assert "/users" in result["paths"]
    
    @patch('requests.get')
    def test_parse_openapi_with_method_filter(self, mock_get):
        """Тест парсинга OpenAPI с фильтром методов"""
        openapi_data = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {"summary": "Get users"},
                    "post": {"summary": "Create user"}
                },
                "/posts": {
                    "get": {"summary": "Get posts"}
                }
            }
        }
        
        mock_response = Mock()
        mock_response.json.return_value = openapi_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = OpenAPIParser()
        result = parser.parse("https://example.com/openapi.json", method_filter="/users")
        
        # Результат должен содержать только отфильтрованные пути
        assert "/users" in str(result)


class TestPostmanParser:
    """Тесты Postman парсера"""
    
    def test_postman_parser_init(self):
        """Тест инициализации Postman парсера"""
        parser = PostmanParser()
        assert parser is not None
    
    @patch('requests.get')
    def test_parse_postman_collection(self, mock_get):
        """Тест парсинга Postman коллекции"""
        postman_data = {
            "info": {"name": "Test Collection", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
            "item": [
                {
                    "name": "Get Users",
                    "request": {
                        "method": "GET",
                        "url": "{{base_url}}/users"
                    }
                }
            ]
        }
        
        mock_response = Mock()
        mock_response.json.return_value = postman_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = PostmanParser()
        result = parser.parse("https://example.com/collection.json")
        
        assert result["info"]["name"] == "Test Collection"
        assert len(result["item"]) == 1
        assert result["item"][0]["name"] == "Get Users"


class TestMarkdownParser:
    """Тесты Markdown парсера"""
    
    def test_markdown_parser_init(self):
        """Тест инициализации Markdown парсера"""
        parser = MarkdownParser()
        assert parser is not None
    
    @patch('requests.get')
    def test_parse_markdown_content(self, mock_get):
        """Тест парсинга Markdown контента"""
        markdown_content = """
# API Documentation

## Authentication
Use Bearer token for authentication.

## Endpoints

### GET /users
Returns list of users.

### POST /users
Creates a new user.
        """
        
        mock_response = Mock()
        mock_response.text = markdown_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        parser = MarkdownParser()
        result = parser.parse("https://example.com/docs.md")
        
        assert "sections" in result
        sections = result["sections"]
        
        # Проверяем, что найдены основные секции
        section_titles = [section.get("title", "") for section in sections]
        assert any("API Documentation" in title for title in section_titles)
        assert any("Authentication" in title for title in section_titles)
        assert any("Endpoints" in title for title in section_titles)
    
    def test_parse_local_markdown_file(self, temp_dir):
        """Тест парсинга локального Markdown файла"""
        md_file = f"{temp_dir}/test.md"
        markdown_content = "# Test\n\nThis is a test markdown file."
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        parser = MarkdownParser()
        result = parser.parse(f"file://{md_file}")
        
        assert "sections" in result
        assert len(result["sections"]) > 0