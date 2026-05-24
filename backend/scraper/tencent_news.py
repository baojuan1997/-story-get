"""Tencent News scraper."""
import json
import re
from datetime import datetime, timezone
from .base import BaseScraper


class TencentNewsScraper(BaseScraper):
    """Scrape hot news from Tencent (腾讯新闻)."""

    def __init__(self):
        super().__init__("TencentNews", "https://news.qq.com")

    async def scrape(self) -> list[dict]:
        items = []

        # Tencent hot search API
        api_url = "https://hot嫌隙-search-pc.ms汽dservice.com/hot/sync/digital?query=热搜&cursor=0&pageSize=20"

        try:
            # Try Tencent's official hot list
            client = await self.get_client()
            response = await client.get(
                "https://pacaio.gitlab.com/qq/qqnews/lists.json",
                timeout=15.0,
            )
            if response.status_code == 200:
                data = response.json()
                list_data = data.get("digitals", [])[:20]

                for i, item in enumerate(list_data, 1):
                    title = item.get("title", "").strip()
                    if not title:
                        continue

                    items.append({
                        "rank": i,
                        "title": title,
                        "source": "腾讯新闻",
                        "source_url": item.get("url", ""),
                        "publish_time": item.get("datetime", ""),
                        "summary": item.get("desc", "")[:150] or title,
                        "keywords": item.get("tags", [])[:5],
                        "heat_score": max(0, 9500 - i * 450),
                    })
        except Exception as e:
            print(f"[TencentNews] Primary API error: {e}")

        # Fallback: try alternative endpoint
        if not items:
            try:
                content = await self.fetch(
                    "https://pacaio.gitlab.com/qq/qqnews/lists.json"
                )
                if content:
                    data = json.loads(content)
                    for i, item in enumerate(data.get("digitals", [])[:20], 1):
                        title = item.get("title", "").strip()
                        if not title:
                            continue
                        items.append({
                            "rank": i,
                            "title": title,
                            "source": "腾讯新闻",
                            "source_url": item.get("url", ""),
                            "publish_time": item.get("datetime", ""),
                            "summary": item.get("desc", "")[:150] or title,
                            "keywords": item.get("tags", [])[:5],
                            "heat_score": max(0, 9500 - i * 450),
                        })
            except Exception as e:
                print(f"[TencentNews] Fallback error: {e}")

        return items
