"""Enhanced async scraper service with httpx and connection pooling."""
import asyncio
from typing import List, Callable, Any, Optional, Dict
import httpx
from backend.utils.retry import retry


class AsyncScraperService:
    """
    Enhanced async scraper using httpx for parallel HTTP requests.
    Supports connection pooling, request batching, and retry logic.
    """
    
    def __init__(
        self,
        max_concurrent: int = 5,
        timeout: float = 30.0,
        max_connections: int = 100
    ):
        """
        Initialize async scraper service.
        
        Args:
            max_concurrent: Maximum concurrent requests per platform
            timeout: Request timeout in seconds
            max_connections: Maximum connections in pool
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.max_connections = max_connections
        self.client: Optional[httpx.AsyncClient] = None
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def __aenter__(self):
        """Async context manager entry."""
        limits = httpx.Limits(
            max_keepalive_connections=self.max_connections,
            max_connections=self.max_connections
        )
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=limits,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def scrape_batch(
        self,
        urls: List[str],
        scrape_func: Callable[[str, httpx.AsyncClient], Any],
        delay_seconds: float = 1.0,
        batch_size: Optional[int] = None
    ) -> List[Any]:
        """
        Scrape multiple URLs in parallel with concurrency control.
        
        Args:
            urls: List of URLs to scrape
            scrape_func: Async function to call for each URL
            delay_seconds: Delay between batches
            batch_size: Number of URLs per batch (None = all at once)
        
        Returns:
            List of results
        """
        if not self.client:
            raise RuntimeError("AsyncScraperService must be used as async context manager")
        
        if batch_size:
            # Process in batches
            results = []
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                batch_results = await self._scrape_batch_internal(batch, scrape_func)
                results.extend(batch_results)
                if i + batch_size < len(urls):
                    await asyncio.sleep(delay_seconds)
            return results
        else:
            return await self._scrape_batch_internal(urls, scrape_func)
    
    async def _scrape_batch_internal(
        self,
        urls: List[str],
        scrape_func: Callable[[str, httpx.AsyncClient], Any]
    ) -> List[Any]:
        """Internal batch scraping with semaphore control."""
        tasks = []
        for url in urls:
            task = self._scrape_with_semaphore(url, scrape_func)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                # Log exception but continue
                continue
            valid_results.append(result)
        
        return valid_results
    
    async def _scrape_with_semaphore(
        self,
        url: str,
        scrape_func: Callable[[str, httpx.AsyncClient], Any]
    ) -> Any:
        """Scrape with semaphore to limit concurrency."""
        async with self._semaphore:
            return await self._retry_scrape(url, scrape_func)
    
    @retry(attempts=3, delay=1, backoff=2, exceptions=(httpx.RequestError, httpx.HTTPStatusError))
    async def _retry_scrape(
        self,
        url: str,
        scrape_func: Callable[[str, httpx.AsyncClient], Any]
    ) -> Any:
        """Scrape with retry logic."""
        return await scrape_func(url, self.client)
    
    async def fetch_url(self, url: str, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        Fetch a single URL using the shared client.
        
        Args:
            url: URL to fetch
            headers: Optional headers
        
        Returns:
            httpx.Response object
        """
        if not self.client:
            raise RuntimeError("AsyncScraperService must be used as async context manager")
        
        async with self._semaphore:
            return await self.client.get(url, headers=headers or {})
    
    async def fetch_batch(
        self,
        urls: List[str],
        headers: Optional[Dict[str, str]] = None
    ) -> List[httpx.Response]:
        """
        Fetch multiple URLs in parallel.
        
        Args:
            urls: List of URLs to fetch
            headers: Optional headers
        
        Returns:
            List of httpx.Response objects
        """
        if not self.client:
            raise RuntimeError("AsyncScraperService must be used as async context manager")
        
        async def fetch_one(url: str) -> httpx.Response:
            return await self.fetch_url(url, headers)
        
        tasks = [fetch_one(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_responses = []
        for response in responses:
            if isinstance(response, httpx.Response):
                valid_responses.append(response)
        
        return valid_responses


# Global instance (should be created per request/context)
_async_scraper: Optional[AsyncScraperService] = None

async def get_async_scraper() -> AsyncScraperService:
    """Get or create global async scraper instance (for use in async context)."""
    global _async_scraper
    if _async_scraper is None:
        _async_scraper = AsyncScraperService()
    return _async_scraper

