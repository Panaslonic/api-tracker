"""
Tests for ContentProcessor validation logic
"""

import pytest
from api_watcher.services.content_processor import ContentProcessor
from api_watcher.notifier.base import NotifierManager


class TestContentProcessorValidation:
    """Tests for the improved is_valid_response method"""
    
    @pytest.fixture
    def processor(self):
        """Create ContentProcessor with mock notifier"""
        notifier = NotifierManager()
        return ContentProcessor(notifier)
    
    def test_valid_html_response(self, processor):
        """Test valid HTML response"""
        content = "<html><body>" + "Valid content " * 20 + "</body></html>"
        is_valid, error = processor.is_valid_response(content, "http://example.com", 200)
        assert is_valid is True
        assert error is None
    
    def test_empty_response(self, processor):
        """Test empty response"""
        is_valid, error = processor.is_valid_response("", "http://example.com", 200)
        assert is_valid is False
        assert error == "Empty response"
    
    def test_short_response(self, processor):
        """Test short response (< 100 chars)"""
        is_valid, error = processor.is_valid_response("Short", "http://example.com", 200)
        assert is_valid is False
        assert "Short response" in error
    
    def test_http_404_status(self, processor):
        """Test HTTP 404 status code"""
        content = "A" * 200
        is_valid, error = processor.is_valid_response(content, "http://example.com", 404)
        assert is_valid is False
        assert "HTTP 404" in error
    
    def test_http_500_status(self, processor):
        """Test HTTP 500 status code"""
        content = "A" * 200
        is_valid, error = processor.is_valid_response(content, "http://example.com", 500)
        assert is_valid is False
        assert "HTTP 500" in error
    
    def test_json_with_error_field(self, processor):
        """Test JSON response with error field"""
        content = '{"error": "Invalid API key", "status": "failed"}'
        is_valid, error = processor.is_valid_response(content, "http://api.example.com", 200)
        assert is_valid is False
        assert "JSON error" in error
        assert "Invalid API key" in error
    
    def test_json_with_success_false(self, processor):
        """Test JSON response with success: false"""
        content = '{"success": false, "message": "Resource not found"}'
        is_valid, error = processor.is_valid_response(content, "http://api.example.com", 200)
        assert is_valid is False
        assert "API error" in error
        assert "Resource not found" in error
    
    def test_json_with_status_error(self, processor):
        """Test JSON response with status: error"""
        content = '{"status": "error", "message": "Database connection failed"}'
        is_valid, error = processor.is_valid_response(content, "http://api.example.com", 200)
        assert is_valid is False
        assert "Status error" in error
        assert "Database connection failed" in error
    
    def test_json_with_status_fail(self, processor):
        """Test JSON response with status: fail"""
        content = '{"status": "fail", "message": "Validation error"}'
        is_valid, error = processor.is_valid_response(content, "http://api.example.com", 200)
        assert is_valid is False
        assert "Status error" in error
    
    def test_valid_json_response(self, processor):
        """Test valid JSON response without errors"""
        content = '{"status": "success", "data": {"id": 123, "name": "Test"}}'
        is_valid, error = processor.is_valid_response(content, "http://api.example.com", 200)
        assert is_valid is True
        assert error is None
    
    def test_html_with_404_text(self, processor):
        """Test HTML with '404' text"""
        content = "<html><body><h1>404 Not Found</h1>" + "Content " * 20 + "</body></html>"
        is_valid, error = processor.is_valid_response(content, "http://example.com", 200)
        assert is_valid is False
        assert "Page not found" in error
    
    def test_html_with_error_text(self, processor):
        """Test HTML with 'internal server error' text"""
        content = "<html><body><h1>500 Internal Server Error</h1>" + "Content " * 20 + "</body></html>"
        is_valid, error = processor.is_valid_response(content, "http://example.com", 200)
        assert is_valid is False
        assert "Internal server error" in error
    
    def test_html_with_forbidden_text(self, processor):
        """Test HTML with 'forbidden' text"""
        content = "<html><body><h1>403 Forbidden</h1>" + "Content " * 20 + "</body></html>"
        is_valid, error = processor.is_valid_response(content, "http://example.com", 200)
        assert is_valid is False
        assert "Access forbidden" in error
    
    def test_malformed_json(self, processor):
        """Test malformed JSON falls back to HTML validation"""
        content = '{"invalid": json content}' + " " * 100
        is_valid, error = processor.is_valid_response(content, "http://example.com", 200)
        # Should pass HTML validation since no error indicators
        assert is_valid is True
        assert error is None
    
    def test_json_with_empty_error_field(self, processor):
        """Test JSON with empty error field (should be valid)"""
        content = '{"error": "", "data": "some data"}' + " " * 100
        is_valid, error = processor.is_valid_response(content, "http://api.example.com", 200)
        # Empty error field should not trigger validation failure
        assert is_valid is True
        assert error is None
    
    def test_json_with_null_error_field(self, processor):
        """Test JSON with null error field (should be valid)"""
        content = '{"error": null, "data": "some data"}' + " " * 100
        is_valid, error = processor.is_valid_response(content, "http://api.example.com", 200)
        assert is_valid is True
        assert error is None
    
    def test_content_type_detection_openapi(self, processor):
        """Test OpenAPI content type detection"""
        content = '{"openapi": "3.0.0", "info": {"title": "Test API"}}'
        content_type = processor.detect_content_type("http://api.example.com/openapi.json", content)
        assert content_type == "openapi"
    
    def test_content_type_detection_json(self, processor):
        """Test JSON content type detection"""
        content = '{"data": "test"}'
        content_type = processor.detect_content_type("http://api.example.com/data.json", content)
        assert content_type == "json"
    
    def test_content_type_detection_html(self, processor):
        """Test HTML content type detection"""
        content = "<html><body>Test</body></html>"
        content_type = processor.detect_content_type("http://example.com/page.html", content)
        assert content_type == "html"
