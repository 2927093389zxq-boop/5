#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Amazon 爬虫程序 - 完整的Amazon数据采集解决方案
Amazon Crawler - Complete Amazon Data Collection Solution

功能特点 / Features:
- 支持搜索结果页、商品详情页、评论页的采集
- 命令行参数支持，灵活配置
- 自动重试和错误处理
- 数据持久化存储
- 多种选择器策略，适应Amazon页面变化
- 批量URL处理支持
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# === 配置部分 / Configuration ===
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
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
]

class Logger:
    """简单的日志类 / Simple logger class"""
    
    @staticmethod
    def info(message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[INFO] {timestamp} - {message}")
    
    @staticmethod
    def error(message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR] {timestamp} - {message}")
    
    @staticmethod
    def warning(message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARNING] {timestamp} - {message}")

logger = Logger()

class AmazonCrawler:
    """Amazon爬虫核心类 / Amazon Crawler Core Class"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化爬虫
        Initialize crawler
        
        Args:
            config: 配置字典 / Configuration dictionary
        """
        # 默认配置 / Default config
        self.config = {
            "data_dir": "data/amazon",
            "min_wait_time": 1.0,
            "max_wait_time": 3.0,
            "max_retries": 3,
            "timeout": 30,
            "proxy": None,
            "headers": {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        }
        
        # 更新配置 / Update config
        if config:
            self.config.update(config)
        
        # 创建数据目录 / Create data directory
        os.makedirs(self.config["data_dir"], exist_ok=True)
        
        # 初始化会话 / Initialize session
        self.session = requests.Session()
        self.session.headers.update(self.config["headers"])
        
        # 设置代理 / Set proxy
        if self.config["proxy"]:
            self.session.proxies = {
                "http": self.config["proxy"],
                "https": self.config["proxy"]
            }
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent / Get random User-Agent"""
        return random.choice(USER_AGENTS)
    
    def _wait(self):
        """随机等待 / Random wait"""
        wait_time = random.uniform(self.config["min_wait_time"], self.config["max_wait_time"])
        logger.info(f"等待 {wait_time:.2f} 秒...")
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
        if retries >= self.config["max_retries"]:
            logger.error(f"达到最大重试次数 / Max retries reached: {url}")
            return None
        
        try:
            self.session.headers['User-Agent'] = self._get_random_user_agent()
            logger.info(f"正在获取页面 / Fetching page: {url}")
            
            start_time = time.time()
            response = self.session.get(url, timeout=self.config["timeout"])
            elapsed = time.time() - start_time
            logger.info(f"页面获取耗时: {elapsed:.2f} 秒")
            
            if response.status_code == 503:
                logger.warning(f"检测到验证码或限流 / Captcha or rate limit detected: {url}")
                self._wait()
                return self._fetch_page(url, retries + 1)
            
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            # 检测验证码页面 / Check for captcha page
            if soup.find('form', {'action': '/errors/validateCaptcha'}):
                logger.warning("检测到Amazon验证码页面 / Amazon captcha page detected")
                self._wait()
                return self._fetch_page(url, retries + 1)
            
            return soup
            
        except requests.RequestException as e:
            logger.error(f"请求失败 / Request failed: {url} - {e}")
            if retries < self.config["max_retries"] - 1:
                logger.info(f"准备重试，剩余重试次数: {self.config['max_retries'] - retries - 1}")
                self._wait()
                return self._fetch_page(url, retries + 1)
            return None
        except Exception as e:
            logger.error(f"页面解析异常 / Page parsing exception: {e}")
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
        logger.info(f"开始采集列表页 / Starting list page scraping: {url}")
        
        soup = self._fetch_page(url)
        if not soup:
            logger.error("无法获取页面，返回空结果")
            return []
        
        products = []
        
        # 尝试不同的选择器 / Try different selectors
        for selector in SELECTORS["list_selectors"]:
            items = soup.select(selector)
            if items:
                logger.info(f"使用选择器找到 {len(items)} 个商品 / Found {len(items)} items with selector: {selector}")
                
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
                        logger.info(f"成功提取商品 {idx+1}/{min(len(items), max_items)}: {title[:30]}...")
                        
                    except Exception as e:
                        logger.error(f"提取商品信息失败 / Failed to extract product info: {e}")
                        continue
                
                if products:
                    break  # 如果找到商品就停止尝试其他选择器 / Stop if products found
        
        logger.info(f"列表页采集完成，共 {len(products)} 个商品 / List page scraping completed, {len(products)} products")
        
        # 如果没有商品，记录零结果页面 / Log zero result page if no products
        if len(products) == 0:
            logger.warning(f"零结果页面 / Zero result page: {url}")
        
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
        logger.info(f"开始采集商品详情 / Starting product detail scraping: {asin}")
        
        soup = self._fetch_page(url)
        if not soup:
            logger.error(f"无法获取商品详情页: {asin}")
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
            
            # 提取品牌 / Extract brand
            brand_elem = soup.select_one('a#bylineInfo')
            if brand_elem:
                detail['brand'] = brand_elem.get_text(strip=True).replace('Visit the', '').replace('Store', '').strip()
            
            # 提取当前售价和原价 / Extract current price and original price
            price_elem = soup.select_one('span.a-price span.a-offscreen')
            if price_elem:
                detail['current_price'] = price_elem.get_text(strip=True)
            
            # 提取原价（未打折前）/ Extract original price (before discount)
            list_price_elem = soup.select_one('span.a-price.a-text-price span.a-offscreen')
            if list_price_elem:
                detail['original_price'] = list_price_elem.get_text(strip=True)
            
            # 提取折扣信息 / Extract discount info
            discount_elem = soup.select_one('span.savingsPercentage')
            if discount_elem:
                detail['discount_percentage'] = discount_elem.get_text(strip=True)
            
            # 提取评分 / Extract rating
            rating_elem = soup.select_one('span.a-icon-alt')
            if rating_elem:
                detail['average_rating'] = rating_elem.get_text(strip=True)
            
            # 提取评论数 / Extract review count
            review_elem = soup.select_one('span#acrCustomerReviewText')
            if review_elem:
                detail['review_count'] = review_elem.get_text(strip=True)
            
            # 提取产品描述（短/长）/ Extract product description (short/long)
            desc_elem = soup.select_one('div#feature-bullets')
            if desc_elem:
                bullets = desc_elem.select('span.a-list-item')
                detail['short_description'] = [b.get_text(strip=True) for b in bullets if b.get_text(strip=True)]
            
            # 提取详细描述 / Extract detailed description
            long_desc_elem = soup.select_one('div#productDescription')
            if long_desc_elem:
                detail['long_description'] = long_desc_elem.get_text(strip=True)[:500]
            
            # 提取规格参数（尺寸、颜色、重量等）/ Extract specifications
            detail['specifications'] = {}
            spec_tables = soup.select('table.prodDetTable, div#prodDetails table')
            for table in spec_tables:
                rows = table.select('tr')
                for row in rows:
                    cells = row.select('th, td')
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            detail['specifications'][key] = value
            
            # 提取BSR排名 / Extract BSR ranking
            bsr_elem = soup.select_one('div#detailBulletsWrapper_feature_div')
            if bsr_elem:
                bsr_text = bsr_elem.get_text()
                if 'Best Sellers Rank' in bsr_text or 'BSR' in bsr_text:
                    detail['bsr_ranking'] = bsr_text[bsr_text.find('Best Sellers Rank'):bsr_text.find('Best Sellers Rank')+200].strip()
            
            # 提取首次上架时间 / Extract first available date
            date_elem = soup.select_one('div#detailBulletsWrapper_feature_div')
            if date_elem:
                date_text = date_elem.get_text()
                if 'Date First Available' in date_text:
                    start = date_text.find('Date First Available')
                    detail['first_available_date'] = date_text[start:start+100].replace('Date First Available', '').strip()[:50]
            
            # 提取库存状态 / Extract stock status
            stock_elem = soup.select_one('div#availability span')
            if stock_elem:
                detail['stock_status'] = stock_elem.get_text(strip=True)
            
            # 提取卖家信息 / Extract seller info
            seller_elem = soup.select_one('div#merchant-info')
            if seller_elem:
                detail['seller_name'] = seller_elem.get_text(strip=True)
            
            # 提取FBA信息 / Extract FBA info
            fba_elem = soup.select_one('span:contains("Fulfilled by Amazon")')
            detail['is_fba'] = bool(fba_elem)
            
            # 提取配送信息 / Extract shipping info
            shipping_elem = soup.select_one('div#mir-layout-DELIVERY_BLOCK')
            if shipping_elem:
                detail['shipping_info'] = shipping_elem.get_text(strip=True)[:200]
            
            logger.info(f"成功采集商品详情: {detail.get('title', 'N/A')[:30]}...")
            
        except Exception as e:
            logger.error(f"提取详情失败 / Failed to extract detail: {e}")
        
        return detail
    
    def scrape_product_reviews(self, asin: str, max_reviews: int = 10) -> List[Dict[str, Any]]:
        """
        采集商品评论
        Scrape product reviews
        
        Args:
            asin: 商品ASIN / Product ASIN
            max_reviews: 最大评论数 / Maximum reviews
            
        Returns:
            评论列表 / Review list
        """
        url = f"https://www.amazon.com/product-reviews/{asin}"
        logger.info(f"开始采集商品评论 / Starting review scraping: {asin}")
        
        soup = self._fetch_page(url)
        if not soup:
            logger.error(f"无法获取评论页面: {asin}")
            return []
        
        reviews = []
        review_elements = soup.select('div[data-hook="review"]')
        
        for review_elem in review_elements[:max_reviews]:
            try:
                review = {
                    "asin": asin,
                    "scraped_at": datetime.now(timezone.utc).isoformat()
                }
                
                # 评论人昵称 / Reviewer nickname
                name_elem = review_elem.select_one('span.a-profile-name')
                if name_elem:
                    review['reviewer_name'] = name_elem.get_text(strip=True)
                
                # 评论星级 / Review rating
                rating_elem = review_elem.select_one('i[data-hook="review-star-rating"] span')
                if rating_elem:
                    review['rating'] = rating_elem.get_text(strip=True)
                
                # 评论发布日期 / Review date
                date_elem = review_elem.select_one('span[data-hook="review-date"]')
                if date_elem:
                    review['review_date'] = date_elem.get_text(strip=True)
                
                # 评论标题 / Review title
                title_elem = review_elem.select_one('a[data-hook="review-title"] span')
                if title_elem:
                    review['review_title'] = title_elem.get_text(strip=True)
                
                # 评论正文 / Review content
                content_elem = review_elem.select_one('span[data-hook="review-body"] span')
                if content_elem:
                    review['review_content'] = content_elem.get_text(strip=True)
                
                # 评论图片 / Review images
                image_elems = review_elem.select('img[data-hook="review-image-tile"]')
                if image_elems:
                    review['review_images'] = [img.get('src', '') for img in image_elems]
                
                # 有用投票数 / Helpful votes
                helpful_elem = review_elem.select_one('span[data-hook="helpful-vote-statement"]')
                if helpful_elem:
                    review['helpful_votes'] = helpful_elem.get_text(strip=True)
                
                reviews.append(review)
                logger.info(f"成功提取评论 {len(reviews)}/{max_reviews}")
                
            except Exception as e:
                logger.error(f"提取评论失败 / Failed to extract review: {e}")
                continue
        
        logger.info(f"评论采集完成，共 {len(reviews)} 条 / Review scraping completed, {len(reviews)} reviews")
        return reviews
    
    def save_data(self, data: List[Dict[str, Any]], filename: str = None, data_type: str = "products") -> str:
        """
        保存数据到JSON文件
        Save data to JSON file
        
        Args:
            data: 数据列表 / Data list
            filename: 文件名(可选) / Filename (optional)
            data_type: 数据类型 (products, reviews) / Data type
            
        Returns:
            保存的文件路径 / Saved file path
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"amazon_{data_type}_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "items": data,
                    "total_count": len(data),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "data_type": data_type
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存 / Data saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存数据失败 / Failed to save data: {e}")
            return ""
    
    def run(self, url: str, max_items: int = 50, deep_detail: bool = False, include_reviews: bool = False, max_reviews: int = 5) -> List[Dict[str, Any]]:
        """
        运行完整的采集流程
        Run complete scraping workflow
        
        Args:
            url: 目标URL / Target URL
            max_items: 最大商品数 / Maximum items
            deep_detail: 是否采集详情 / Whether to scrape detail
            include_reviews: 是否采集评论 / Whether to include reviews
            max_reviews: 每个商品最大评论数 / Max reviews per product
            
        Returns:
            商品列表 / Product list
        """
        logger.info(f"开始完整采集流程 / Starting complete scraping workflow: {url}")
        
        # 采集列表页 / Scrape list page
        products = self.scrape_list_page(url, max_items)
        
        # 如果需要详情和/或评论，进一步采集 / Scrape details and/or reviews if needed
        if (deep_detail or include_reviews) and products:
            logger.info(f"开始采集 {len(products)} 个商品的详情和/或评论")
            
            # 限制详情采集数量，避免请求过多 / Limit detail scraping to avoid too many requests
            max_detail_count = min(len(products), 20)  # 最多20个商品的详情
            
            for i, product in enumerate(products[:max_detail_count]):
                asin = product['asin']
                logger.info(f"正在处理商品 {i+1}/{max_detail_count}: {asin}")
                
                # 采集详情 / Scrape detail
                if deep_detail:
                    self._wait()
                    detail = self.scrape_product_detail(asin)
                    product.update(detail)
                    logger.info(f"详情采集进度 / Detail scraping progress: {i+1}/{max_detail_count}")
                
                # 采集评论 / Scrape reviews
                if include_reviews:
                    self._wait()
                    reviews = self.scrape_product_reviews(asin, max_reviews)
                    product['reviews'] = reviews
                    logger.info(f"评论采集进度 / Reviews scraping progress: {i+1}/{max_detail_count}")
        
        # 保存数据 / Save data
        if products:
            logger.info(f"准备保存 {len(products)} 个商品数据")
            self.save_data(products)
        
        logger.info(f"采集流程完成 / Scraping workflow completed")
        return products
    
    def run_batch(self, urls: List[str], max_items_per_url: int = 20, deep_detail: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量处理多个URL
        Process multiple URLs in batch
        
        Args:
            urls: URL列表 / URL list
            max_items_per_url: 每个URL最大商品数 / Max items per URL
            deep_detail: 是否采集详情 / Whether to scrape detail
            
        Returns:
            按URL分组的商品数据 / URL grouped product data
        """
        results = {}
        
        for url in urls:
            logger.info(f"开始处理批量URL中的第 {list(urls).index(url)+1}/{len(urls)} 个: {url}")
            products = self.run(url, max_items_per_url, deep_detail)
            results[url] = products
            
            # 批量处理时增加间隔时间 / Increase wait time between URLs
            if list(urls).index(url) < len(urls) - 1:
                logger.info("批量处理中的URL间隔...")
                time.sleep(random.uniform(3.0, 5.0))
        
        # 合并所有结果并保存 / Merge all results and save
        all_products = []
        for url, products in results.items():
            all_products.extend(products)
        
        if all_products:
            self.save_data(all_products, filename=f"amazon_batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        logger.info(f"批量处理完成，共处理 {len(urls)} 个URL，采集 {len(all_products)} 个商品")
        return results

def main():
    """主函数 / Main function"""
    parser = argparse.ArgumentParser(description="Amazon 爬虫程序 - 采集Amazon商品数据")
    
    # 基本参数 / Basic arguments
    parser.add_argument("--url", type=str, help="Amazon搜索页面URL")
    parser.add_argument("--batch-file", type=str, help="包含多个URL的文本文件路径")
    parser.add_argument("--output-dir", type=str, default="data/amazon", help="数据输出目录")
    parser.add_argument("--max-items", type=int, default=50, help="最大采集商品数量")
    
    # 功能选项 / Feature options
    parser.add_argument("--deep-detail", action="store_true", help="采集商品详细信息")
    parser.add_argument("--include-reviews", action="store_true", help="采集商品评论")
    parser.add_argument("--max-reviews", type=int, default=5, help="每个商品最大评论数")
    
    # 配置选项 / Configuration options
    parser.add_argument("--min-wait", type=float, default=1.0, help="最小等待时间(秒)")
    parser.add_argument("--max-wait", type=float, default=3.0, help="最大等待时间(秒)")
    parser.add_argument("--max-retries", type=int, default=3, help="最大重试次数")
    parser.add_argument("--timeout", type=int, default=30, help="请求超时时间(秒)")
    parser.add_argument("--proxy", type=str, help="代理服务器地址")
    
    args = parser.parse_args()
    
    # 验证参数 / Validate arguments
    if not args.url and not args.batch_file:
        parser.error("必须提供 --url 或 --batch-file 参数")
    
    # 创建配置 / Create config
    config = {
        "data_dir": args.output_dir,
        "min_wait_time": args.min_wait,
        "max_wait_time": args.max_wait,
        "max_retries": args.max_retries,
        "timeout": args.timeout,
        "proxy": args.proxy
    }
    
    # 创建爬虫实例 / Create crawler instance
    crawler = AmazonCrawler(config)
    
    logger.info("Amazon爬虫程序启动")
    logger.info(f"配置: 最小等待={args.min_wait}s, 最大等待={args.max_wait}s, 最大重试={args.max_retries}, 超时={args.timeout}s")
    
    if args.batch_file:
        # 批量处理模式 / Batch processing mode
        try:
            with open(args.batch_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            logger.info(f"从文件加载了 {len(urls)} 个URL进行批量处理")
            crawler.run_batch(urls, args.max_items, args.deep_detail)
            
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
    else:
        # 单URL模式 / Single URL mode
        logger.info(f"开始采集URL: {args.url}")
        logger.info(f"选项: 深度详情={args.deep_detail}, 包含评论={args.include_reviews}, 最大评论数={args.max_reviews}")
        
        products = crawler.run(
            args.url, 
            max_items=args.max_items,
            deep_detail=args.deep_detail,
            include_reviews=args.include_reviews,
            max_reviews=args.max_reviews
        )
        
        logger.info(f"采集完成! 总共采集了 {len(products)} 个商品")
        
        # 显示简单统计 / Show simple stats
        if products:
            # 计算有价格信息的商品比例 / Calculate percentage of products with price
            priced_products = [p for p in products if p.get('price')]
            price_percentage = (len(priced_products) / len(products)) * 100
            
            # 计算有评分信息的商品比例 / Calculate percentage of products with rating
            rated_products = [p for p in products if p.get('rating')]
            rating_percentage = (len(rated_products) / len(products)) * 100
            
            logger.info(f"统计信息:")
            logger.info(f"  - 商品总数: {len(products)}")
            logger.info(f"  - 有价格信息的商品: {len(priced_products)} ({price_percentage:.1f}%)")
            logger.info(f"  - 有评分信息的商品: {len(rated_products)} ({rating_percentage:.1f}%)")
            
            # 显示前3个商品的预览 / Show preview of first 3 products
            logger.info("\n前3个商品预览:")
            for i, product in enumerate(products[:3], 1):
                logger.info(f"商品 {i}:")
                logger.info(f"  标题: {product.get('title', 'N/A')[:60]}...")
                logger.info(f"  价格: {product.get('price', 'N/A')}")
                logger.info(f"  评分: {product.get('rating', 'N/A')}")
                logger.info(f"  ASIN: {product.get('asin', 'N/A')}")

if __name__ == "__main__":
    main()