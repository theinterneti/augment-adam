"""Web Retriever for the Context Engine.

This module provides a retriever for fetching relevant information from
the web.

Version: 0.1.0
Created: 2025-04-26
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional, Union, Tuple
import aiohttp
import asyncio

from augment_adam.core.errors import (
    ResourceError, NetworkError, wrap_error, log_error, ErrorCategory
)
from augment_adam.context_engine.context_manager import ContextItem

logger = logging.getLogger(__name__)


class WebRetriever:
    """Web Retriever for the Context Engine.
    
    This class retrieves relevant information from the web.
    
    Attributes:
        search_api_key: API key for the search engine
        search_engine_id: ID of the search engine
        default_relevance: The default relevance score for retrieved items
        session: aiohttp session for making requests
    """
    
    def __init__(
        self,
        search_api_key: Optional[str] = None,
        search_engine_id: Optional[str] = None,
        default_relevance: float = 0.6
    ):
        """Initialize the Web Retriever.
        
        Args:
            search_api_key: API key for the search engine
            search_engine_id: ID of the search engine
            default_relevance: The default relevance score for retrieved items
        """
        self.search_api_key = search_api_key
        self.search_engine_id = search_engine_id
        self.default_relevance = default_relevance
        self.session = None
        
        logger.info("Web Retriever initialized")
    
    async def _ensure_session(self):
        """Ensure that an aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def _close_session(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search the web for information.
        
        Args:
            query: The query to search for
            max_results: The maximum number of results to return
            
        Returns:
            A list of search results
        """
        await self._ensure_session()
        
        if not self.search_api_key or not self.search_engine_id:
            logger.warning("Search API key or engine ID not provided")
            return []
        
        try:
            # Use Google Custom Search API
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.search_api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(max_results, 10)  # API limit is 10
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Search API returned status {response.status}")
                    return []
                
                data = await response.json()
                items = data.get("items", [])
                
                results = []
                for item in items:
                    result = {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                    }
                    results.append(result)
                
                return results
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to search the web",
                category=ErrorCategory.NETWORK,
                details={"query": query},
            )
            log_error(error, logger=logger)
            return []
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch a web page.
        
        Args:
            url: The URL to fetch
            
        Returns:
            The page content, or None if the fetch failed
        """
        await self._ensure_session()
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: status {response.status}")
                    return None
                
                content = await response.text()
                return content
        except Exception as e:
            error = wrap_error(
                e,
                message=f"Failed to fetch {url}",
                category=ErrorCategory.NETWORK,
                details={"url": url},
            )
            log_error(error, logger=logger)
            return None
    
    async def _extract_text(self, html: str) -> str:
        """Extract text from HTML.
        
        Args:
            html: The HTML content
            
        Returns:
            The extracted text
        """
        # Very simple HTML text extraction
        # In a real implementation, use a proper HTML parser
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    async def _retrieve_async(
        self,
        query: str,
        max_items: int = 5
    ) -> List[ContextItem]:
        """Retrieve context items from the web asynchronously.
        
        Args:
            query: The query to retrieve context for
            max_items: The maximum number of items to retrieve
            
        Returns:
            The retrieved context items
        """
        try:
            # Search the web
            search_results = await self._search(query, max_items)
            
            # Fetch and process pages
            items = []
            for result in search_results:
                url = result.get("link")
                if not url:
                    continue
                
                # Fetch page
                html = await self._fetch_page(url)
                if not html:
                    continue
                
                # Extract text
                text = await self._extract_text(html)
                if not text:
                    continue
                
                # Create snippet with title and text
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                content = f"{title}\n\n{snippet}\n\n{text[:1000]}..."  # Limit text length
                
                # Estimate token count (very rough approximation)
                token_count = len(content.split()) * 1.3  # Rough approximation
                
                # Create context item
                item = ContextItem(
                    content=content,
                    source="web",
                    relevance=self.default_relevance,
                    metadata={
                        "url": url,
                        "title": title,
                    },
                    token_count=int(token_count)
                )
                items.append(item)
            
            # Close session
            await self._close_session()
            
            logger.info(f"Retrieved {len(items)} items from web for query: {query}")
            return items
        except Exception as e:
            error = wrap_error(
                e,
                message="Failed to retrieve from web",
                category=ErrorCategory.NETWORK,
                details={"query": query},
            )
            log_error(error, logger=logger)
            return []
    
    def retrieve(
        self,
        query: str,
        max_items: int = 5
    ) -> List[ContextItem]:
        """Retrieve context items from the web.
        
        Args:
            query: The query to retrieve context for
            max_items: The maximum number of items to retrieve
            
        Returns:
            The retrieved context items
        """
        # Run the async method in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._retrieve_async(query, max_items))
        finally:
            loop.close()
