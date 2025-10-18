"""
增强型爬虫引擎 - 支持市场调研和竞品分析
Enhanced Scraper Engine - Support for market research and competitive analysis

功能特性 / Features:
- 周期性采集调度 / Periodic scraping schedule
- User-Agent 轮换 / User-Agent rotation
- 随机延时（2-5秒）/ Random delays (2-5 seconds)
- 错误重试 + 缓存 / Error retry + caching
- 抽样采集策略 / Sampling strategy
- CSV/数据库存储 / CSV/Database storage
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
import csv
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EnhancedScraper:
    """增强型爬虫引擎 / Enhanced Scraper Engine"""
    
    # 扩展的 User-Agent 列表（模拟更多浏览器）
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        # Firefox on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ]
    
    def __init__(self, 
                 cache_dir: str = "data/cache",
                 data_dir: str = "data/enhanced",
                 delay_range: tuple = (2.0, 5.0),
                 max_retries: int = 3,
                 cache_ttl_hours: int = 24):
        """
        初始化增强型爬虫
        
        Args:
            cache_dir: 缓存目录 / Cache directory
            data_dir: 数据目录 / Data directory
            delay_range: 延时范围(秒) / Delay range (seconds)
            max_retries: 最大重试次数 / Max retries
            cache_ttl_hours: 缓存有效期(小时) / Cache TTL (hours)
        """
        self.cache_dir = Path(cache_dir)
        self.data_dir = Path(data_dir)
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # 创建必要的目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化会话
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        logger.info("Enhanced scraper initialized")
    
    def _get_random_user_agent(self) -> str:
        """获取随机 User-Agent / Get random User-Agent"""
        return random.choice(self.USER_AGENTS)
    
    def _random_delay(self, min_delay: float = None, max_delay: float = None):
        """
        随机延时（默认2-5秒）
        Random delay (default 2-5 seconds)
        
        Args:
            min_delay: 最小延时 / Minimum delay
            max_delay: 最大延时 / Maximum delay
        """
        if min_delay is None:
            min_delay = self.delay_range[0]
        if max_delay is None:
            max_delay = self.delay_range[1]
        
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def _get_cache_key(self, url: str) -> str:
        """生成缓存键 / Generate cache key"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径 / Get cache file path"""
        return self.cache_dir / f"{cache_key}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """检查缓存是否有效 / Check if cache is valid"""
        if not cache_path.exists():
            return False
        
        # 检查缓存时间
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - cache_time > self.cache_ttl:
            logger.debug(f"Cache expired: {cache_path}")
            return False
        
        return True
    
    def _get_from_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """从缓存获取数据 / Get data from cache"""
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Cache hit: {url}")
                    return data
            except Exception as e:
                logger.error(f"Error reading cache: {e}")
        
        return None
    
    def _save_to_cache(self, url: str, data: Dict[str, Any]):
        """保存数据到缓存 / Save data to cache"""
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cached: {url}")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def fetch_page(self, url: str, use_cache: bool = True, retries: int = 0) -> Optional[str]:
        """
        获取页面内容（带缓存和重试）
        Fetch page content with cache and retry
        
        Args:
            url: 目标URL / Target URL
            use_cache: 是否使用缓存 / Whether to use cache
            retries: 当前重试次数 / Current retry count
            
        Returns:
            页面HTML内容 / Page HTML content
        """
        # 检查缓存
        if use_cache:
            cached_data = self._get_from_cache(url)
            if cached_data:
                return cached_data.get('html', '')
        
        # 检查重试次数
        if retries >= self.max_retries:
            logger.error(f"Max retries reached for {url}")
            return None
        
        try:
            # 设置随机 User-Agent
            self.session.headers['User-Agent'] = self._get_random_user_agent()
            
            # 随机延时
            if retries > 0:
                self._random_delay(3.0, 6.0)  # 重试时延时更长
            else:
                self._random_delay()
            
            logger.info(f"Fetching: {url} (attempt {retries + 1}/{self.max_retries})")
            
            # 发送请求
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            html = response.text
            
            # 保存到缓存
            if use_cache:
                self._save_to_cache(url, {
                    'html': html,
                    'url': url,
                    'timestamp': datetime.now().isoformat()
                })
            
            return html
            
        except requests.HTTPError as e:
            if e.response.status_code in [403, 429, 503]:
                logger.warning(f"HTTP {e.response.status_code} for {url}, retrying...")
                return self.fetch_page(url, use_cache, retries + 1)
            else:
                logger.error(f"HTTP error {e.response.status_code}: {url}")
                return None
                
        except requests.Timeout:
            logger.warning(f"Timeout for {url}, retrying...")
            return self.fetch_page(url, use_cache, retries + 1)
            
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            if retries < self.max_retries - 1:
                return self.fetch_page(url, use_cache, retries + 1)
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return None
    
    def sample_scrape(self, 
                     urls: List[str], 
                     sample_size: int = 100,
                     use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        抽样采集（从多个URL采集指定数量的商品）
        Sample scraping (collect specified number of products from multiple URLs)
        
        Args:
            urls: URL列表 / URL list
            sample_size: 采样数量 / Sample size
            use_cache: 是否使用缓存 / Whether to use cache
            
        Returns:
            商品数据列表 / Product data list
        """
        all_products = []
        per_url_sample = max(1, sample_size // len(urls))
        
        logger.info(f"Starting sample scrape: {len(urls)} URLs, {sample_size} total samples")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{len(urls)}: {url}")
            
            html = self.fetch_page(url, use_cache)
            if html:
                # 这里需要根据具体平台实现解析逻辑
                # This needs platform-specific parsing logic
                products = self._parse_products(html, url, per_url_sample)
                all_products.extend(products)
            
            # 检查是否已达到目标数量
            if len(all_products) >= sample_size:
                break
        
        # 确保不超过采样数量
        all_products = all_products[:sample_size]
        
        logger.info(f"Sample scrape completed: {len(all_products)} products collected")
        return all_products
    
    def _parse_products(self, html: str, source_url: str, max_items: int) -> List[Dict[str, Any]]:
        """
        解析产品数据（基础实现，应被子类重写）
        Parse product data (basic implementation, should be overridden by subclasses)
        
        Args:
            html: HTML内容 / HTML content
            source_url: 来源URL / Source URL
            max_items: 最大商品数 / Max items
            
        Returns:
            商品列表 / Product list
        """
        # 这是一个基础实现，实际应该根据不同平台实现不同的解析逻辑
        logger.warning("Using basic product parser - should be overridden for specific platforms")
        return []
    
    def save_to_csv(self, products: List[Dict[str, Any]], filename: str = None) -> str:
        """
        保存数据到CSV文件
        Save data to CSV file
        
        Args:
            products: 商品数据列表 / Product data list
            filename: 文件名 / Filename
            
        Returns:
            文件路径 / File path
        """
        if not products:
            logger.warning("No products to save")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"products_{timestamp}.csv"
        
        filepath = self.data_dir / filename
        
        try:
            # 获取所有字段
            fieldnames = set()
            for product in products:
                fieldnames.update(product.keys())
            fieldnames = sorted(fieldnames)
            
            # 写入CSV
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(products)
            
            logger.info(f"Data saved to CSV: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return ""
    
    def save_to_json(self, products: List[Dict[str, Any]], filename: str = None) -> str:
        """
        保存数据到JSON文件
        Save data to JSON file
        
        Args:
            products: 商品数据列表 / Product data list
            filename: 文件名 / Filename
            
        Returns:
            文件路径 / File path
        """
        if not products:
            logger.warning("No products to save")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"products_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'products': products,
                    'total_count': len(products),
                    'scraped_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Data saved to JSON: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return ""
    
    def clear_cache(self, older_than_hours: int = None):
        """
        清理缓存
        Clear cache
        
        Args:
            older_than_hours: 清理多少小时前的缓存 / Clear cache older than hours
        """
        if older_than_hours is None:
            older_than_hours = self.cache_ttl.total_seconds() / 3600
        
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        cleared_count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_time < cutoff_time:
                try:
                    cache_file.unlink()
                    cleared_count += 1
                except Exception as e:
                    logger.error(f"Error deleting cache file {cache_file}: {e}")
        
        logger.info(f"Cleared {cleared_count} cache files older than {older_than_hours} hours")
        return cleared_count
