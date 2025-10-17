#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Amazon爬虫使用示例
Amazon Scraper Usage Examples

演示如何使用Amazon爬虫进行数据采集
Demonstrates how to use Amazon scraper for data collection
"""

import sys
import os

# 添加项目根目录到路径 / Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scrapers.amazon_scraper import AmazonScraper, scrape_amazon
import json


def example1_basic_scraping():
    """
    示例1: 基础采集
    Example 1: Basic scraping
    """
    print("=" * 60)
    print("示例1: 基础采集 / Example 1: Basic Scraping")
    print("=" * 60)
    
    # 创建爬虫实例 / Create scraper instance
    scraper = AmazonScraper()
    
    # 采集搜索结果页 / Scrape search results page
    url = "https://www.amazon.com/s?k=laptop"
    print(f"\n正在采集 / Scraping: {url}")
    
    products = scraper.scrape_list_page(url, max_items=10)
    
    print(f"\n✅ 采集完成，共 {len(products)} 个商品 / Completed, {len(products)} products")
    
    if products:
        print("\n前3个商品预览 / First 3 products preview:")
        for i, product in enumerate(products[:3], 1):
            print(f"\n商品 {i} / Product {i}:")
            print(f"  标题 / Title: {product.get('title', 'N/A')[:50]}...")
            print(f"  价格 / Price: {product.get('price', 'N/A')}")
            print(f"  评分 / Rating: {product.get('rating', 'N/A')}")
            print(f"  ASIN: {product.get('asin', 'N/A')}")


def example2_detail_scraping():
    """
    示例2: 详情页采集
    Example 2: Detail page scraping
    """
    print("\n" + "=" * 60)
    print("示例2: 详情页采集 / Example 2: Detail Page Scraping")
    print("=" * 60)
    
    scraper = AmazonScraper()
    
    # 使用示例ASIN / Use example ASIN
    asin = "B08N5WRWNW"  # 示例商品ASIN / Example product ASIN
    print(f"\n正在采集商品详情 / Scraping product detail: {asin}")
    
    detail = scraper.scrape_product_detail(asin)
    
    if detail:
        print("\n✅ 详情采集完成 / Detail scraping completed")
        print(f"\n商品详情 / Product Detail:")
        print(f"  标题 / Title: {detail.get('title', 'N/A')[:50]}...")
        print(f"  价格 / Price: {detail.get('price', 'N/A')}")
        print(f"  评分 / Rating: {detail.get('rating', 'N/A')}")
        print(f"  评论数 / Reviews: {detail.get('review_count', 'N/A')}")
        print(f"  品牌 / Brand: {detail.get('brand', 'N/A')}")


def example3_save_data():
    """
    示例3: 数据保存
    Example 3: Data saving
    """
    print("\n" + "=" * 60)
    print("示例3: 数据保存 / Example 3: Data Saving")
    print("=" * 60)
    
    scraper = AmazonScraper()
    
    # 模拟采集数据 / Mock scraped data
    sample_data = [
        {
            "asin": "TEST001",
            "title": "Sample Product 1",
            "price": "$29.99",
            "rating": "4.5 out of 5 stars",
            "url": "https://amazon.com/dp/TEST001"
        },
        {
            "asin": "TEST002",
            "title": "Sample Product 2",
            "price": "$39.99",
            "rating": "4.8 out of 5 stars",
            "url": "https://amazon.com/dp/TEST002"
        }
    ]
    
    print(f"\n保存 {len(sample_data)} 个商品数据 / Saving {len(sample_data)} products")
    
    filepath = scraper.save_data(sample_data, filename="example_products.json")
    
    print(f"✅ 数据已保存到 / Data saved to: {filepath}")
    
    # 读取并验证 / Read and verify
    with open(filepath, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    
    print(f"\n验证 / Verification:")
    print(f"  总数量 / Total count: {saved_data['total_count']}")
    print(f"  采集时间 / Scraped at: {saved_data['scraped_at']}")
    
    # 清理示例文件 / Cleanup example file
    os.remove(filepath)
    print(f"\n✅ 示例文件已清理 / Example file cleaned up")


def example4_convenience_function():
    """
    示例4: 使用便捷函数
    Example 4: Using convenience function
    """
    print("\n" + "=" * 60)
    print("示例4: 使用便捷函数 / Example 4: Using Convenience Function")
    print("=" * 60)
    
    url = "https://www.amazon.com/bestsellers"
    print(f"\n使用便捷函数采集 / Using convenience function to scrape:")
    print(f"URL: {url}")
    
    # 注意：这会实际访问Amazon，可能需要一些时间
    # Note: This will actually visit Amazon, may take some time
    # 在演示模式下，我们跳过实际执行
    # In demo mode, we skip actual execution
    
    print("\n代码示例 / Code example:")
    print("""
    from scrapers.amazon_scraper import scrape_amazon
    
    # 快速采集 / Quick scraping
    products = scrape_amazon(
        url="https://www.amazon.com/bestsellers",
        max_items=50,
        deep_detail=False
    )
    
    # 带详情采集 / With detail scraping
    products_with_detail = scrape_amazon(
        url="https://www.amazon.com/s?k=headphones",
        max_items=20,
        deep_detail=True
    )
    """)
    
    print("\n💡 提示: 实际使用时取消注释上面的代码")
    print("💡 Tip: Uncomment the code above for actual usage")


def example5_batch_urls():
    """
    示例5: 批量URL采集
    Example 5: Batch URL scraping
    """
    print("\n" + "=" * 60)
    print("示例5: 批量URL采集 / Example 5: Batch URL Scraping")
    print("=" * 60)
    
    urls = [
        "https://www.amazon.com/s?k=laptop",
        "https://www.amazon.com/s?k=headphones",
        "https://www.amazon.com/bestsellers"
    ]
    
    print(f"\n准备采集 {len(urls)} 个URL / Preparing to scrape {len(urls)} URLs:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    print("\n代码示例 / Code example:")
    print("""
    from core.crawl.dispatcher import run_batch
    
    # 批量采集 / Batch scraping
    run_batch(urls, storage_mode="local")
    """)
    
    print("\n💡 提示: 使用dispatcher可以自动处理多个URL")
    print("💡 Tip: Use dispatcher to automatically handle multiple URLs")


def main():
    """
    主函数：运行所有示例
    Main function: Run all examples
    """
    print("\n" + "=" * 60)
    print("Amazon爬虫使用示例集")
    print("Amazon Scraper Usage Examples")
    print("=" * 60)
    
    try:
        # 运行基础示例 / Run basic examples
        example3_save_data()  # 只运行不需要网络请求的示例
        
        print("\n" + "=" * 60)
        print("其他示例 / Other Examples")
        print("=" * 60)
        print("\n以下示例需要实际网络请求，演示模式下跳过:")
        print("The following examples require actual network requests, skipped in demo mode:")
        print("  - 示例1: 基础采集 / Example 1: Basic Scraping")
        print("  - 示例2: 详情页采集 / Example 2: Detail Page Scraping")
        print("  - 示例4: 便捷函数 / Example 4: Convenience Function")
        print("  - 示例5: 批量采集 / Example 5: Batch Scraping")
        
        print("\n💡 提示: 修改脚本以运行其他示例")
        print("💡 Tip: Modify the script to run other examples")
        
        example4_convenience_function()
        example5_batch_urls()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断 / User interrupted")
    except Exception as e:
        print(f"\n\n❌ 错误 / Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 所有示例演示完成 / All examples demonstrated")
    print("=" * 60)
    print("\n查看更多文档 / See more documentation:")
    print("  - README.md")
    print("  - scrapers/amazon_scraper.py")
    print("  - test/unit/test_amazon_scraper.py")
    print()


if __name__ == "__main__":
    main()
