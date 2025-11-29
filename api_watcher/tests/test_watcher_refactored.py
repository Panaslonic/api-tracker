"""
Unit tests for Refactored APIWatcher
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from api_watcher.watcher import APIWatcher
from api_watcher.storage.repository import SnapshotRepository
from api_watcher.utils.async_fetcher import ContentFetcher
from api_watcher.notifier.base import NotifierManager

class TestAPIWatcherRefactored:
    """Tests for APIWatcher"""
    
    @pytest.fixture
    def mock_repository(self):
        return Mock(spec=SnapshotRepository)
    
    @pytest.fixture
    def mock_fetcher(self):
        fetcher = Mock(spec=ContentFetcher)
        fetcher.fetch = AsyncMock()
        return fetcher
    
    @pytest.fixture
    def mock_notifier_manager(self):
        return Mock(spec=NotifierManager)
    
    @pytest.fixture
    def watcher(self, mock_repository, mock_fetcher, mock_notifier_manager):
        # Patch Config to avoid side effects
        with patch('api_watcher.watcher.Config') as mock_config:
            mock_config.DATABASE_URL = 'sqlite:///:memory:'
            mock_config.is_openrouter_configured.return_value = False
            mock_config.is_gemini_configured.return_value = False
            
            return APIWatcher(
                repository=mock_repository,
                fetcher=mock_fetcher,
                notifier_manager=mock_notifier_manager
            )

    @pytest.mark.asyncio
    async def test_fetch_content(self, watcher, mock_fetcher):
        """Test async fetch content"""
        mock_fetcher.fetch.return_value = "content"
        result = await watcher.fetch_content("http://example.com")
        assert result == "content"
        mock_fetcher.fetch.assert_called_once_with("http://example.com")

    def test_is_valid_response_valid(self, watcher):
        """Test valid response check"""
        valid_content = "A" * 200
        assert watcher._is_valid_response(valid_content, "http://example.com") is True

    def test_is_valid_response_invalid_short(self, watcher):
        """Test short response check"""
        short_content = "Short"
        assert watcher._is_valid_response(short_content, "http://example.com") is False

    def test_is_valid_response_error(self, watcher):
        """Test error response check"""
        error_content = "404 Not Found" * 10
        assert watcher._is_valid_response(error_content, "http://example.com") is False

    def test_detect_content_type(self, watcher):
        """Test content type detection"""
        assert watcher.detect_content_type("http://api/openapi.json", "{}") == "openapi"
        assert watcher.detect_content_type("http://api/data.json", '{"openapi": "3.0"}') == "openapi"
        assert watcher.detect_content_type("http://api/data.json", '{"key": "value"}') == "json"
        assert watcher.detect_content_type("http://api/page", "<html></html>") == "html"

    @pytest.mark.asyncio
    async def test_process_url_new_snapshot(self, watcher, mock_repository, mock_fetcher):
        """Test processing new URL (first snapshot)"""
        url = "http://example.com"
        # Content must be > 100 chars to be valid
        content = "<html><body>New Content</body></html>" + "<!-- padding -->" * 10
        mock_fetcher.fetch.return_value = content
        mock_repository.get_latest.return_value = None
        
        result = await watcher.process_url(url)
        
        assert result['url'] == url
        assert result['has_changes'] is False
        assert result.get('is_first_snapshot') is True
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_url_no_changes(self, watcher, mock_repository, mock_fetcher):
        """Test processing URL with no changes"""
        url = "http://example.com"
        # Content must be > 100 chars to be valid
        content = "<html><body>Content</body></html>" + "<!-- padding -->" * 10
        mock_fetcher.fetch.return_value = content
        
        # Mock old snapshot
        old_snapshot = Mock()
        old_snapshot.content_hash = watcher.comparator.calculate_hash(content)
        old_snapshot.raw_html = content
        mock_repository.get_latest.return_value = old_snapshot
        
        result = await watcher.process_url(url)
        
        assert result['url'] == url
        assert result['has_changes'] is False
        mock_repository.save.assert_not_called()

