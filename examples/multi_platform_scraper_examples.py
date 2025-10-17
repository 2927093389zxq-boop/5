"""
多平台爬虫示例脚本
Multi-Platform Scraper Example Script

演示如何使用多平台爬虫采集不同电商平台的数据
Demonstrates how to use multi-platform scraper to collect data from different e-commerce platforms
"""

import sys
import os
# 添加项目根目录到Python路径 / Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.multi_platform_scraper import scrape_platform, get_scraper, PLATFORM_SCRAPERS
import json


def example_1_quick_scrape():
    """
    示例1: 快速采集单个平台
    Example 1: Quick scraping from a single platform
    """
    print("\n" + "="*60)
    print("示例1: 快速采集 / Example 1: Quick Scraping")
    print("="*60)
    
    # 使用便捷函数采集 / Use convenience function to scrape
    products = scrape_platform(
        platform_name="ebay",
        url="https://www.ebay.com/sch/i.html?_nkw=laptop",
        max_items=10,
        deep_detail=False
    )
    
    print(f"\n采集到 {len(products)} 个商品 / Scraped {len(products)} products")
    if products:
        print("\n第一个商品示例 / First product example:")
        print(json.dumps(products[0], indent=2, ensure_ascii=False))


def example_2_use_scraper_class():
    """
    示例2: 使用爬虫类
    Example 2: Using scraper class
    """
    print("\n" + "="*60)
    print("示例2: 使用爬虫类 / Example 2: Using Scraper Class")
    print("="*60)
    
    # 创建爬虫实例 / Create scraper instance
    scraper = get_scraper("shopee")
    
    print(f"\n平台名称 / Platform name: {scraper.PLATFORM_NAME}")
    print(f"数据目录 / Data directory: {scraper.data_dir}")
    
    # 运行采集 / Run scraping
    products = scraper.run(
        url="https://shopee.ph/search?keyword=phone",
        max_items=10,
        deep_detail=False
    )
    
    print(f"\n采集到 {len(products)} 个商品 / Scraped {len(products)} products")


def example_3_custom_configuration():
    """
    示例3: 自定义配置
    Example 3: Custom configuration
    """
    print("\n" + "="*60)
    print("示例3: 自定义配置 / Example 3: Custom Configuration")
    print("="*60)
    
    scraper = get_scraper("temu")
    
    # 自定义等待时间 / Customize wait time
    print(f"默认等待时间 / Default wait time: {scraper.wait_time}")
    scraper.wait_time = {"min": 2.0, "max": 4.0}
    print(f"修改后等待时间 / Modified wait time: {scraper.wait_time}")
    
    # 自定义最大重试次数 / Customize max retries
    print(f"默认重试次数 / Default max retries: {scraper.max_retries}")
    scraper.max_retries = 5
    print(f"修改后重试次数 / Modified max retries: {scraper.max_retries}")
    
    print("\n配置已更新 / Configuration updated")


def example_4_batch_scraping():
    """
    示例4: 批量采集多个平台
    Example 4: Batch scraping from multiple platforms
    """
    print("\n" + "="*60)
    print("示例4: 批量采集 / Example 4: Batch Scraping")
    print("="*60)
    
    # 选择几个平台进行演示 / Select a few platforms for demonstration
    platforms = ["ebay", "etsy", "mercari"]
    
    all_products = []
    
    for platform in platforms:
        try:
            print(f"\n正在采集 {platform} / Scraping {platform}...")
            scraper = get_scraper(platform)
            
            # 注意：实际使用时需要提供有效URL并设置enable_scraping=True
            # Note: Provide valid URL and set enable_scraping=True for actual use
            enable_scraping = False  # 设为True以启用实际采集 / Set to True to enable actual scraping
            
            if enable_scraping:
                # 实际采集代码 / Actual scraping code
                url = f"https://{platform}.com/search?q=example"
                products = scraper.run(url, max_items=10)
            else:
                # 演示模式：跳过实际网络请求 / Demo mode: skip actual network requests
                products = []
            
            print(f"  {platform}: 采集到 {len(products)} 个商品")
            all_products.extend(products)
            
        except Exception as e:
            print(f"  {platform}: 失败 - {e}")
    
    print(f"\n总计采集: {len(all_products)} 个商品 / Total scraped: {len(all_products)} products")
    print("\n提示: 设置 enable_scraping=True 以启用实际采集")
    print("Tip: Set enable_scraping=True to enable actual scraping")


def example_5_list_all_platforms():
    """
    示例5: 列出所有支持的平台
    Example 5: List all supported platforms
    """
    print("\n" + "="*60)
    print("示例5: 支持的平台列表 / Example 5: Supported Platforms List")
    print("="*60)
    
    print(f"\n总计支持 {len(PLATFORM_SCRAPERS)} 个平台 / Total {len(PLATFORM_SCRAPERS)} platforms supported:\n")
    
    for i, platform in enumerate(sorted(PLATFORM_SCRAPERS.keys()), 1):
        scraper_class = PLATFORM_SCRAPERS[platform]
        scraper = scraper_class()
        print(f"{i:2d}. {platform:20s} - {scraper.PLATFORM_NAME}")


def example_6_error_handling():
    """
    示例6: 错误处理演示
    Example 6: Error handling demonstration
    """
    print("\n" + "="*60)
    print("示例6: 错误处理 / Example 6: Error Handling")
    print("="*60)
    
    scraper = get_scraper("lazada")
    
    print("\n爬虫自动处理以下错误 / Scraper automatically handles:")
    print("- 网络超时 / Network timeout")
    print("- HTTP 403/503 错误 / HTTP 403/503 errors")
    print("- 验证码页面 / Captcha pages")
    print("- 缺失的HTML元素 / Missing HTML elements")
    print("- 页面结构变化 / Page structure changes")
    
    print("\n重试配置 / Retry configuration:")
    print(f"- 最大重试次数 / Max retries: {scraper.max_retries}")
    print(f"- 等待时间 / Wait time: {scraper.wait_time}")


def example_7_data_format():
    """
    示例7: 数据格式展示
    Example 7: Data format demonstration
    """
    print("\n" + "="*60)
    print("示例7: 数据格式 / Example 7: Data Format")
    print("="*60)
    
    print("\n基础数据格式（所有平台）/ Basic data format (all platforms):")
    basic_format = {
        "platform": "ebay",
        "title": "Product Name",
        "price": "$19.99",
        "url": "https://ebay.com/item/...",
        "image": "https://..."
    }
    print(json.dumps(basic_format, indent=2))
    
    print("\n平台特定字段示例 / Platform-specific fields example:")
    
    print("\nShopee:")
    shopee_format = {
        "platform": "shopee",
        "title": "Product Name",
        "price": "₱299",
        "sold": "1.2k sold",
        "location": "Metro Manila"
    }
    print(json.dumps(shopee_format, indent=2))
    
    print("\neBay:")
    ebay_format = {
        "platform": "ebay",
        "title": "Product Name",
        "price": "$25.99",
        "condition": "New",
        "shipping": "Free shipping"
    }
    print(json.dumps(ebay_format, indent=2))


def example_8_save_data():
    """
    示例8: 数据保存
    Example 8: Data saving
    """
    print("\n" + "="*60)
    print("示例8: 数据保存 / Example 8: Data Saving")
    print("="*60)
    
    scraper = get_scraper("tiktokshop")
    
    # 模拟数据 / Mock data
    test_data = [
        {
            "platform": "tiktokshop",
            "title": "Test Product 1",
            "price": "$19.99"
        },
        {
            "platform": "tiktokshop",
            "title": "Test Product 2",
            "price": "$29.99"
        }
    ]
    
    # 保存数据 / Save data
    filepath = scraper.save_data(test_data, filename="example_tiktokshop.json")
    
    if filepath:
        print(f"\n数据已保存到 / Data saved to: {filepath}")
        print("\n保存的数据包含 / Saved data contains:")
        print("- platform: 平台名称 / Platform name")
        print("- items: 商品列表 / Product list")
        print("- total_count: 总数量 / Total count")
        print("- scraped_at: 采集时间 / Scraping time")


def main():
    """主函数 / Main function"""
    print("\n" + "="*60)
    print("多平台爬虫示例脚本")
    print("Multi-Platform Scraper Example Script")
    print("="*60)
    
    # 运行所有示例 / Run all examples
    examples = [
        example_5_list_all_platforms,    # 先列出所有平台 / List platforms first
        example_6_error_handling,        # 错误处理 / Error handling
        example_7_data_format,           # 数据格式 / Data format
        example_3_custom_configuration,  # 自定义配置 / Custom config
        # example_1_quick_scrape,        # 实际采集示例（需要网络）/ Actual scraping (needs network)
        # example_2_use_scraper_class,   # 实际采集示例（需要网络）/ Actual scraping (needs network)
        # example_4_batch_scraping,      # 批量采集（需要网络）/ Batch scraping (needs network)
        example_8_save_data,             # 数据保存 / Data saving
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n示例执行失败 / Example failed: {e}")
    
    print("\n" + "="*60)
    print("所有示例执行完成 / All examples completed")
    print("="*60)
    print("\n查看详细文档 / See detailed documentation:")
    print("docs/MULTI_PLATFORM_SCRAPER_GUIDE.md")
    print("\n")


if __name__ == "__main__":
    main()
