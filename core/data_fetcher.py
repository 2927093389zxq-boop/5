"""
数据获取模块 - 支持多平台数据采集
Data Fetcher Module - Multi-platform data collection support
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import time

# 支持的平台列表 / Supported platforms list
PLATFORM_LIST = [
    "Amazon", "Shopee", "eBay", "Fordeal", "Mercari", "Fyndia", "Tokopedia",
    "Onbuy", "Joom", "Yandex Market", "Faire", "AliExpress", "TikTok Shop",
    "Rakuten Japan", "Ozon", "Etsy", "Mercadolibre", "Noon", "Wildberries",
    "Coupang", "Flipkart", "Allegro", "Target", "Falabella", "Cdiscount",
    "Otto", "Jumia", "Lazada", "Temu"
]


def get_platform_data(
    platform_name: str,
    keyword: str = "",
    category_url: str = "",
    max_items: int = 50,
    deep_detail: bool = True
) -> List[Dict[str, Any]]:
    """
    从指定平台获取数据
    Get data from specified platform
    
    Args:
        platform_name: 平台名称 (Platform name)
        keyword: 搜索关键词 (Search keyword)
        category_url: 分类URL (Category URL)
        max_items: 最大条目数 (Maximum items)
        deep_detail: 是否获取详情 (Whether to get details)
    
    Returns:
        数据列表 (List of data items)
    """
    if platform_name == "Amazon":
        return _fetch_amazon_data(keyword, category_url, max_items, deep_detail)
    elif platform_name in ["Shopee", "eBay", "Fordeal", "Mercari", "Fyndia", "Tokopedia",
                           "Onbuy", "Joom", "Yandex Market", "Faire", "AliExpress", 
                           "TikTok Shop", "Rakuten Japan", "Ozon", "Etsy", "Mercadolibre",
                           "Noon", "Wildberries", "Coupang", "Flipkart", "Allegro",
                           "Target", "Falabella", "Cdiscount", "Otto", "Jumia", "Lazada", "Temu"]:
        return _fetch_multi_platform_data(platform_name, keyword, category_url, max_items, deep_detail)
    else:
        st.error(f"不支持的平台: {platform_name} / Unsupported platform: {platform_name}")
        return []


def _fetch_amazon_data(
    keyword: str,
    category_url: str,
    max_items: int,
    deep_detail: bool
) -> List[Dict[str, Any]]:
    """Amazon平台数据获取 / Amazon platform data fetching"""
    try:
        from scrapers.amazon_scraper import AmazonScraper
        
        st.info("正在从Amazon获取数据... / Fetching data from Amazon...")
        
        # 构建URL / Build URL
        if category_url:
            url = category_url
        elif keyword:
            url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
        else:
            url = "https://www.amazon.com/bestsellers"
        
        # 使用真实爬虫 / Use real scraper
        scraper = AmazonScraper()
        products = scraper.run(url, max_items=max_items, deep_detail=deep_detail)
        
        # 转换为统一格式 / Convert to unified format
        result = []
        for product in products:
            item = {
                "platform": "Amazon",
                "title": product.get("title", ""),
                "price": product.get("price", ""),
                "rating": product.get("rating", ""),
                "url": product.get("url", ""),
                "asin": product.get("asin", ""),
                "review_count": product.get("review_count", ""),
                "scraped_at": product.get("scraped_at", "")
            }
            if deep_detail and "description" in product:
                item["description"] = product.get("description", "")
                item["brand"] = product.get("brand", "")
            result.append(item)
        
        return result
        
    except Exception as e:
        st.error(f"Amazon数据获取失败 / Amazon data fetch failed: {e}")
        # 降级为模拟数据 / Fallback to mock data
        st.warning("使用模拟数据 / Using mock data")
        return _fetch_amazon_mock_data(keyword, category_url, max_items, deep_detail)


def _fetch_amazon_mock_data(
    keyword: str,
    category_url: str,
    max_items: int,
    deep_detail: bool
) -> List[Dict[str, Any]]:
    """Amazon模拟数据(降级方案) / Amazon mock data (fallback)"""
    time.sleep(0.5)
    
    mock_data = []
    for i in range(min(max_items, 10)):
        item = {
            "platform": "Amazon",
            "title": f"Amazon Product {i+1} - {keyword or 'Bestseller'}",
            "price": f"${19.99 + i * 5}",
            "rating": f"{4.0 + (i % 5) * 0.2:.1f}",
            "url": f"https://amazon.com/product/{i+1}",
            "category": category_url or "Electronics"
        }
        if deep_detail:
            item["description"] = f"Detailed description for product {i+1}"
            item["reviews_count"] = 100 + i * 50
        mock_data.append(item)
    
    return mock_data


def _fetch_shopee_data(
    keyword: str,
    category_url: str,
    max_items: int,
    deep_detail: bool
) -> List[Dict[str, Any]]:
    """Shopee平台数据获取 / Shopee platform data fetching"""
    st.info("正在从Shopee获取数据... / Fetching data from Shopee...")
    time.sleep(0.5)
    
    mock_data = []
    for i in range(min(max_items, 10)):
        item = {
            "platform": "Shopee",
            "title": f"Shopee Item {i+1} - {keyword or 'Hot Sale'}",
            "price": f"₱{299 + i * 100}",
            "rating": f"{4.2 + (i % 5) * 0.15:.1f}",
            "url": f"https://shopee.ph/product/{i+1}",
            "category": category_url or "Fashion",
            "sold_count": f"{500 + i * 200} sold"
        }
        if deep_detail:
            item["description"] = f"Shopee product description {i+1}"
            item["shop_name"] = f"Shop{i+1}"
            item["shipping_from"] = "Metro Manila"
        mock_data.append(item)
    
    return mock_data


def _fetch_ebay_data(
    keyword: str,
    category_url: str,
    max_items: int,
    deep_detail: bool
) -> List[Dict[str, Any]]:
    """eBay平台数据获取 / eBay platform data fetching"""
    st.info("正在从eBay获取数据... / Fetching data from eBay...")
    time.sleep(0.5)
    
    mock_data = []
    for i in range(min(max_items, 10)):
        item = {
            "platform": "eBay",
            "title": f"eBay Listing {i+1} - {keyword or 'Popular'}",
            "price": f"${25.99 + i * 10}",
            "condition": "New" if i % 2 == 0 else "Used",
            "url": f"https://ebay.com/itm/{i+1}",
            "category": category_url or "Electronics",
            "bids": i * 2 if i % 3 == 0 else "Buy It Now"
        }
        if deep_detail:
            item["description"] = f"eBay item description {i+1}"
            item["seller_rating"] = f"{95 + i % 5}%"
            item["shipping"] = "Free shipping" if i % 2 == 0 else "$5.99"
        mock_data.append(item)
    
    return mock_data


def _fetch_multi_platform_data(
    platform_name: str,
    keyword: str,
    category_url: str,
    max_items: int,
    deep_detail: bool
) -> List[Dict[str, Any]]:
    """
    多平台数据获取（使用真实爬虫）
    Multi-platform data fetching (using real scrapers)
    """
    try:
        from scrapers.multi_platform_scraper import get_scraper
        
        st.info(f"正在从{platform_name}获取数据... / Fetching data from {platform_name}...")
        
        # 构建URL / Build URL
        platform_lower = platform_name.lower().replace(" ", "_")
        
        # 平台URL模式映射 / Platform URL pattern mapping
        url_patterns = {
            "shopee": f"https://shopee.ph/search?keyword={keyword}" if keyword else "https://shopee.ph/",
            "ebay": f"https://www.ebay.com/sch/i.html?_nkw={keyword}" if keyword else "https://www.ebay.com/",
            "fordeal": category_url or f"https://www.fordeal.com/search?q={keyword}",
            "mercari": category_url or f"https://www.mercari.com/search/?keyword={keyword}",
            "fyndia": category_url or f"https://www.fyndia.com/search?q={keyword}",
            "tokopedia": category_url or f"https://www.tokopedia.com/search?q={keyword}",
            "onbuy": category_url or f"https://www.onbuy.com/gb/search/?q={keyword}",
            "joom": category_url or f"https://www.joom.com/en/search/q.{keyword}",
            "yandex_market": category_url or f"https://market.yandex.ru/search?text={keyword}",
            "faire": category_url or f"https://www.faire.com/search?q={keyword}",
            "aliexpress": category_url or f"https://www.aliexpress.com/w/wholesale-{keyword}.html",
            "tiktokshop": category_url or f"https://shop.tiktok.com/search?q={keyword}",
            "rakuten_japan": category_url or f"https://search.rakuten.co.jp/search/mall/{keyword}/",
            "ozon": category_url or f"https://www.ozon.ru/search/?text={keyword}",
            "etsy": category_url or f"https://www.etsy.com/search?q={keyword}",
            "mercadolibre": category_url or f"https://www.mercadolibre.com.ar/{keyword}",
            "noon": category_url or f"https://www.noon.com/uae-en/search?q={keyword}",
            "wildberries": category_url or f"https://www.wildberries.ru/catalog/0/search.aspx?search={keyword}",
            "coupang": category_url or f"https://www.coupang.com/np/search?q={keyword}",
            "flipkart": category_url or f"https://www.flipkart.com/search?q={keyword}",
            "allegro": category_url or f"https://allegro.pl/listing?string={keyword}",
            "target": category_url or f"https://www.target.com/s?searchTerm={keyword}",
            "falabella": category_url or f"https://www.falabella.com/falabella-cl/search?Ntt={keyword}",
            "cdiscount": category_url or f"https://www.cdiscount.com/search/10/{keyword}.html",
            "otto": category_url or f"https://www.otto.de/suche/{keyword}/",
            "jumia": category_url or f"https://www.jumia.com.ng/catalog/?q={keyword}",
            "lazada": category_url or f"https://www.lazada.com.my/catalog/?q={keyword}",
            "temu": category_url or f"https://www.temu.com/search_result.html?search_key={keyword}",
        }
        
        url = url_patterns.get(platform_lower, category_url or "")
        if not url:
            st.error(f"无法构建{platform_name}的URL / Cannot build URL for {platform_name}")
            return []
        
        # 使用真实爬虫 / Use real scraper
        scraper = get_scraper(platform_lower)
        products = scraper.run(url, max_items=max_items, deep_detail=deep_detail)
        
        # 转换为统一格式 / Convert to unified format
        result = []
        for product in products:
            item = {
                "platform": platform_name,
                "title": product.get("title", ""),
                "price": product.get("price", ""),
                "url": product.get("url", ""),
                "image": product.get("image", ""),
            }
            # 添加可选字段 / Add optional fields
            for key in ["rating", "review_count", "condition", "shipping", "brand", 
                       "sold", "location", "delivery", "discount"]:
                if key in product:
                    item[key] = product[key]
            
            result.append(item)
        
        return result
        
    except Exception as e:
        st.error(f"{platform_name}数据获取失败 / {platform_name} data fetch failed: {e}")
        # 降级为模拟数据 / Fallback to mock data
        st.warning("使用模拟数据 / Using mock data")
        return _fetch_generic_mock_data(platform_name, keyword, category_url, max_items, deep_detail)


def _fetch_generic_mock_data(
    platform_name: str,
    keyword: str,
    category_url: str,
    max_items: int,
    deep_detail: bool
) -> List[Dict[str, Any]]:
    """通用模拟数据生成器 / Generic mock data generator"""
    time.sleep(0.5)
    
    mock_data = []
    for i in range(min(max_items, 10)):
        item = {
            "platform": platform_name,
            "title": f"{platform_name} Product {i+1} - {keyword or 'Featured'}",
            "price": f"${19.99 + i * 5}" if i % 2 == 0 else f"€{15.99 + i * 4}",
            "rating": f"{4.0 + (i % 5) * 0.2:.1f}",
            "url": f"https://{platform_name.lower().replace(' ', '')}.com/product/{i+1}",
            "category": category_url or "General"
        }
        if deep_detail:
            item["description"] = f"Detailed description for {platform_name} product {i+1}"
            item["review_count"] = 50 + i * 20
        mock_data.append(item)
    
    return mock_data
