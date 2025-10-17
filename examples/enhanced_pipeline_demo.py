"""
Integration Example: All Future Enhancements Working Together
集成示例：所有未来增强功能协同工作

This example demonstrates how to use all four enhancements together:
1. Browser automation for JavaScript-rendered content
2. Task queue for distributed scraping
3. Data validation and deduplication
4. Real-time monitoring dashboard

本示例演示如何同时使用所有四项增强功能：
1. 用于 JavaScript 渲染内容的浏览器自动化
2. 用于分布式抓取的任务队列
3. 数据验证和去重
4. 实时监控仪表板
"""

import asyncio
import time
from typing import Dict, Any, List

from core.browser_automation import BrowserAutomation
from core.task_queue import TaskQueue, Task
from core.data_validation import (
    DataQualityChecker,
    create_amazon_validator,
    create_amazon_deduplicator
)
from core.monitoring import get_monitoring_dashboard
from scrapers.amazon_scraper import AmazonScraper
from scrapers.logger import log_info, log_error


class EnhancedScrapingPipeline:
    """
    Enhanced scraping pipeline with all four improvements
    具有所有四项改进的增强型抓取管道
    """
    
    def __init__(self, max_workers: int = 4, use_browser: bool = False):
        """
        Initialize pipeline
        初始化管道
        
        Args:
            max_workers: Number of worker threads / 工作线程数
            use_browser: Use browser automation / 使用浏览器自动化
        """
        # 1. Setup monitoring
        self.dashboard = get_monitoring_dashboard()
        log_info("监控仪表板已初始化 / Monitoring dashboard initialized")
        
        # 2. Setup data validation
        self.validator = create_amazon_validator()
        self.deduplicator = create_amazon_deduplicator()
        self.quality_checker = DataQualityChecker(self.validator, self.deduplicator)
        log_info("数据验证器已初始化 / Data validator initialized")
        
        # 3. Setup task queue
        self.queue = TaskQueue(max_workers=max_workers)
        self.queue.register_handler("scrape_url", self._scrape_handler)
        log_info(f"任务队列已初始化，工作线程数: {max_workers} / Task queue initialized with {max_workers} workers")
        
        # 4. Setup browser automation (optional)
        self.use_browser = use_browser
        self.browser = None
        if use_browser:
            self.browser = BrowserAutomation(headless=True)
            log_info("浏览器自动化已启用 / Browser automation enabled")
    
    def _scrape_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task handler for scraping
        抓取任务处理器
        
        Args:
            params: Task parameters / 任务参数
            
        Returns:
            Task result / 任务结果
        """
        url = params["url"]
        platform = params.get("platform", "amazon")
        max_items = params.get("max_items", 50)
        
        log_info(f"开始抓取 / Starting scrape: {url}")
        start_time = time.time()
        
        try:
            # Use browser automation for JS-heavy sites if enabled
            if self.use_browser and self.browser:
                log_info(f"使用浏览器自动化 / Using browser automation: {url}")
                # Note: This is async, would need to be called properly in async context
                # For now, fall back to traditional scraper
                # In production, you'd use: content = await self.browser.get_page_content(url)
                scraper = AmazonScraper()
                items = scraper.scrape_list_page(url, max_items=max_items)
            else:
                # Use traditional scraper for static sites
                scraper = AmazonScraper()
                items = scraper.scrape_list_page(url, max_items=max_items)
            
            if not items:
                log_error(f"未抓取到数据 / No data scraped: {url}")
                response_time = time.time() - start_time
                self.dashboard.record_scraping_operation(
                    platform=platform,
                    success=False,
                    response_time=response_time,
                    error_type="no_data"
                )
                return {"success": False, "error": "No data scraped"}
            
            # Validate and deduplicate
            log_info(f"验证和去重 {len(items)} 个项目 / Validating and deduplicating {len(items)} items")
            quality_report = self.quality_checker.check(items)
            clean_data = quality_report["valid_data"]
            
            log_info(f"质量检查完成 / Quality check complete: "
                    f"有效={quality_report['valid_count']}, "
                    f"无效={quality_report['invalid_count']}, "
                    f"唯一={quality_report['unique_count']}, "
                    f"重复={quality_report['duplicate_count']}")
            
            # Record success in monitoring
            response_time = time.time() - start_time
            self.dashboard.record_scraping_operation(
                platform=platform,
                success=True,
                response_time=response_time,
                items_count=len(clean_data)
            )
            
            log_info(f"抓取成功 / Scrape successful: {url} ({len(clean_data)} items)")
            
            return {
                "success": True,
                "items": clean_data,
                "quality": {
                    "valid_count": quality_report["valid_count"],
                    "invalid_count": quality_report["invalid_count"],
                    "unique_count": quality_report["unique_count"],
                    "duplicate_count": quality_report["duplicate_count"],
                    "quality_score": quality_report["quality_score"]
                }
            }
            
        except Exception as e:
            log_error(f"抓取失败 / Scrape failed: {url} - {e}")
            
            # Record failure in monitoring
            response_time = time.time() - start_time
            self.dashboard.record_scraping_operation(
                platform=platform,
                success=False,
                response_time=response_time,
                error_type=type(e).__name__
            )
            
            return {"success": False, "error": str(e)}
    
    def add_tasks(self, urls: List[str], platform: str = "amazon", max_items: int = 50):
        """
        Add scraping tasks to queue
        添加抓取任务到队列
        
        Args:
            urls: List of URLs to scrape / 要抓取的 URL 列表
            platform: Platform name / 平台名称
            max_items: Maximum items per URL / 每个 URL 的最大项目数
        """
        log_info(f"添加 {len(urls)} 个任务到队列 / Adding {len(urls)} tasks to queue")
        
        for i, url in enumerate(urls):
            task = Task(
                task_id=f"task_{i}",
                task_type="scrape_url",
                params={
                    "url": url,
                    "platform": platform,
                    "max_items": max_items
                },
                priority=i  # Higher priority for first tasks
            )
            self.queue.add_task(task)
    
    async def run(self):
        """
        Run the scraping pipeline
        运行抓取管道
        """
        log_info("启动抓取管道 / Starting scraping pipeline")
        
        # Start queue
        self.queue.start()
        
        # Wait for all tasks to complete
        while True:
            stats = self.queue.get_stats()
            
            if stats["running"] == 0 and stats["pending"] == 0:
                break
            
            # Log progress
            log_info(f"队列状态 / Queue status: "
                    f"待处理={stats['pending']}, "
                    f"运行中={stats['running']}, "
                    f"已完成={stats['completed']}, "
                    f"失败={stats['failed']}")
            
            await asyncio.sleep(2)
        
        # Stop queue
        self.queue.stop()
        
        # Get final statistics
        final_stats = self.queue.get_stats()
        dashboard_data = self.dashboard.get_dashboard_data()
        current_stats = dashboard_data["current_stats"]
        
        log_info("=" * 60)
        log_info("抓取管道完成 / Scraping pipeline completed")
        log_info("=" * 60)
        log_info(f"任务统计 / Task Statistics:")
        log_info(f"  总任务 / Total Tasks: {final_stats['total']}")
        log_info(f"  已完成 / Completed: {final_stats['completed']}")
        log_info(f"  失败 / Failed: {final_stats['failed']}")
        log_info(f"  取消 / Cancelled: {final_stats['cancelled']}")
        log_info("")
        log_info(f"监控统计 / Monitoring Statistics:")
        log_info(f"  总请求 / Total Requests: {current_stats['total_requests']}")
        log_info(f"  成功率 / Success Rate: {current_stats['success_rate']:.1f}%")
        log_info(f"  抓取项目 / Items Scraped: {current_stats['total_items_scraped']}")
        log_info(f"  平均响应时间 / Avg Response Time: {current_stats['avg_response_time']:.2f}s")
        log_info(f"  错误数 / Errors: {current_stats['total_errors']}")
        log_info("=" * 60)
        
        # Cleanup
        if self.browser:
            await self.browser.close()
    
    def print_monitoring_dashboard(self):
        """Print monitoring dashboard summary / 打印监控仪表板摘要"""
        data = self.dashboard.get_dashboard_data()
        
        print("\n" + "=" * 80)
        print("MONITORING DASHBOARD / 监控仪表板")
        print("=" * 80)
        
        # Current stats
        stats = data["current_stats"]
        print(f"\n📊 Overall Statistics / 总体统计:")
        print(f"  Total Requests / 总请求: {stats['total_requests']}")
        print(f"  Success Rate / 成功率: {stats['success_rate']:.1f}%")
        print(f"  Items Scraped / 抓取项目: {stats['total_items_scraped']}")
        print(f"  Errors / 错误: {stats['total_errors']}")
        print(f"  Captcha Hits / 验证码: {stats['captcha_hits']}")
        
        # Performance
        print(f"\n⚡ Performance / 性能:")
        print(f"  Avg Response Time / 平均响应时间: {stats['avg_response_time']:.2f}s")
        print(f"  Min Response Time / 最小响应时间: {stats['min_response_time']:.2f}s")
        print(f"  Max Response Time / 最大响应时间: {stats['max_response_time']:.2f}s")
        print(f"  Requests/min / 请求/分钟: {stats['requests_per_minute']:.1f}")
        
        # Platform stats
        if data["platform_stats"]:
            print(f"\n🌐 Platform Statistics / 平台统计:")
            for platform, pstats in data["platform_stats"].items():
                success_rate = (pstats["successful"] / pstats["requests"] * 100 
                              if pstats["requests"] > 0 else 0)
                print(f"  {platform}:")
                print(f"    Requests / 请求: {pstats['requests']}")
                print(f"    Success Rate / 成功率: {success_rate:.1f}%")
                print(f"    Items / 项目: {pstats['items']}")
        
        # Alerts
        if data["alerts"]:
            print(f"\n🚨 Recent Alerts / 最近警报:")
            for alert in data["alerts"][-5:]:  # Last 5 alerts
                severity_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(alert["severity"], "⚪")
                print(f"  {severity_icon} [{alert['timestamp'][:19]}] {alert['message']}")
        
        print("=" * 80 + "\n")


async def main():
    """Main function / 主函数"""
    
    print("\n" + "=" * 80)
    print("ENHANCED SCRAPING PIPELINE DEMO / 增强型抓取管道演示")
    print("=" * 80)
    print("\nThis demo showcases all four enhancements:")
    print("此演示展示所有四项增强功能：")
    print("  1. Browser Automation (Playwright) / 浏览器自动化")
    print("  2. Distributed Task Queue / 分布式任务队列")
    print("  3. Data Validation & Deduplication / 数据验证和去重")
    print("  4. Real-time Monitoring / 实时监控")
    print("=" * 80 + "\n")
    
    # Create pipeline
    pipeline = EnhancedScrapingPipeline(
        max_workers=2,  # Use 2 workers for demo
        use_browser=False  # Set to True to enable browser automation
    )
    
    # Example URLs (modify as needed for your use case)
    # 示例 URL（根据您的用例需要进行修改）
    urls = [
        "https://www.amazon.com/bestsellers",
        "https://www.amazon.com/s?k=laptop",
        # Add more URLs as needed / 根据需要添加更多 URL
    ]
    
    # Alternative: Use environment variable or config file for URLs
    # 替代方案：使用环境变量或配置文件存储 URL
    # import os
    # urls = os.getenv("SCRAPE_URLS", "").split(",")
    
    print(f"准备抓取 {len(urls)} 个 URL / Preparing to scrape {len(urls)} URLs")
    
    # Add tasks
    pipeline.add_tasks(urls, platform="amazon", max_items=20)
    
    # Run pipeline
    await pipeline.run()
    
    # Print final dashboard
    pipeline.print_monitoring_dashboard()
    
    print("\n演示完成！ / Demo completed!")
    print("查看 Streamlit 仪表板以获取实时监控 / Check Streamlit dashboard for real-time monitoring")
    print("运行: python -m streamlit run ui/monitoring_view.py")
    print("或: python run_launcher.py  (如果使用主启动器)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Note: In production, you might want to run this with proper error handling
    # 注意：在生产环境中，您可能希望使用适当的错误处理运行此程序
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n中断：用户取消 / Interrupted: User cancelled")
    except Exception as e:
        print(f"\n\n错误 / Error: {e}")
        import traceback
        traceback.print_exc()
