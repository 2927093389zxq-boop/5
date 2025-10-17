"""
Amazon 爬虫模块 - 实现真实的Amazon数据采集
Amazon Scraper Module - Real Amazon data collection implementation

支持功能 / Features:
- 商品列表页采集 / Product list page scraping
- 商品详情页采集 / Product detail page scraping  
- 多种选择器策略 / Multiple selector strategies
- 数据持久化存储 / Data persistence
- 自动重试机制 / Auto retry mechanism
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from scrapers.logger import log_info, log_error, log_warning

# === AUTO_TUNING_CONFIG_START ===
# 这个配置块会被自迭代引擎动态调整
# This config block will be dynamically adjusted by auto-iteration engine

SELECTORS = {
    "list_selectors": [
        "div.s-result-item",
        "div[data-asin][data-component-type='s-search-result']",
        "div.zg-grid-general-faceout",
        "div.p13n-sc-uncoverable-faceout"
    ],
    "title_selectors": [
        "span.a-size-medium",
        "h2 a span",
        "div.p13n-sc-truncated",
        "img"
    ],
    "price_selectors": [
        "span.a-price-whole",
        "span.p13n-sc-price",
        "span.a-offscreen"
    ],
    "rating_selectors": [
        "span.a-icon-alt",
        "i.a-icon-star span"
    ],
    "review_count_selectors": [
        "span.a-size-base",
        "div.a-row.a-size-small span"
    ]
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

WAIT_TIME = {"min": 1.0, "max": 2.0}
MAX_RETRIES = 3
SCROLL_CYCLES = 3
# === AUTO_TUNING_CONFIG_END ===


class AmazonScraper:
    """Amazon爬虫核心类 / Amazon Scraper Core Class"""
    
    def __init__(self, data_dir: str = "data/amazon"):
        """
        初始化爬虫
        Initialize scraper
        
        Args:
            data_dir: 数据存储目录 / Data storage directory
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent / Get random User-Agent"""
        return random.choice(USER_AGENTS)
    
    def _wait(self):
        """随机等待 / Random wait"""
        wait_time = random.uniform(WAIT_TIME["min"], WAIT_TIME["max"])
        time.sleep(wait_time)
    
    def _fetch_page(self, url: str, retries: int = 0) -> Optional[BeautifulSoup]:
        """
        获取页面内容
        Fetch page content
        
        Args:
            url: 目标URL / Target URL
            retries: 重试次数 / Retry count
            
        Returns:
            BeautifulSoup对象或None / BeautifulSoup object or None
        """
        if retries >= MAX_RETRIES:
            log_error(f"达到最大重试次数 / Max retries reached: {url}")
            return None
        
        try:
            self.session.headers['User-Agent'] = self._get_random_user_agent()
            log_info(f"正在获取页面 / Fetching page: {url}")
            
            start_time = time.time()
            response = self.session.get(url, timeout=30)
            elapsed = time.time() - start_time
            log_info(f"[LIST_TIME] secs={elapsed:.2f}")
            
            if response.status_code == 503:
                log_warning(f"检测到验证码或限流 / Captcha or rate limit detected: {url}")
                self._wait()
                return self._fetch_page(url, retries + 1)
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # 检测验证码页面 / Check for captcha page
            if soup.find('form', {'action': '/errors/validateCaptcha'}):
                log_warning("检测到Amazon验证码页面 / Amazon captcha page detected")
                self._wait()
                return self._fetch_page(url, retries + 1)
            
            return soup
            
        except requests.RequestException as e:
            log_error(f"[ERROR] 请求失败 / Request failed: {url} - {e}")
            if retries < MAX_RETRIES - 1:
                self._wait()
                return self._fetch_page(url, retries + 1)
            return None
        except Exception as e:
            log_error(f"[EXCEPTION] 页面解析异常 / Page parsing exception: {e}")
            return None
    
    def _extract_text(self, item, selectors: List[str], attr: str = None) -> str:
        """
        使用多个选择器提取文本
        Extract text using multiple selectors
        
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
    
    def _extract_price(self, item) -> str:
        """
        提取价格信息
        Extract price information
        
        Args:
            item: BeautifulSoup元素 / BeautifulSoup element
            
        Returns:
            价格字符串 / Price string
        """
        price_text = self._extract_text(item, SELECTORS["price_selectors"])
        if not price_text and item.select_one('span.a-price'):
            # 尝试组合价格 / Try to combine price
            whole = item.select_one('span.a-price-whole')
            fraction = item.select_one('span.a-price-fraction')
            if whole:
                price_text = whole.get_text(strip=True)
                if fraction:
                    price_text += fraction.get_text(strip=True)
        return price_text
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """
        采集列表页商品
        Scrape product list page
        
        Args:
            url: 列表页URL / List page URL
            max_items: 最大商品数 / Maximum items
            
        Returns:
            商品列表 / Product list
        """
        log_info(f"开始采集列表页 / Starting list page scraping: {url}")
        
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        
        # 尝试不同的选择器 / Try different selectors
        for selector in SELECTORS["list_selectors"]:
            items = soup.select(selector)
            if items:
                log_info(f"使用选择器找到 {len(items)} 个商品 / Found {len(items)} items with selector: {selector}")
                
                for idx, item in enumerate(items[:max_items]):
                    try:
                        # 提取ASIN / Extract ASIN
                        asin = item.get('data-asin', '')
                        if not asin or asin == '':
                            continue
                        
                        # 提取标题 / Extract title
                        title = self._extract_text(item, SELECTORS["title_selectors"])
                        if not title:
                            title = self._extract_text(item, SELECTORS["title_selectors"], attr='alt')
                        
                        # 提取价格 / Extract price
                        price = self._extract_price(item)
                        
                        # 提取评分 / Extract rating
                        rating = self._extract_text(item, SELECTORS["rating_selectors"])
                        
                        # 提取评论数 / Extract review count
                        review_count = self._extract_text(item, SELECTORS["review_count_selectors"])
                        
                        # 构造商品URL / Construct product URL
                        product_url = f"https://www.amazon.com/dp/{asin}"
                        
                        product = {
                            "asin": asin,
                            "title": title,
                            "price": price,
                            "rating": rating,
                            "review_count": review_count,
                            "url": product_url,
                            "scraped_at": datetime.now(timezone.utc).isoformat(),
                            "source_url": url
                        }
                        
                        products.append(product)
                        
                    except Exception as e:
                        log_error(f"[ERROR] 提取商品信息失败 / Failed to extract product info: {e}")
                        continue
                
                if products:
                    break  # 如果找到商品就停止尝试其他选择器 / Stop if products found
        
        log_info(f"列表页采集完成，共 {len(products)} 个商品 / List page scraping completed, {len(products)} products")
        
        # 如果没有商品，记录零结果页面 / Log zero result page if no products
        if len(products) == 0:
            log_warning(f"零结果页面 / Zero result page: {url}")
        
        return products
    
    def scrape_product_detail(self, asin: str) -> Dict[str, Any]:
        """
        采集商品详情
        Scrape product detail
        
        Args:
            asin: 商品ASIN / Product ASIN
            
        Returns:
            商品详情 / Product detail
        """
        url = f"https://www.amazon.com/dp/{asin}"
        log_info(f"开始采集商品详情 / Starting product detail scraping: {asin}")
        
        soup = self._fetch_page(url)
        if not soup:
            return {}
        
        detail = {
            "asin": asin,
            "url": url,
            "scraped_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # 提取标题 / Extract title
            title_elem = soup.select_one('span#productTitle')
            if title_elem:
                detail['title'] = title_elem.get_text(strip=True)
            
            # 提取价格 / Extract price
            price_elem = soup.select_one('span.a-price span.a-offscreen')
            if price_elem:
                detail['price'] = price_elem.get_text(strip=True)
            
            # 提取评分 / Extract rating
            rating_elem = soup.select_one('span.a-icon-alt')
            if rating_elem:
                detail['rating'] = rating_elem.get_text(strip=True)
            
            # 提取评论数 / Extract review count
            review_elem = soup.select_one('span#acrCustomerReviewText')
            if review_elem:
                detail['review_count'] = review_elem.get_text(strip=True)
            
            # 提取描述 / Extract description
            desc_elem = soup.select_one('div#feature-bullets')
            if desc_elem:
                bullets = desc_elem.select('span.a-list-item')
                detail['description'] = [b.get_text(strip=True) for b in bullets]
            
            # 提取品牌 / Extract brand
            brand_elem = soup.select_one('a#bylineInfo')
            if brand_elem:
                detail['brand'] = brand_elem.get_text(strip=True)
            
        except Exception as e:
            log_error(f"[EXCEPTION] 提取详情失败 / Failed to extract detail: {e}")
        
        return detail
    
    def save_data(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        保存数据到JSON文件
        Save data to JSON file
        
        Args:
            data: 商品数据列表 / Product data list
            filename: 文件名(可选) / Filename (optional)
            
        Returns:
            保存的文件路径 / Saved file path
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"amazon_products_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "items": data,
                    "total_count": len(data),
                    "scraped_at": datetime.now(timezone.utc).isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            log_info(f"数据已保存 / Data saved: {filepath}")
            return filepath
            
        except Exception as e:
            log_error(f"[ERROR] 保存数据失败 / Failed to save data: {e}")
            return ""
    
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
        # 采集列表页 / Scrape list page
        products = self.scrape_list_page(url, max_items)
        
        # 如果需要详情，采集每个商品的详情 / Scrape details if needed
        if deep_detail and products:
            log_info(f"开始采集 {len(products)} 个商品的详情 / Starting detail scraping for {len(products)} products")
            for i, product in enumerate(products[:10]):  # 限制详情采集数量 / Limit detail scraping
                self._wait()
                detail = self.scrape_product_detail(product['asin'])
                product.update(detail)
                log_info(f"详情采集进度 / Detail scraping progress: {i+1}/{min(len(products), 10)}")
        
        # 保存数据 / Save data
        if products:
            self.save_data(products)
        
        return products


def scrape_amazon(url: str, max_items: int = 50, deep_detail: bool = False) -> List[Dict[str, Any]]:
    """
    便捷函数：采集Amazon数据
    Convenience function: Scrape Amazon data
    
    Args:
        url: 目标URL / Target URL
        max_items: 最大商品数 / Maximum items
        deep_detail: 是否采集详情 / Whether to scrape detail
        
    Returns:
        商品列表 / Product list
    """
    scraper = AmazonScraper()
    return scraper.run(url, max_items, deep_detail)


if __name__ == "__main__":
    # 测试示例 / Test example
    test_url = "https://www.amazon.com/s?k=laptop"
    products = scrape_amazon(test_url, max_items=20, deep_detail=False)
    print(f"采集到 {len(products)} 个商品 / Scraped {len(products)} products")
