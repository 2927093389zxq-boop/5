"""
市场调研示例 - 展示增强型爬虫和高级分析功能
Market Research Example - Demonstrate enhanced scraper and advanced analysis

本示例展示如何使用新的功能进行市场调研和竞品分析：
This example shows how to use new features for market research and competitive analysis:

1. 周期性采集 / Periodic scraping
2. 抽样策略 / Sampling strategy
3. 竞品矩阵分析 / Competitor matrix analysis
4. 价格分布图 / Price distribution charts
5. 关键词云 / Keyword cloud
6. 品牌集中度分析 / Brand concentration analysis
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_scraper import EnhancedScraper
from core.advanced_analysis import AdvancedAnalyzer
from core.periodic_scheduler import PeriodicScheduler, create_market_research_scheduler
from scrapers.amazon_scraper import AmazonScraper
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_enhanced_scraping():
    """
    示例1：使用增强型爬虫进行采集
    Example 1: Using enhanced scraper for data collection
    """
    print("\n" + "="*60)
    print("示例1：增强型爬虫采集 / Example 1: Enhanced Scraping")
    print("="*60 + "\n")
    
    # 创建增强型爬虫实例
    scraper = EnhancedScraper(
        delay_range=(2.0, 5.0),  # 2-5秒随机延时
        max_retries=3,
        cache_ttl_hours=24
    )
    
    # 示例URL列表
    urls = [
        "https://www.amazon.com/s?k=laptop",
        "https://www.amazon.com/s?k=wireless+mouse",
    ]
    
    print("✓ 创建增强型爬虫实例 / Enhanced scraper created")
    print(f"✓ 延时范围: {scraper.delay_range[0]}-{scraper.delay_range[1]}秒")
    print(f"✓ 最大重试: {scraper.max_retries}次")
    print(f"✓ 缓存有效期: {scraper.cache_ttl.total_seconds()/3600}小时")
    print(f"✓ User-Agent池: {len(scraper.USER_AGENTS)}个")
    
    # 注意：这里仅展示配置，实际爬取需要实现具体平台的解析逻辑
    print("\n[提示] 实际爬取需要实现具体平台的解析逻辑")


def example_2_sampling_strategy():
    """
    示例2：抽样采集策略
    Example 2: Sampling strategy
    """
    print("\n" + "="*60)
    print("示例2：抽样采集策略 / Example 2: Sampling Strategy")
    print("="*60 + "\n")
    
    # 使用Amazon爬虫进行实际采集
    scraper = AmazonScraper()
    
    # 采集多个类目的样本数据
    categories = {
        "Electronics": "https://www.amazon.com/s?k=electronics",
        "Books": "https://www.amazon.com/s?k=books",
        "Home": "https://www.amazon.com/s?k=home+kitchen"
    }
    
    print("抽样策略配置 / Sampling Strategy Configuration:")
    print(f"✓ 类目数量: {len(categories)}")
    print(f"✓ 每类目样本: 50-100个商品")
    print(f"✓ 总样本量: 150-300个商品")
    
    # 模拟采集（实际使用时取消注释）
    # all_products = []
    # for category, url in categories.items():
    #     print(f"\n采集类目: {category}")
    #     products = scraper.scrape_list_page(url, max_items=100)
    #     all_products.extend(products)
    #     print(f"✓ 采集完成: {len(products)}个商品")
    
    print("\n[提示] 实际采集时会从每个类目采集50-100个商品作为样本")


def example_3_competitor_analysis():
    """
    示例3：竞品矩阵分析
    Example 3: Competitor matrix analysis
    """
    print("\n" + "="*60)
    print("示例3：竞品矩阵分析 / Example 3: Competitor Analysis")
    print("="*60 + "\n")
    
    # 使用示例数据
    sample_products = [
        {
            'brand': 'Apple',
            'title': 'MacBook Pro',
            'price': '$1299.00',
            'rating': '4.7 out of 5 stars',
            'review_count': '2,456 ratings'
        },
        {
            'brand': 'Apple',
            'title': 'MacBook Air',
            'price': '$999.00',
            'rating': '4.8 out of 5 stars',
            'review_count': '3,210 ratings'
        },
        {
            'brand': 'Dell',
            'title': 'Dell XPS 13',
            'price': '$1099.00',
            'rating': '4.5 out of 5 stars',
            'review_count': '1,234 ratings'
        },
        {
            'brand': 'HP',
            'title': 'HP Pavilion',
            'price': '$799.00',
            'rating': '4.3 out of 5 stars',
            'review_count': '890 ratings'
        },
        {
            'brand': 'Lenovo',
            'title': 'ThinkPad X1',
            'price': '$1199.00',
            'rating': '4.6 out of 5 stars',
            'review_count': '1,567 ratings'
        }
    ]
    
    # 创建分析器
    analyzer = AdvancedAnalyzer(output_dir="data/analysis")
    
    # 执行竞品矩阵分析
    competitor_matrix = analyzer.analyze_competitor_matrix(sample_products, group_by='brand')
    
    print("竞品矩阵分析结果 / Competitor Matrix Results:")
    print(competitor_matrix.to_string())
    
    print("\n✓ 分析完成！竞品矩阵展示了各品牌的价格区间、评分和市场份额")


def example_4_price_distribution():
    """
    示例4：价格分布分析
    Example 4: Price distribution analysis
    """
    print("\n" + "="*60)
    print("示例4：价格分布分析 / Example 4: Price Distribution")
    print("="*60 + "\n")
    
    # 使用示例数据
    sample_products = [
        {'price': f'${price}.00'} 
        for price in [299, 399, 499, 599, 699, 799, 899, 999, 1099, 1199, 
                     1299, 1399, 1499, 399, 499, 599, 699, 799, 899, 999]
    ]
    
    # 创建分析器
    analyzer = AdvancedAnalyzer(output_dir="data/analysis")
    
    # 执行价格分布分析
    price_stats = analyzer.analyze_price_distribution(sample_products, save_plot=True)
    
    print("价格分布统计 / Price Distribution Statistics:")
    print(f"✓ 平均价格: ${price_stats['mean']:.2f}")
    print(f"✓ 中位数价格: ${price_stats['median']:.2f}")
    print(f"✓ 标准差: ${price_stats['std']:.2f}")
    print(f"✓ 价格范围: ${price_stats['min']:.2f} - ${price_stats['max']:.2f}")
    print(f"✓ 25分位数: ${price_stats['q25']:.2f}")
    print(f"✓ 75分位数: ${price_stats['q75']:.2f}")
    
    print("\n价格区间分布 / Price Range Distribution:")
    for range_name, count in price_stats['price_ranges'].items():
        print(f"  {range_name}: {count}个商品")
    
    print("\n✓ 价格分布图已保存到 data/analysis/ 目录")


def example_5_keyword_analysis():
    """
    示例5：关键词分析和词云
    Example 5: Keyword analysis and word cloud
    """
    print("\n" + "="*60)
    print("示例5：关键词分析 / Example 5: Keyword Analysis")
    print("="*60 + "\n")
    
    # 使用示例数据
    sample_products = [
        {'title': 'Wireless Gaming Mouse RGB LED Backlit 6 Buttons'},
        {'title': 'Mechanical Gaming Keyboard RGB Backlight Blue Switch'},
        {'title': 'Gaming Headset with Microphone LED Light'},
        {'title': 'RGB Gaming Mouse Pad Large Extended'},
        {'title': 'Ergonomic Gaming Chair RGB LED Lights'},
        {'title': 'Gaming Monitor 27 inch 144Hz RGB'},
        {'title': 'Wireless Gaming Headset RGB LED'},
        {'title': 'Gaming Laptop Intel Core i7 RGB Keyboard'},
        {'title': 'Gaming Desktop PC RGB Cooling System'},
        {'title': 'Gaming Graphics Card RGB LED Backplate'}
    ]
    
    # 创建分析器
    analyzer = AdvancedAnalyzer(output_dir="data/analysis")
    
    # 执行关键词分析
    keywords = analyzer.analyze_keywords(sample_products, text_field='title', 
                                        top_n=20, save_wordcloud=True)
    
    print("热门关键词 Top 20 / Top 20 Keywords:")
    for i, (word, freq) in enumerate(keywords.items(), 1):
        print(f"  {i:2d}. {word:20s} : {freq:3d}次")
    
    print("\n✓ 关键词云图已保存到 data/analysis/ 目录")


def example_6_brand_concentration():
    """
    示例6：品牌集中度分析
    Example 6: Brand concentration analysis
    """
    print("\n" + "="*60)
    print("示例6：品牌集中度分析 / Example 6: Brand Concentration")
    print("="*60 + "\n")
    
    # 使用示例数据
    sample_products = []
    brands = {
        'Apple': 15,
        'Samsung': 12,
        'Dell': 10,
        'HP': 8,
        'Lenovo': 7,
        'Asus': 6,
        'Acer': 5,
        'MSI': 4,
        'Razer': 3,
        'Others': 10
    }
    
    for brand, count in brands.items():
        for i in range(count):
            sample_products.append({
                'brand': brand,
                'title': f'{brand} Product {i+1}',
                'price': '$999.00'
            })
    
    # 创建分析器
    analyzer = AdvancedAnalyzer(output_dir="data/analysis")
    
    # 执行品牌集中度分析
    brand_analysis = analyzer.analyze_brand_concentration(sample_products)
    
    print("品牌集中度分析结果 / Brand Concentration Results:")
    print(f"✓ 总品牌数: {brand_analysis['total_brands']}")
    print(f"✓ 总商品数: {brand_analysis['total_products']}")
    print(f"✓ HHI指数: {brand_analysis['hhi_index']}")
    print(f"✓ CR4 (前4名集中度): {brand_analysis['cr4_percent']}%")
    print(f"✓ CR8 (前8名集中度): {brand_analysis['cr8_percent']}%")
    print(f"✓ 市场集中度类型: {brand_analysis['concentration_type']}")
    
    print("\n前10品牌市场份额 / Top 10 Brand Market Share:")
    for i, brand_info in enumerate(brand_analysis['top_brands'], 1):
        print(f"  {i:2d}. {brand_info['brand']:15s} : {brand_info['market_share_percent']:5.2f}% ({brand_info['count']}个商品)")
    
    print("\n✓ 品牌份额饼图已保存到 data/analysis/ 目录")


def example_7_comprehensive_report():
    """
    示例7：生成综合分析报告
    Example 7: Generate comprehensive analysis report
    """
    print("\n" + "="*60)
    print("示例7：综合分析报告 / Example 7: Comprehensive Report")
    print("="*60 + "\n")
    
    # 创建完整的示例数据集
    sample_products = []
    brands = ['Apple', 'Samsung', 'Dell', 'HP', 'Lenovo', 'Asus', 'Acer']
    
    for i in range(100):
        brand = brands[i % len(brands)]
        sample_products.append({
            'brand': brand,
            'title': f'{brand} Product {i+1} Gaming Laptop RGB LED Wireless',
            'price': f'${500 + (i * 10) % 1000}.00',
            'rating': f'{3.5 + (i % 3) * 0.5:.1f} out of 5 stars',
            'review_count': f'{(i + 1) * 50} ratings'
        })
    
    # 创建分析器
    analyzer = AdvancedAnalyzer(output_dir="data/analysis")
    
    # 生成综合报告
    print("正在生成综合分析报告...")
    report_path = analyzer.generate_comprehensive_report(
        sample_products,
        report_name=f"market_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    print(f"\n✓ 综合分析报告已生成: {report_path}")
    print("\n报告包含以下内容:")
    print("  - 竞品矩阵分析")
    print("  - 价格分布统计和图表")
    print("  - 关键词分析和词云")
    print("  - 品牌集中度分析和饼图")
    print("  - 市场趋势分析")


def example_8_periodic_scheduler():
    """
    示例8：周期性采集调度
    Example 8: Periodic scraping schedule
    """
    print("\n" + "="*60)
    print("示例8：周期性采集调度 / Example 8: Periodic Scheduler")
    print("="*60 + "\n")
    
    # 创建调度器
    scheduler = PeriodicScheduler()
    
    # 定义采集任务
    def sample_scrape_task():
        logger.info("执行每日市场调研任务...")
        # 这里添加实际的采集逻辑
        return "采集完成"
    
    # 添加每日任务（每天早上8点）
    scheduler.add_daily_job(
        'daily_market_research',
        sample_scrape_task,
        hour=8,
        minute=0
    )
    
    # 添加每周任务（每周一早上9点）
    scheduler.add_weekly_job(
        'weekly_market_report',
        sample_scrape_task,
        day_of_week='mon',
        hour=9,
        minute=0
    )
    
    print("✓ 调度任务配置成功！")
    print("\n已配置的任务 / Configured Jobs:")
    for job in scheduler.get_jobs():
        print(f"  - ID: {job['id']}")
        print(f"    类型: {job['type']}")
        print(f"    计划: {job['schedule']}")
        print(f"    下次运行: {job['next_run']}")
        print()
    
    print("[提示] 调度器已配置但未启动。实际使用时调用 scheduler.start() 启动")


def main():
    """运行所有示例 / Run all examples"""
    print("\n" + "="*60)
    print("市场调研和竞品分析示例程序")
    print("Market Research and Competitive Analysis Examples")
    print("="*60)
    
    examples = [
        ("增强型爬虫", example_1_enhanced_scraping),
        ("抽样采集策略", example_2_sampling_strategy),
        ("竞品矩阵分析", example_3_competitor_analysis),
        ("价格分布分析", example_4_price_distribution),
        ("关键词分析", example_5_keyword_analysis),
        ("品牌集中度分析", example_6_brand_concentration),
        ("综合分析报告", example_7_comprehensive_report),
        ("周期性调度", example_8_periodic_scheduler),
    ]
    
    print("\n可用的示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  0. 运行所有示例")
    
    try:
        choice = input("\n请选择要运行的示例 (0-8): ").strip()
        
        if choice == '0':
            # 运行所有示例
            for name, func in examples:
                try:
                    func()
                    input("\n按回车继续到下一个示例...")
                except KeyboardInterrupt:
                    print("\n\n用户中断")
                    break
                except Exception as e:
                    logger.error(f"运行示例时出错: {e}")
                    import traceback
                    traceback.print_exc()
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            # 运行选定的示例
            _, func = examples[int(choice) - 1]
            func()
        else:
            print("无效的选择")
    
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        logger.error(f"程序出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("示例程序结束 / Examples Completed")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
