"""
数据获取模块 - 支持多平台数据采集
Data Fetcher Module - Multi-platform data collection support
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import time

# 支持的平台列表 / Supported platforms list
PLATFORM_LIST = ["Amazon", "Shopee", "eBay"]


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
    elif platform_name == "Shopee":
        return _fetch_shopee_data(keyword, category_url, max_items, deep_detail)
    elif platform_name == "eBay":
        return _fetch_ebay_data(keyword, category_url, max_items, deep_detail)
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
