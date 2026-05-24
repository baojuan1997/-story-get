"""News scraper module."""
from .base import BaseScraper
from .sina_news import SinaNewsScraper
from .tencent_news import TencentNewsScraper
from .weibo_hot import WeiboHotScraper

__all__ = ["BaseScraper", "SinaNewsScraper", "TencentNewsScraper", "WeiboHotScraper"]
