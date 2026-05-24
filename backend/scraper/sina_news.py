"""Sina News scraper."""
import json
import re
from datetime import datetime, timezone
from .base import BaseScraper


class SinaNewsScraper(BaseScraper):
    """Scrape hot news from Sina (新浪新闻)."""

    def __init__(self):
        super().__init__("SinaNews", "https://news.sina.com.cn")

    async def scrape(self) -> list[dict]:
        items = []

        # Sina hot list API
        api_url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&k=&num=20&page=1&r=0.5"

        try:
            content = await self.fetch(api_url)
            if content:
                data = json.loads(content)
                list_data = data.get("result", {}).get("data", [])

                for i, item in enumerate(list_data[:20], 1):
                    title = item.get("title", "").strip()
                    if not title:
                        continue

                    keywords_raw = item.get("keywords", "") or ""
                    keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]

                    pub_time = item.get("ctime", "")
                    if pub_time:
                        try:
                            dt = datetime.fromtimestamp(int(pub_time), tz=timezone.utc)
                            pub_time = dt.strftime("%Y-%m-%dT%H:%M:%S")
                        except Exception:
                            pub_time = ""

                    items.append({
                        "rank": i,
                        "title": title,
                        "source": "新浪新闻",
                        "source_url": item.get("url", ""),
                        "publish_time": pub_time,
                        "summary": item.get("intro", "")[:150] or title,
                        "keywords": keywords[:5],
                        "heat_score": max(0, 10000 - i * 400),
                    })
        except Exception as e:
            print(f"[SinaNews] Parse error: {e}")

        return items
