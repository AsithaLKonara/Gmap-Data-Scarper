"""Async scraping utilities for parallel HTTP requests."""
from __future__ import annotations

import asyncio
from typing import List, Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from scrapers.social_common import HttpClient


class AsyncScraper:
    """
    Async scraper for parallel HTTP-based scraping.
    
    Note: Selenium-based scrapers (Google Maps) should remain sequential.
    """
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize async scraper.
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def scrape_batch(
        self,
        urls: List[str],
        scrape_func: Callable[[str], Any],
        delay_seconds: float = 1.0
    ) -> List[Any]:
        """
        Scrape multiple URLs in parallel.
        
        Args:
            urls: List of URLs to scrape
            scrape_func: Function to call for each URL
            delay_seconds: Delay between requests
            
        Returns:
            List of results
        """
        loop = asyncio.get_event_loop()
        
        async def scrape_with_delay(url: str) -> Any:
            await asyncio.sleep(delay_seconds)
            return await loop.run_in_executor(self.executor, scrape_func, url)
        
        tasks = [scrape_with_delay(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        return [r for r in results if not isinstance(r, Exception)]
    
    def close(self) -> None:
        """Close the executor."""
        self.executor.shutdown(wait=True)


class TaskQueue:
    """Simple task queue for managing scraping tasks."""
    
    def __init__(self, max_size: int = 100):
        """
        Initialize task queue.
        
        Args:
            max_size: Maximum queue size
        """
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.max_size = max_size
    
    async def put(self, task: Any) -> None:
        """Add task to queue."""
        await self.queue.put(task)
    
    async def get(self) -> Any:
        """Get task from queue."""
        return await self.queue.get()
    
    def size(self) -> int:
        """Get current queue size."""
        return self.queue.qsize()
    
    def is_full(self) -> bool:
        """Check if queue is full."""
        return self.queue.qsize() >= self.max_size

