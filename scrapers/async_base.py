"""Async base scraper for HTTP-based platforms."""
from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any, Optional
import httpx
import asyncio
from typing import List


class AsyncBaseScraper(ABC):
    """Base class for async HTTP-based scrapers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Platform name."""
        pass
    
    def __init__(self, max_concurrent: int = 5, timeout: int = 30):
        """
        Initialize async scraper.
        
        Args:
            max_concurrent: Maximum concurrent requests
            timeout: Request timeout in seconds
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(max_connections=self.max_concurrent, max_keepalive_connections=5),
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    @abstractmethod
    async def search_async(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> Iterable[Dict[str, Any]]:
        """
        Async search implementation.
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Yields:
            Result dictionaries
        """
        pass
    
    async def search_batch_async(
        self,
        queries: List[str],
        max_results_per_query: Optional[int] = None
    ) -> Iterable[Dict[str, Any]]:
        """
        Search multiple queries concurrently.
        
        Args:
            queries: List of search queries
            max_results_per_query: Maximum results per query
        
        Yields:
            Result dictionaries from all queries
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def search_with_semaphore(q: str):
            async with semaphore:
                async for result in self.search_async(q, max_results_per_query):
                    yield result
        
        # Create tasks for all queries
        tasks = [search_with_semaphore(q) for q in queries]
        
        # Process results as they come
        for task in asyncio.as_completed([self._gather_results(t) for t in tasks]):
            results = await task
            for result in results:
                yield result
    
    async def _gather_results(self, async_gen):
        """Gather all results from async generator."""
        results = []
        async for result in async_gen:
            results.append(result)
        return results
    
    def platform_name(self) -> str:
        """Get platform name."""
        return self.name

