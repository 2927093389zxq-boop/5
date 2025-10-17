"""
多平台爬虫模块 - 支持28个电商平台
Multi-Platform Scraper Module - Support for 28 e-commerce platforms

支持的平台 / Supported platforms:
1. Fordeal
2. Mercari
3. Fyndia
4. Tokopedia
5. Onbuy
6. Joom
7. Yandex Market
8. Faire
9. AliExpress
10. eBay
11. TikTok Shop
12. Rakuten Japan (乐天日本)
13. Ozon
14. Etsy
15. Mercadolibre
16. Noon
17. Wildberries
18. Shopee
19. Coupang
20. Flipkart
21. Allegro
22. Target
23. Falabella
24. Cdiscount
25. Otto
26. Jumia
27. Lazada
28. Temu
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper
from scrapers.logger import log_info, log_error, log_warning


# ==================== Fordeal ====================
class FordealScraper(BaseScraper):
    """Fordeal平台爬虫 / Fordeal Platform Scraper"""
    PLATFORM_NAME = "fordeal"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Fordeal商品列表 / Scrape Fordeal product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.product-item",
            "div[class*='product']",
            "div.item-card"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div.title", "h3", "h4"]),
                            "price": self._extract_text(item, ["div.price", "span.price", "span[class*='price']"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Mercari ====================
class MercariScraper(BaseScraper):
    """Mercari平台爬虫 / Mercari Platform Scraper"""
    PLATFORM_NAME = "mercari"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Mercari商品列表 / Scrape Mercari product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div[data-testid='SearchResultItem']",
            "div.item-box",
            "div[class*='item']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div[data-testid='ItemName']", "h3", "div.item-name"]),
                            "price": self._extract_text(item, ["div[data-testid='ItemPrice']", "span.price", "div.price"]),
                            "condition": self._extract_text(item, ["div[data-testid='ItemCondition']", "span.condition"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Fyndia ====================
class FyndiaScraper(BaseScraper):
    """Fyndia平台爬虫 / Fyndia Platform Scraper"""
    PLATFORM_NAME = "fyndia"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Fyndia商品列表 / Scrape Fyndia product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.product-card",
            "div.product-item",
            "article[class*='product']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h3.product-title", "div.title", "h4"]),
                            "price": self._extract_text(item, ["span.price", "div.price"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Tokopedia ====================
class TokopediaScraper(BaseScraper):
    """Tokopedia平台爬虫 / Tokopedia Platform Scraper"""
    PLATFORM_NAME = "tokopedia"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Tokopedia商品列表 / Scrape Tokopedia product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div[data-testid='divProductWrapper']",
            "div.css-kkkpmy",
            "div.product-card"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div.prd_link-product-name", "span.product-name"]),
                            "price": self._extract_text(item, ["div.prd_link-product-price", "span.price"]),
                            "rating": self._extract_text(item, ["span.rating", "div[class*='rating']"]),
                            "location": self._extract_text(item, ["span.prd_link-shop-loc", "span.location"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Onbuy ====================
class OnbuyScraper(BaseScraper):
    """Onbuy平台爬虫 / Onbuy Platform Scraper"""
    PLATFORM_NAME = "onbuy"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Onbuy商品列表 / Scrape Onbuy product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.listing-product",
            "div.product-item",
            "article.product"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h4.product-title", "a.product-link"]),
                            "price": self._extract_text(item, ["span.price-value", "div.price"]),
                            "rating": self._extract_text(item, ["span.rating-value"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Joom ====================
class JoomScraper(BaseScraper):
    """Joom平台爬虫 / Joom Platform Scraper"""
    PLATFORM_NAME = "joom"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Joom商品列表 / Scrape Joom product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.goods-item",
            "div[class*='ProductCard']",
            "article.product"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div.goods-item__title", "h3", "div.title"]),
                            "price": self._extract_text(item, ["div.goods-item__price", "span.price"]),
                            "rating": self._extract_text(item, ["div.rating", "span.rating-value"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Yandex Market ====================
class YandexMarketScraper(BaseScraper):
    """Yandex Market平台爬虫 / Yandex Market Platform Scraper"""
    PLATFORM_NAME = "yandex_market"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Yandex Market商品列表 / Scrape Yandex Market product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "article[data-autotest-id='product-snippet']",
            "div.n-snippet-card2",
            "div[class*='ProductCard']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h3", "a[class*='title']", "span.title"]),
                            "price": self._extract_text(item, ["span[class*='price']", "div.price"]),
                            "rating": self._extract_text(item, ["div[class*='rating']"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Faire ====================
class FaireScraper(BaseScraper):
    """Faire平台爬虫 / Faire Platform Scraper"""
    PLATFORM_NAME = "faire"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Faire商品列表 / Scrape Faire product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div[data-test-id='product-card']",
            "div.product-card",
            "article.product"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h3", "div.product-name", "a.title"]),
                            "price": self._extract_text(item, ["span.price", "div.price"]),
                            "brand": self._extract_text(item, ["div.brand-name", "span.brand"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== AliExpress ====================
class AliExpressScraper(BaseScraper):
    """AliExpress平台爬虫 / AliExpress Platform Scraper"""
    PLATFORM_NAME = "aliexpress"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集AliExpress商品列表 / Scrape AliExpress product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.list--gallery--C2f2tvm",
            "div[class*='product-item']",
            "a.search-card-item"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h1", "h3", "div.title", "span.title"]),
                            "price": self._extract_text(item, ["div.price", "span.price"]),
                            "orders": self._extract_text(item, ["span.order", "div[class*='order']"]),
                            "rating": self._extract_text(item, ["span.rating", "div.rating"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== eBay (Real Implementation) ====================
class EbayScraper(BaseScraper):
    """eBay平台爬虫（真实实现）/ eBay Platform Scraper (Real Implementation)"""
    PLATFORM_NAME = "ebay"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集eBay商品列表 / Scrape eBay product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.s-item",
            "li.s-item",
            "div.srp-results li"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        # Skip placeholder items
                        if 'srp-river-answer' in item.get('class', []):
                            continue
                        
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h3.s-item__title", "div.s-item__title"]),
                            "price": self._extract_text(item, ["span.s-item__price", "div.s-item__price"]),
                            "condition": self._extract_text(item, ["span.SECONDARY_INFO", "span.s-item__condition"]),
                            "shipping": self._extract_text(item, ["span.s-item__shipping", "span[class*='shipping']"]),
                            "url": self._extract_text(item, ["a.s-item__link"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"] and product["title"] != "Shop on eBay":
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== TikTok Shop ====================
class TiktokShopScraper(BaseScraper):
    """TikTok Shop平台爬虫 / TikTok Shop Platform Scraper"""
    PLATFORM_NAME = "tiktokshop"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集TikTok Shop商品列表 / Scrape TikTok Shop product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div[class*='ProductCard']",
            "div.product-item",
            "a[class*='product']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div[class*='title']", "span.title", "h3"]),
                            "price": self._extract_text(item, ["div[class*='price']", "span.price"]),
                            "sold": self._extract_text(item, ["span[class*='sold']", "div.sold"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Rakuten Japan (乐天日本) ====================
class RakutenJapanScraper(BaseScraper):
    """Rakuten Japan平台爬虫（乐天日本）/ Rakuten Japan Platform Scraper"""
    PLATFORM_NAME = "rakuten_japan"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Rakuten Japan商品列表 / Scrape Rakuten Japan product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.searchresultitem",
            "div.dui-card",
            "div[class*='item']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h2", "div.title", "a.title"]),
                            "price": self._extract_text(item, ["span.price", "div.price"]),
                            "rating": self._extract_text(item, ["span.rating", "div[class*='rating']"]),
                            "review_count": self._extract_text(item, ["span.review", "span[class*='review']"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Ozon ====================
class OzonScraper(BaseScraper):
    """Ozon平台爬虫 / Ozon Platform Scraper"""
    PLATFORM_NAME = "ozon"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Ozon商品列表 / Scrape Ozon product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div[class*='tile']",
            "div.widget-search-result-container",
            "article"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["span.tsBody500Medium", "div.title", "h3"]),
                            "price": self._extract_text(item, ["span[class*='price']", "div.price"]),
                            "rating": self._extract_text(item, ["div[class*='rating']"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Etsy ====================
class EtsyScraper(BaseScraper):
    """Etsy平台爬虫 / Etsy Platform Scraper"""
    PLATFORM_NAME = "etsy"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Etsy商品列表 / Scrape Etsy product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.v2-listing-card",
            "div[data-listing-id]",
            "div.listing-card"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h3", "h2.v2-listing-card__title"]),
                            "price": self._extract_text(item, ["span.currency-value", "span.price"]),
                            "rating": self._extract_text(item, ["span[class*='rating']"]),
                            "shop": self._extract_text(item, ["p.shop-name", "span.shop"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Mercadolibre ====================
class MercadolibreScraper(BaseScraper):
    """Mercadolibre平台爬虫 / Mercadolibre Platform Scraper"""
    PLATFORM_NAME = "mercadolibre"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Mercadolibre商品列表 / Scrape Mercadolibre product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "li.ui-search-layout__item",
            "div.ui-search-result",
            "div.andes-card"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h2.ui-search-item__title", "h2"]),
                            "price": self._extract_text(item, ["span.price-tag-fraction", "div.price"]),
                            "shipping": self._extract_text(item, ["p.ui-search-item__shipping", "span.shipping"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Noon ====================
class NoonScraper(BaseScraper):
    """Noon平台爬虫 / Noon Platform Scraper"""
    PLATFORM_NAME = "noon"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Noon商品列表 / Scrape Noon product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div[class*='productContainer']",
            "div.grid",
            "div[data-qa='product-card']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div[class*='title']", "h3", "span.title"]),
                            "price": self._extract_text(item, ["div[class*='price']", "span.price"]),
                            "rating": self._extract_text(item, ["div[class*='rating']"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Wildberries ====================
class WildberriesScraper(BaseScraper):
    """Wildberries平台爬虫 / Wildberries Platform Scraper"""
    PLATFORM_NAME = "wildberries"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Wildberries商品列表 / Scrape Wildberries product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "article.product-card",
            "div.product-card",
            "div[class*='card']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["span.goods-name", "h3", "div.title"]),
                            "price": self._extract_text(item, ["span.price", "div[class*='price']"]),
                            "rating": self._extract_text(item, ["span.rating", "div.rating"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Shopee (Real Implementation) ====================
class ShopeeScraper(BaseScraper):
    """Shopee平台爬虫（真实实现）/ Shopee Platform Scraper (Real Implementation)"""
    PLATFORM_NAME = "shopee"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Shopee商品列表 / Scrape Shopee product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.col-xs-2-4",
            "div[data-sqe='item']",
            "div.shopee-search-item-result__item"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div.ie3A+n", "div[class*='title']"]),
                            "price": self._extract_text(item, ["span.ZEgDH9", "div.price"]),
                            "sold": self._extract_text(item, ["div.r6HknA", "span.sold"]),
                            "location": self._extract_text(item, ["div.zGGwiV", "div.location"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Coupang ====================
class CoupangScraper(BaseScraper):
    """Coupang平台爬虫 / Coupang Platform Scraper"""
    PLATFORM_NAME = "coupang"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Coupang商品列表 / Scrape Coupang product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "li.search-product",
            "li[class*='product']",
            "div.product-item"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div.name", "div.title"]),
                            "price": self._extract_text(item, ["strong.price-value", "span.price"]),
                            "rating": self._extract_text(item, ["span.rating", "div[class*='rating']"]),
                            "delivery": self._extract_text(item, ["span.delivery", "div.delivery"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Flipkart ====================
class FlipkartScraper(BaseScraper):
    """Flipkart平台爬虫 / Flipkart Platform Scraper"""
    PLATFORM_NAME = "flipkart"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Flipkart商品列表 / Scrape Flipkart product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div._1AtVbE",
            "div[class*='product']",
            "div._13oc-S"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div._4rR01T", "a.s1Q9rs", "div.title"]),
                            "price": self._extract_text(item, ["div._30jeq3", "div.price"]),
                            "rating": self._extract_text(item, ["div._3LWZlK", "span.rating"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Allegro ====================
class AllegroScraper(BaseScraper):
    """Allegro平台爬虫 / Allegro Platform Scraper"""
    PLATFORM_NAME = "allegro"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Allegro商品列表 / Scrape Allegro product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "article[data-role='offer']",
            "div.mpof_ki",
            "article"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h2", "div.mpof_ki_title", "a[class*='title']"]),
                            "price": self._extract_text(item, ["span.mpof_ki_price", "span.price"]),
                            "delivery": self._extract_text(item, ["span.mpof_ki_delivery", "span.delivery"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Target ====================
class TargetScraper(BaseScraper):
    """Target平台爬虫 / Target Platform Scraper"""
    PLATFORM_NAME = "target"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Target商品列表 / Scrape Target product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div[data-test='@web/site-top-of-funnel/ProductCardWrapper']",
            "div.ProductCard",
            "li[class*='styles__StyledCol']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["a[data-test='product-title']", "div.title"]),
                            "price": self._extract_text(item, ["span[data-test='current-price']", "span.price"]),
                            "rating": self._extract_text(item, ["div[data-test='ratings']"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Falabella ====================
class FalabellaScraper(BaseScraper):
    """Falabella平台爬虫 / Falabella Platform Scraper"""
    PLATFORM_NAME = "falabella"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Falabella商品列表 / Scrape Falabella product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.pod-card",
            "div.search-pod-item",
            "div[class*='product']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["b.pod-title", "div.title"]),
                            "price": self._extract_text(item, ["span.copy14", "span.price"]),
                            "rating": self._extract_text(item, ["span.rating"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Cdiscount ====================
class CdiscountScraper(BaseScraper):
    """Cdiscount平台爬虫 / Cdiscount Platform Scraper"""
    PLATFORM_NAME = "cdiscount"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Cdiscount商品列表 / Scrape Cdiscount product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.prdtBILDetails",
            "div[class*='product']",
            "ul.prdtList li"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h3.prdtBILTit", "a.title"]),
                            "price": self._extract_text(item, ["span.price", "div.price"]),
                            "rating": self._extract_text(item, ["span.rating"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Otto ====================
class OttoScraper(BaseScraper):
    """Otto平台爬虫 / Otto Platform Scraper"""
    PLATFORM_NAME = "otto"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Otto商品列表 / Scrape Otto product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div.find_tile",
            "article.product",
            "div[class*='product']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h2", "p.find_tile__name"]),
                            "price": self._extract_text(item, ["span.find_tile__price", "span.price"]),
                            "rating": self._extract_text(item, ["span.rating"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Jumia ====================
class JumiaScraper(BaseScraper):
    """Jumia平台爬虫 / Jumia Platform Scraper"""
    PLATFORM_NAME = "jumia"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Jumia商品列表 / Scrape Jumia product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "article.prd",
            "div.card",
            "article[class*='product']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["h3.name", "div.title"]),
                            "price": self._extract_text(item, ["div.prc", "span.price"]),
                            "rating": self._extract_text(item, ["div.stars", "span.rating"]),
                            "discount": self._extract_text(item, ["div.bdg", "span.discount"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='data-src'),
                        }
                        if not product["image"]:
                            product["image"] = self._extract_text(item, ["img"], attr='src')
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Lazada ====================
class LazadaScraper(BaseScraper):
    """Lazada平台爬虫 / Lazada Platform Scraper"""
    PLATFORM_NAME = "lazada"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Lazada商品列表 / Scrape Lazada product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div[data-qa-locator='product-item']",
            "div.Bm3ON",
            "div[class*='product']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div.RfADt", "div.title", "h3"]),
                            "price": self._extract_text(item, ["span.ooOxS", "span.price"]),
                            "rating": self._extract_text(item, ["span.qzqFw", "span.rating"]),
                            "location": self._extract_text(item, ["span.oa6ri", "span.location"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== Temu ====================
class TemuScraper(BaseScraper):
    """Temu平台爬虫 / Temu Platform Scraper"""
    PLATFORM_NAME = "temu"
    
    def scrape_list_page(self, url: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """采集Temu商品列表 / Scrape Temu product list"""
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        products = []
        selectors = [
            "div[class*='goods-card']",
            "div[class*='ProductCard']",
            "div[data-role='product']"
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                log_info(f"[{self.PLATFORM_NAME}] 找到 {len(items)} 个商品 / Found {len(items)} items")
                for item in items[:max_items]:
                    try:
                        product = {
                            "platform": self.PLATFORM_NAME,
                            "title": self._extract_text(item, ["div[class*='title']", "h3", "span.title"]),
                            "price": self._extract_text(item, ["div[class*='price']", "span.price"]),
                            "rating": self._extract_text(item, ["div[class*='rating']", "span.rating"]),
                            "sold": self._extract_text(item, ["span[class*='sold']", "div.sold"]),
                            "url": self._extract_text(item, ["a"], attr='href'),
                            "image": self._extract_text(item, ["img"], attr='src'),
                        }
                        if product["title"]:
                            products.append(product)
                    except Exception as e:
                        log_error(f"[{self.PLATFORM_NAME}] 提取失败 / Extract failed: {e}")
                        continue
                if products:
                    break
        
        return products


# ==================== 平台映射 / Platform Mapping ====================
PLATFORM_SCRAPERS = {
    "fordeal": FordealScraper,
    "mercari": MercariScraper,
    "fyndia": FyndiaScraper,
    "tokopedia": TokopediaScraper,
    "onbuy": OnbuyScraper,
    "joom": JoomScraper,
    "yandex_market": YandexMarketScraper,
    "faire": FaireScraper,
    "aliexpress": AliExpressScraper,
    "ebay": EbayScraper,
    "tiktokshop": TiktokShopScraper,
    "rakuten_japan": RakutenJapanScraper,
    "ozon": OzonScraper,
    "etsy": EtsyScraper,
    "mercadolibre": MercadolibreScraper,
    "noon": NoonScraper,
    "wildberries": WildberriesScraper,
    "shopee": ShopeeScraper,
    "coupang": CoupangScraper,
    "flipkart": FlipkartScraper,
    "allegro": AllegroScraper,
    "target": TargetScraper,
    "falabella": FalabellaScraper,
    "cdiscount": CdiscountScraper,
    "otto": OttoScraper,
    "jumia": JumiaScraper,
    "lazada": LazadaScraper,
    "temu": TemuScraper,
}


def get_scraper(platform_name: str) -> BaseScraper:
    """
    获取指定平台的爬虫实例
    Get scraper instance for specified platform
    
    Args:
        platform_name: 平台名称 / Platform name
        
    Returns:
        爬虫实例 / Scraper instance
    """
    platform_name = platform_name.lower().replace(" ", "_")
    scraper_class = PLATFORM_SCRAPERS.get(platform_name)
    
    if scraper_class:
        return scraper_class()
    else:
        raise ValueError(f"不支持的平台 / Unsupported platform: {platform_name}")


def scrape_platform(platform_name: str, url: str, max_items: int = 50, deep_detail: bool = False) -> List[Dict[str, Any]]:
    """
    便捷函数：采集指定平台的数据
    Convenience function: Scrape data from specified platform
    
    Args:
        platform_name: 平台名称 / Platform name
        url: 目标URL / Target URL
        max_items: 最大商品数 / Maximum items
        deep_detail: 是否采集详情 / Whether to scrape detail
        
    Returns:
        商品列表 / Product list
    """
    scraper = get_scraper(platform_name)
    return scraper.run(url, max_items, deep_detail)
