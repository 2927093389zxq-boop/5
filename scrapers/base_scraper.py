"""
基础爬虫模块 - 为所有平台提供统一的基础类
Base Scraper Module - Unified base class for all platforms
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from scrapers.logger import log_info, log_error, log_warning


class BaseScraper(ABC):
    """基础爬虫类 - 所有平台爬虫的抽象基类 / Base Scraper - Abstract base class for all platform scrapers"""
    
    # 平台名称，由子类重写 / Platform name, overridden by subclasses
    PLATFORM_NAME = "base"
    
    # 默认用户代理列表 / Default User-Agent list
    DEFAULT_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    
    # 默认等待时间配置 / Default wait time configuration
    DEFAULT_WAIT_TIME = {"min": 1.0, "max": 2.5}
    
    # 默认最大重试次数 / Default max retries
    DEFAULT_MAX_RETRIES = 3
    
    def __init__(self, data_dir: str = None):
        """
        初始化爬虫
        Initialize scraper
        
        Args:
            data_dir: 数据存储目录 / Data storage directory
        """
        if data_dir is None:
            data_dir = f"data/{self.PLATFORM_NAME}"
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # 允许子类自定义配置 / Allow subclass to customize config
        self.user_agents = self.DEFAULT_USER_AGENTS
        self.wait_time = self.DEFAULT_WAIT_TIME.copy()
        self.max_retries = self.DEFAULT_MAX_RETRIES
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent / Get random User-Agent"""
        return random.choice(self.user_agents)
    
    def _wait(self, min_time: float = None, max_time: float = None):
        """
        随机等待 / Random wait
        
        Args:
            min_time: 最小等待时间 / Minimum wait time
            max_time: 最大等待时间 / Maximum wait time
        """
        if min_time is None:
            min_time = self.wait_time["min"]
        if max_time is None:
            max_time = self.wait_time["max"]
        wait_time = random.uniform(min_time, max_time)
        time.sleep(wait_time)
    
    def _fetch_page(self, url: str, retries: int = 0, timeout: int = 30) -> Optional[BeautifulSoup]:
        """
        获取页面内容（带重试机制）
        Fetch page content with retry mechanism
        
        Args:
            url: 目标URL / Target URL
            retries: 当前重试次数 / Current retry count
            timeout: 超时时间 / Timeout
            
        Returns:
            BeautifulSoup对象或None / BeautifulSoup object or None
        """
        if retries >= self.max_retries:
            log_error(f"[{self.PLATFORM_NAME}] 达到最大重试次数 / Max retries reached: {url}")
            return None
        
        try:
            self.session.headers['User-Agent'] = self._get_random_user_agent()
            log_info(f"[{self.PLATFORM_NAME}] 正在获取页面 / Fetching page: {url}")
            
            start_time = time.time()
            response = self.session.get(url, timeout=timeout)
            elapsed = time.time() - start_time
            log_info(f"[{self.PLATFORM_NAME}] [LIST_TIME] secs={elapsed:.2f}")
            
            # 处理常见HTTP状态码 / Handle common HTTP status codes
            if response.status_code == 503:
                log_warning(f"[{self.PLATFORM_NAME}] 检测到限流或验证码 / Rate limit or captcha detected")
                self._wait(3.0, 5.0)
                return self._fetch_page(url, retries + 1, timeout)
            
            if response.status_code == 403:
                log_warning(f"[{self.PLATFORM_NAME}] 访问被拒绝，可能需要更换User-Agent / Access denied")
                self._wait(2.0, 4.0)
                return self._fetch_page(url, retries + 1, timeout)
            
            response.raise_for_status()
            
            # 使用lxml解析器提高速度 / Use lxml parser for better speed
            soup = BeautifulSoup(response.content, 'lxml')
            
            # 检测验证码页面（平台特定） / Detect captcha page (platform-specific)
            if self._is_captcha_page(soup):
                log_warning(f"[{self.PLATFORM_NAME}] 检测到验证码页面 / Captcha page detected")
                self._wait(5.0, 8.0)
                return self._fetch_page(url, retries + 1, timeout)
            
            return soup
            
        except requests.Timeout:
            log_error(f"[{self.PLATFORM_NAME}] [ERROR] 请求超时 / Request timeout: {url}")
            if retries < self.max_retries - 1:
                self._wait()
                return self._fetch_page(url, retries + 1, timeout)
            return None
            
        except requests.RequestException as e:
            log_error(f"[{self.PLATFORM_NAME}] [ERROR] 请求失败 / Request failed: {url} - {e}")
            if retries < self.max_retries - 1:
                self._wait()
                return self._fetch_page(url, retries + 1, timeout)
            return None
            
        except Exception as e:
            log_error(f"[{self.PLATFORM_NAME}] [EXCEPTION] 页面解析异常 / Page parsing exception: {e}")
            return None
    
    def _is_captcha_page(self, soup: BeautifulSoup) -> bool:
        """
        检测是否为验证码页面（子类可重写）
        Detect if page is a captcha page (can be overridden by subclasses)
        
        Args:
            soup: BeautifulSoup对象 / BeautifulSoup object
            
        Returns:
            是否为验证码页面 / Whether it's a captcha page
        """
        # 子类可以重写此方法以实现平台特定的验证码检测
        # Subclasses can override this method for platform-specific captcha detection
        return False
    
    def _extract_text(self, item, selectors: List[str], attr: str = None) -> str:
        """
        使用多个选择器提取文本（降级策略）
        Extract text using multiple selectors (fallback strategy)
        
        Args:
            item: BeautifulSoup元素 / BeautifulSoup element
            selectors: 选择器列表 / Selector list
            attr: 属性名(用于提取属性值) / Attribute name (for extracting attribute value)
            
        Returns:
            提取的文本 / Extracted text
        """
        for selector in selectors:
            try:
                element = item.select_one(selector)
                if element:
                    if attr:
                        value = element.get(attr, '').strip()
                        if value:
                            return value
                    else:
                        text = element.get_text(strip=True)
                        if text:
                            return text
            except Exception:
                continue
        return ""
    
    def save_data(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        保存数据到JSON文件
        Save data to JSON file
        
        Args:
            data: 数据列表 / Data list
            filename: 文件名(可选) / Filename (optional)
            
        Returns:
            保存的文件路径 / Saved file path
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.PLATFORM_NAME}_products_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "platform": self.PLATFORM_NAME,
                    "items": data,
                    "total_count": len(data),
                    "scraped_at": datetime.now(timezone.utc).isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            log_info(f"[{self.PLATFORM_NAME}] 数据已保存 / Data saved: {filepath}")
            return filepath
            
        except Exception as e:
            log_error(f"[{self.PLATFORM_NAME}] [ERROR] 保存数据失败 / Failed to save data: {e}")
            return ""
    
    @abstractmethod
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """
        采集列表页（抽象方法，必须由子类实现）
        Scrape list page (abstract method, must be implemented by subclasses)
        
        Args:
            url: 列表页URL / List page URL
            max_items: 最大商品数 / Maximum items
            
        Returns:
            商品列表 / Product list
        """
        pass
    
    def scrape_product_detail(self, product_id: str) -> Dict[str, Any]:
        """
        采集商品详情（可选实现）
        Scrape product detail (optional implementation)
        
        Args:
            product_id: 商品ID / Product ID
            
        Returns:
            商品详情 / Product detail
        """
        # 默认实现返回空字典，子类可以重写
        # Default implementation returns empty dict, subclasses can override
        return {}
    
    def run(self, url: str, max_items: int = 50, deep_detail: bool = False) -> List[Dict[str, Any]]:
        """
        运行完整的采集流程
        Run complete scraping workflow
        
        Args:
            url: 目标URL / Target URL
            max_items: 最大商品数 / Maximum items
            deep_detail: 是否采集详情 / Whether to scrape detail
            
        Returns:
            商品列表 / Product list
        """
        log_info(f"[{self.PLATFORM_NAME}] 开始采集 / Starting scraping: {url}")
        
        # 采集列表页 / Scrape list page
        products = self.scrape_list_page(url, max_items)
        
        # 如果需要详情，采集每个商品的详情 / Scrape details if needed
        if deep_detail and products:
            log_info(f"[{self.PLATFORM_NAME}] 开始采集详情 / Starting detail scraping for {len(products)} products")
            detail_limit = min(len(products), 10)  # 限制详情采集数量 / Limit detail scraping
            for i, product in enumerate(products[:detail_limit]):
                self._wait()
                product_id = product.get('id', product.get('asin', ''))
                if product_id:
                    detail = self.scrape_product_detail(product_id)
                    product.update(detail)
                log_info(f"[{self.PLATFORM_NAME}] 详情采集进度 / Detail progress: {i+1}/{detail_limit}")
        
        # 保存数据 / Save data
        if products:
            self.save_data(products)
        else:
            log_warning(f"[{self.PLATFORM_NAME}] 零结果 / Zero results: {url}")
        
        log_info(f"[{self.PLATFORM_NAME}] 采集完成，共 {len(products)} 个商品 / Completed, {len(products)} products")
        return products
