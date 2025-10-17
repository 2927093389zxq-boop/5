# Scrapers Package
# 爬虫模块包

"""
Scrapers package - Multi-platform web scraping support
"""

from scrapers.amazon_scraper import AmazonScraper, scrape_amazon
from scrapers.base_scraper import BaseScraper
from scrapers.multi_platform_scraper import (
    PLATFORM_SCRAPERS,
    get_scraper,
    scrape_platform,
)

__all__ = [
    'AmazonScraper',
    'scrape_amazon',
    'BaseScraper',
    'PLATFORM_SCRAPERS',
    'get_scraper',
    'scrape_platform',
]
