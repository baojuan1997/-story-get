"""Base scraper class for news sources."""
import httpx
import asyncio
from abc import ABC, abstractmethod
from typing import Optional


class BaseScraper(ABC):
    """Base class for all news scrapers."""

    def __init__(self, name: str, base_url: str = ""):
        self.name = name
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept": "application/json, text/html, */*",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                },
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch a URL and return the text content."""
        try:
            client = await self.get_client()
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[{self.name}] Fetch error for {url}: {e}")
            return None

    @abstractmethod
    async def scrape(self) -> list[dict]:
        """Scrape and return a list of hot items as dicts."""
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
