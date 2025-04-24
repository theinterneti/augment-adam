"""Web search plugin for the Dukat assistant.

This module provides a plugin for searching the web and
retrieving information from websites.

Version: 0.1.0
Created: 2025-04-22
"""

from typing import Dict, Any, List, Optional, Set
import logging
import os
import json
import time
import urllib.parse
import re
import hashlib
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from augment_adam.core.circuit_breaker import circuit_breaker
from augment_adam.core.errors import CircuitBreakerError, ErrorCategory, wrap_error, log_error
from augment_adam.plugins.base import Plugin

logger = logging.getLogger(__name__)


class WebSearchPlugin(Plugin):
    """Plugin for web search operations.

    This plugin provides functionality for searching the web
    and retrieving information from websites.

    Attributes:
        name: The name of the plugin.
        description: A description of the plugin.
        version: The version of the plugin.
        search_engine: The search engine to use.
        user_agent: The user agent to use for requests.
        cache_dir: The directory to cache search results.
        cache_expiry: The expiry time for cached results in seconds.
    """

    def __init__(
        self,
        search_engine: str = "duckduckgo",
        user_agent: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_expiry: int = 3600,  # 1 hour
        version: str = "0.1.0",
    ):
        """Initialize the web search plugin.

        Args:
            search_engine: The search engine to use.
            user_agent: The user agent to use for requests.
            cache_dir: The directory to cache search results.
            cache_expiry: The expiry time for cached results in seconds.
            version: The version of the plugin.
        """
        super().__init__(
            name="web_search",
            description="Plugin for web search operations",
            version=version,
        )

        self.search_engine = search_engine.lower()
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.cache_dir = cache_dir or os.path.expanduser(
            "~/.augment_adam/cache/web_search")
        self.cache_expiry = cache_expiry

        # Create cache directory if it doesn't exist
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)

        logger.info(
            f"Initialized web search plugin with search engine: {search_engine}")

    def execute(
        self,
        action: str,
        query: str,
        num_results: int = 5,
        use_cache: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute a web search operation.

        Args:
            action: The action to perform (search, fetch).
            query: The search query or URL.
            num_results: The number of results to return.
            use_cache: Whether to use cached results.
            **kwargs: Additional arguments for the action.

        Returns:
            The result of the operation.
        """
        try:
            if action == "search":
                return self.search(query, num_results, use_cache)
            elif action == "fetch":
                return self.fetch_url(query, use_cache)
            else:
                error_msg = f"Unknown action: {action}"
                logger.error(error_msg)
                return {"error": error_msg}

        except CircuitBreakerError as e:
            # Handle circuit breaker errors specifically
            error = wrap_error(
                e,
                message=f"Service unavailable for {action} with query {query}",
                category=ErrorCategory.DEPENDENCY,
                details={
                    "action": action,
                    "query": query,
                    "circuit_breaker": e.details.get("circuit_breaker", {}),
                },
            )
            log_error(error, logger=logger)
            return {
                "error": str(error),
                "circuit_breaker": e.details.get("circuit_breaker", {}),
                "status": "service_unavailable",
            }

        except Exception as e:
            # Handle other exceptions
            error = wrap_error(
                e,
                message=f"Error performing {action} with query {query}",
                category=ErrorCategory.PLUGIN,
                details={
                    "action": action,
                    "query": query,
                },
            )
            log_error(error, logger=logger)
            return {"error": str(error)}

    def search(
        self,
        query: str,
        num_results: int = 5,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Search the web for a query.

        Args:
            query: The search query.
            num_results: The number of results to return.
            use_cache: Whether to use cached results.

        Returns:
            The search results.
        """
        # Check if we have cached results
        if use_cache and self.cache_dir:
            cached_results = self._get_cached_results(query)
            if cached_results:
                logger.info(f"Using cached results for query: {query}")
                return cached_results

        # Perform the search
        if self.search_engine == "duckduckgo":
            results = self._search_duckduckgo(query, num_results)
        elif self.search_engine == "google":
            results = self._search_google(query, num_results)
        else:
            error_msg = f"Unsupported search engine: {self.search_engine}"
            logger.error(error_msg)
            return {"error": error_msg}

        # Cache the results
        if self.cache_dir:
            self._cache_results(query, results)

        return results

    @circuit_breaker(
        name="web_fetch_url",
        failure_threshold=3,
        timeout_seconds=300.0,  # 5 minutes
        excluded_exceptions={requests.exceptions.ConnectionError}
    )
    def fetch_url(
        self,
        url: str,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Fetch the content of a URL.

        Args:
            url: The URL to fetch.
            use_cache: Whether to use cached results.

        Returns:
            The content of the URL.
        """
        # Check if we have cached results
        if use_cache and self.cache_dir:
            cached_results = self._get_cached_results(url)
            if cached_results:
                logger.info(f"Using cached results for URL: {url}")
                return cached_results

        try:
            # Fetch the URL
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract the title
            title = soup.title.string if soup.title else ""

            # Extract the main content
            # This is a simple approach and may not work for all websites
            main_content = ""

            # Try to find the main content
            main_tags = soup.find_all(["article", "main", "div", "section"])
            if main_tags:
                # Find the tag with the most text
                main_tag = max(main_tags, key=lambda tag: len(tag.get_text()))
                main_content = main_tag.get_text(separator=" ", strip=True)
            else:
                # Fall back to the body
                main_content = soup.body.get_text(
                    separator=" ", strip=True) if soup.body else ""

            # Clean up the content
            main_content = re.sub(r"\s+", " ", main_content).strip()

            # Truncate if too long
            if len(main_content) > 10000:
                main_content = main_content[:10000] + "..."

            # Extract links
            links = []
            for link in soup.find_all("a", href=True):
                href = link["href"]
                text = link.get_text(strip=True)

                # Skip empty links
                if not text:
                    continue

                # Handle relative URLs
                if href.startswith("/"):
                    parsed_url = urllib.parse.urlparse(url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    href = base_url + href

                # Skip non-HTTP links
                if not href.startswith(("http://", "https://")):
                    continue

                links.append({
                    "url": href,
                    "text": text,
                })

            # Limit the number of links
            links = links[:20]

            # Create the result
            result = {
                "url": url,
                "title": title,
                "content": main_content,
                "links": links,
                "timestamp": int(time.time()),
            }

            # Cache the result
            if self.cache_dir:
                self._cache_results(url, result)

            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching URL {url}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    @circuit_breaker(
        name="web_search_duckduckgo",
        failure_threshold=3,
        timeout_seconds=300.0,  # 5 minutes
        excluded_exceptions={requests.exceptions.ConnectionError}
    )
    def _search_duckduckgo(
        self,
        query: str,
        num_results: int = 5,
    ) -> Dict[str, Any]:
        """Search DuckDuckGo for a query.

        Args:
            query: The search query.
            num_results: The number of results to return.

        Returns:
            The search results.
        """
        # DuckDuckGo doesn't have an official API, so we'll use the HTML site
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

        try:
            # Fetch the search results
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract the results
            results = []
            for result in soup.select(".result"):
                # Extract the title
                title_elem = result.select_one(".result__title")
                title = title_elem.get_text(strip=True) if title_elem else ""

                # Extract the URL
                url_elem = result.select_one(".result__url")
                result_url = url_elem.get_text(strip=True) if url_elem else ""

                # Extract the snippet
                snippet_elem = result.select_one(".result__snippet")
                snippet = snippet_elem.get_text(
                    strip=True) if snippet_elem else ""

                # Skip results without a URL
                if not result_url:
                    continue

                # Add the result
                results.append({
                    "title": title,
                    "url": result_url,
                    "snippet": snippet,
                })

                # Stop if we have enough results
                if len(results) >= num_results:
                    break

            return {
                "query": query,
                "results": results,
                "timestamp": int(time.time()),
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"Error searching DuckDuckGo for {query}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    @circuit_breaker(
        name="web_search_google",
        failure_threshold=3,
        timeout_seconds=300.0,  # 5 minutes
        excluded_exceptions={requests.exceptions.ConnectionError}
    )
    def _search_google(
        self,
        query: str,
        num_results: int = 5,
    ) -> Dict[str, Any]:
        """Search Google for a query.

        Args:
            query: The search query.
            num_results: The number of results to return.

        Returns:
            The search results.
        """
        # Google doesn't have an official API for free, so we'll use the HTML site
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}"

        try:
            # Fetch the search results
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract the results
            results = []
            for result in soup.select(".g"):
                # Extract the title
                title_elem = result.select_one("h3")
                title = title_elem.get_text(strip=True) if title_elem else ""

                # Extract the URL
                url_elem = result.select_one("a")
                result_url = url_elem["href"] if url_elem and "href" in url_elem.attrs else ""

                # Clean up the URL
                if result_url.startswith("/url?q="):
                    result_url = result_url[7:]
                    result_url = result_url.split("&")[0]

                # Extract the snippet
                snippet_elem = result.select_one(".VwiC3b")
                snippet = snippet_elem.get_text(
                    strip=True) if snippet_elem else ""

                # Skip results without a URL
                if not result_url:
                    continue

                # Add the result
                results.append({
                    "title": title,
                    "url": result_url,
                    "snippet": snippet,
                })

                # Stop if we have enough results
                if len(results) >= num_results:
                    break

            return {
                "query": query,
                "results": results,
                "timestamp": int(time.time()),
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"Error searching Google for {query}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _get_cache_path(self, key: str) -> str:
        """Get the cache path for a key.

        Args:
            key: The cache key.

        Returns:
            The cache path.
        """
        # Create a safe filename from the key
        safe_key = re.sub(r"[^a-zA-Z0-9_-]", "_", key)
        safe_key = re.sub(r"_+", "_", safe_key)
        safe_key = safe_key[:100]  # Limit the length

        # Add a hash to ensure uniqueness
        key_hash = hashlib.md5(key.encode()).hexdigest()[:8]

        return os.path.join(self.cache_dir, f"{safe_key}_{key_hash}.json")

    def _get_cached_results(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached results for a key.

        Args:
            key: The cache key.

        Returns:
            The cached results, or None if not found or expired.
        """
        if not self.cache_dir:
            return None

        cache_path = self._get_cache_path(key)

        try:
            # Check if the cache file exists
            if not os.path.exists(cache_path):
                return None

            # Read the cache file
            with open(cache_path, "r") as f:
                cached_data = json.load(f)

            # Check if the cache is expired
            if "timestamp" in cached_data:
                cache_age = int(time.time()) - cached_data["timestamp"]
                if cache_age > self.cache_expiry:
                    logger.debug(f"Cache expired for key: {key}")
                    return None

            return cached_data

        except Exception as e:
            logger.error(f"Error reading cache for key {key}: {str(e)}")
            return None

    def _cache_results(self, key: str, results: Dict[str, Any]) -> bool:
        """Cache results for a key.

        Args:
            key: The cache key.
            results: The results to cache.

        Returns:
            True if successful, False otherwise.
        """
        if not self.cache_dir:
            return False

        cache_path = self._get_cache_path(key)

        try:
            # Ensure the cache directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)

            # Write the cache file
            with open(cache_path, "w") as f:
                json.dump(results, f)

            logger.debug(f"Cached results for key: {key}")
            return True

        except Exception as e:
            logger.error(f"Error caching results for key {key}: {str(e)}")
            return False
