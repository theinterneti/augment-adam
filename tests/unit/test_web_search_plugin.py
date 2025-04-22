"""Tests for the web search plugin.

This module contains tests for the web search plugin functionality.

Version: 0.1.0
Created: 2025-04-22
"""

import os
import tempfile
import json
import time
from unittest.mock import patch, MagicMock

import pytest
import requests
from bs4 import BeautifulSoup

from dukat.plugins.web_search import WebSearchPlugin


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def plugin(temp_dir):
    """Create a web search plugin for testing."""
    return WebSearchPlugin(cache_dir=temp_dir)


def test_plugin_init(temp_dir):
    """Test that the plugin initializes correctly."""
    plugin = WebSearchPlugin(
        search_engine="duckduckgo",
        user_agent="Test User Agent",
        cache_dir=temp_dir,
        cache_expiry=7200,
    )

    assert plugin.name == "web_search"
    assert plugin.description == "Plugin for web search operations"
    assert plugin.version == "0.1.0"
    assert plugin.search_engine == "duckduckgo"
    assert plugin.user_agent == "Test User Agent"
    assert plugin.cache_dir == temp_dir
    assert plugin.cache_expiry == 7200

    # Check that the cache directory was created
    assert os.path.exists(temp_dir)


def test_get_cache_path(plugin, temp_dir):
    """Test that the plugin gets cache paths correctly."""
    # Test with a simple key
    cache_path = plugin._get_cache_path("test")
    assert cache_path.startswith(temp_dir)
    assert "test_" in cache_path
    assert cache_path.endswith(".json")

    # Test with a complex key
    cache_path = plugin._get_cache_path("https://example.com/path?query=value")
    assert cache_path.startswith(temp_dir)
    assert "_" in cache_path
    assert cache_path.endswith(".json")


def test_cache_and_get_results(plugin, temp_dir):
    """Test caching and retrieving results."""
    # Create some test results
    results = {
        "query": "test",
        "results": [
            {"title": "Test Result", "url": "https://example.com",
                "snippet": "This is a test result."},
        ],
        "timestamp": int(time.time()),
    }

    # Cache the results
    success = plugin._cache_results("test", results)
    assert success is True

    # Check that the cache file was created
    cache_path = plugin._get_cache_path("test")
    assert os.path.exists(cache_path)

    # Get the cached results
    cached_results = plugin._get_cached_results("test")
    assert cached_results is not None
    assert cached_results["query"] == "test"
    assert len(cached_results["results"]) == 1
    assert cached_results["results"][0]["title"] == "Test Result"

    # Test with expired cache
    expired_results = {
        "query": "expired",
        "results": [],
        "timestamp": int(time.time()) - plugin.cache_expiry - 1,
    }

    plugin._cache_results("expired", expired_results)
    cached_results = plugin._get_cached_results("expired")
    assert cached_results is None


@patch("dukat.plugins.web_search.requests.get")
def test_search_duckduckgo(mock_get, plugin):
    """Test searching with DuckDuckGo."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <body>
            <div class="result">
                <h2 class="result__title"><a href="https://example.com">Example Title</a></h2>
                <a class="result__url">https://example.com</a>
                <div class="result__snippet">This is an example snippet.</div>
            </div>
            <div class="result">
                <h2 class="result__title"><a href="https://example.org">Another Title</a></h2>
                <a class="result__url">https://example.org</a>
                <div class="result__snippet">This is another example snippet.</div>
            </div>
        </body>
    </html>
    """
    mock_get.return_value = mock_response

    # Search for a query
    results = plugin._search_duckduckgo("test query", 2)

    # Check that the request was made correctly
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert "https://html.duckduckgo.com/html/" in args[0]
    assert "test%20query" in args[0]  # URL encoded space

    # Check the results
    assert results["query"] == "test query"
    assert len(results["results"]) == 2
    assert results["results"][0]["title"] == "Example Title"
    assert results["results"][0]["url"] == "https://example.com"
    assert results["results"][0]["snippet"] == "This is an example snippet."
    assert results["results"][1]["title"] == "Another Title"
    assert results["results"][1]["url"] == "https://example.org"
    assert results["results"][1]["snippet"] == "This is another example snippet."


@patch("dukat.plugins.web_search.requests.get")
def test_search_google(mock_get, plugin):
    """Test searching with Google."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <body>
            <div class="g">
                <h3>Example Title</h3>
                <a href="https://example.com">Link</a>
                <div class="VwiC3b">This is an example snippet.</div>
            </div>
            <div class="g">
                <h3>Another Title</h3>
                <a href="https://example.org">Link</a>
                <div class="VwiC3b">This is another example snippet.</div>
            </div>
        </body>
    </html>
    """
    mock_get.return_value = mock_response

    # Set the search engine to Google
    plugin.search_engine = "google"

    # Search for a query
    results = plugin._search_google("test query", 2)

    # Check that the request was made correctly
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert "https://www.google.com/search" in args[0]
    assert "test%20query" in args[0]  # URL encoded space
    assert "num=2" in args[0]

    # Check the results
    assert results["query"] == "test query"
    assert len(results["results"]) == 2
    assert results["results"][0]["title"] == "Example Title"
    assert results["results"][0]["url"] == "https://example.com"
    assert results["results"][0]["snippet"] == "This is an example snippet."
    assert results["results"][1]["title"] == "Another Title"
    assert results["results"][1]["url"] == "https://example.org"
    assert results["results"][1]["snippet"] == "This is another example snippet."


@patch("dukat.plugins.web_search.requests.get")
def test_fetch_url(mock_get, plugin):
    """Test fetching a URL."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <head>
            <title>Example Page</title>
        </head>
        <body>
            <article>
                <h1>Example Article</h1>
                <p>This is an example article.</p>
                <a href="https://example.com/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
            </article>
        </body>
    </html>
    """
    mock_get.return_value = mock_response

    # Fetch a URL
    result = plugin.fetch_url("https://example.com")

    # Check that the request was made correctly
    mock_get.assert_called_once_with(
        "https://example.com",
        headers={"User-Agent": plugin.user_agent},
        timeout=10,
    )

    # Check the result
    assert result["url"] == "https://example.com"
    assert result["title"] == "Example Page"
    assert "Example Article" in result["content"]
    assert "This is an example article." in result["content"]
    assert len(result["links"]) == 2
    assert result["links"][0]["url"] == "https://example.com/page1"
    assert result["links"][0]["text"] == "Page 1"
    assert result["links"][1]["url"] == "https://example.com/page2"
    assert result["links"][1]["text"] == "Page 2"


@patch("dukat.plugins.web_search.WebSearchPlugin.search")
def test_execute_search(mock_search, plugin):
    """Test executing a search."""
    # Set up the mock
    mock_search.return_value = {
        "query": "test query",
        "results": [
            {"title": "Test Result", "url": "https://example.com",
                "snippet": "This is a test result."},
        ],
        "timestamp": int(time.time()),
    }

    # Execute a search
    result = plugin.execute(
        action="search",
        query="test query",
        num_results=5,
        use_cache=True,
    )

    # Check that the search was called correctly
    mock_search.assert_called_once_with("test query", 5, True)

    # Check the result
    assert result["query"] == "test query"
    assert len(result["results"]) == 1
    assert result["results"][0]["title"] == "Test Result"


@patch("dukat.plugins.web_search.WebSearchPlugin.fetch_url")
def test_execute_fetch(mock_fetch, plugin):
    """Test executing a fetch."""
    # Set up the mock
    mock_fetch.return_value = {
        "url": "https://example.com",
        "title": "Example Page",
        "content": "This is an example page.",
        "links": [],
        "timestamp": int(time.time()),
    }

    # Execute a fetch
    result = plugin.execute(
        action="fetch",
        query="https://example.com",
        use_cache=True,
    )

    # Check that the fetch was called correctly
    mock_fetch.assert_called_once_with("https://example.com", True)

    # Check the result
    assert result["url"] == "https://example.com"
    assert result["title"] == "Example Page"
    assert result["content"] == "This is an example page."


def test_execute_invalid_action(plugin):
    """Test executing with an invalid action."""
    result = plugin.execute(
        action="invalid",
        query="test",
    )

    assert "error" in result
    assert "Unknown action" in result["error"]
