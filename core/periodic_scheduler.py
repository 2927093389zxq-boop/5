"""
周期性采集调度器 - 支持每日/每周自动采集
Periodic Scraping Scheduler - Support daily/weekly automated scraping

功能特性 / Features:
- 定时任务管理 / Scheduled task management
- 每日/每周采集 / Daily/weekly scraping
- 自动数据汇总 / Automatic data aggregation
- 邮件通知 / Email notifications
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
import traceback

logger = logging.getLogger(__name__)


class PeriodicScheduler:
    """周期性调度器 / Periodic Scheduler"""
    
    def __init__(self, config_file: str = "config/scheduler_config.json"):
        """
        初始化调度器
        
        Args:
            config_file: 配置文件路径 / Config file path
        """
        self.scheduler = BackgroundScheduler()
        self.config_file = Path(config_file)
        self.jobs = {}
        
        # 加载配置
        self.config = self._load_config()
        
        logger.info("Periodic scheduler initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置 / Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # 默认配置
        return {
            'timezone': 'Asia/Shanghai',
            'daily_scrape_time': '08:00',
            'weekly_scrape_day': 'monday',
            'weekly_scrape_time': '09:00',
            'enable_notifications': False,
            'notification_email': ''
        }
    
    def _save_config(self):
        """保存配置 / Save configuration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def add_daily_job(self, 
                     job_id: str,
                     func: Callable,
                     hour: int = 8,
                     minute: int = 0,
                     **kwargs) -> bool:
        """
        添加每日任务
        Add daily job
        
        Args:
            job_id: 任务ID / Job ID
            func: 要执行的函数 / Function to execute
            hour: 小时(0-23) / Hour (0-23)
            minute: 分钟(0-59) / Minute (0-59)
            **kwargs: 传递给函数的参数 / Arguments to pass to function
            
        Returns:
            是否成功添加 / Whether successfully added
        """
        try:
            # 包装函数以捕获异常
            def wrapped_func():
                try:
                    logger.info(f"Starting daily job: {job_id}")
                    result = func(**kwargs)
                    logger.info(f"Daily job completed: {job_id}")
                    return result
                except Exception as e:
                    logger.error(f"Error in daily job {job_id}: {e}")
                    logger.error(traceback.format_exc())
            
            job = self.scheduler.add_job(
                wrapped_func,
                CronTrigger(hour=hour, minute=minute),
                id=job_id,
                name=f"Daily: {job_id}",
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                'type': 'daily',
                'schedule': f"{hour:02d}:{minute:02d}",
                'job': job
            }
            
            logger.info(f"Daily job added: {job_id} at {hour:02d}:{minute:02d}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding daily job: {e}")
            return False
    
    def add_weekly_job(self,
                      job_id: str,
                      func: Callable,
                      day_of_week: str = 'mon',
                      hour: int = 9,
                      minute: int = 0,
                      **kwargs) -> bool:
        """
        添加每周任务
        Add weekly job
        
        Args:
            job_id: 任务ID / Job ID
            func: 要执行的函数 / Function to execute
            day_of_week: 星期几(mon/tue/wed/thu/fri/sat/sun) / Day of week
            hour: 小时(0-23) / Hour (0-23)
            minute: 分钟(0-59) / Minute (0-59)
            **kwargs: 传递给函数的参数 / Arguments to pass to function
            
        Returns:
            是否成功添加 / Whether successfully added
        """
        try:
            # 包装函数以捕获异常
            def wrapped_func():
                try:
                    logger.info(f"Starting weekly job: {job_id}")
                    result = func(**kwargs)
                    logger.info(f"Weekly job completed: {job_id}")
                    return result
                except Exception as e:
                    logger.error(f"Error in weekly job {job_id}: {e}")
                    logger.error(traceback.format_exc())
            
            job = self.scheduler.add_job(
                wrapped_func,
                CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
                id=job_id,
                name=f"Weekly: {job_id}",
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                'type': 'weekly',
                'day': day_of_week,
                'schedule': f"{day_of_week} {hour:02d}:{minute:02d}",
                'job': job
            }
            
            logger.info(f"Weekly job added: {job_id} on {day_of_week} at {hour:02d}:{minute:02d}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding weekly job: {e}")
            return False
    
    def add_interval_job(self,
                        job_id: str,
                        func: Callable,
                        hours: int = 0,
                        minutes: int = 0,
                        seconds: int = 0,
                        **kwargs) -> bool:
        """
        添加间隔任务
        Add interval job
        
        Args:
            job_id: 任务ID / Job ID
            func: 要执行的函数 / Function to execute
            hours: 间隔小时数 / Interval hours
            minutes: 间隔分钟数 / Interval minutes
            seconds: 间隔秒数 / Interval seconds
            **kwargs: 传递给函数的参数 / Arguments to pass to function
            
        Returns:
            是否成功添加 / Whether successfully added
        """
        try:
            # 包装函数以捕获异常
            def wrapped_func():
                try:
                    logger.info(f"Starting interval job: {job_id}")
                    result = func(**kwargs)
                    logger.info(f"Interval job completed: {job_id}")
                    return result
                except Exception as e:
                    logger.error(f"Error in interval job {job_id}: {e}")
                    logger.error(traceback.format_exc())
            
            from apscheduler.triggers.interval import IntervalTrigger
            
            job = self.scheduler.add_job(
                wrapped_func,
                IntervalTrigger(hours=hours, minutes=minutes, seconds=seconds),
                id=job_id,
                name=f"Interval: {job_id}",
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                'type': 'interval',
                'interval': f"{hours}h {minutes}m {seconds}s",
                'job': job
            }
            
            logger.info(f"Interval job added: {job_id} every {hours}h {minutes}m {seconds}s")
            return True
            
        except Exception as e:
            logger.error(f"Error adding interval job: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """
        移除任务
        Remove job
        
        Args:
            job_id: 任务ID / Job ID
            
        Returns:
            是否成功移除 / Whether successfully removed
        """
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"Job removed: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """
        暂停任务
        Pause job
        
        Args:
            job_id: 任务ID / Job ID
            
        Returns:
            是否成功暂停 / Whether successfully paused
        """
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job paused: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """
        恢复任务
        Resume job
        
        Args:
            job_id: 任务ID / Job ID
            
        Returns:
            是否成功恢复 / Whether successfully resumed
        """
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job resumed: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")
            return False
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """
        获取所有任务
        Get all jobs
        
        Returns:
            任务列表 / Job list
        """
        jobs_list = []
        for job_id, job_info in self.jobs.items():
            job = job_info['job']
            jobs_list.append({
                'id': job_id,
                'name': job.name,
                'type': job_info['type'],
                'schedule': job_info.get('schedule', job_info.get('interval', '')),
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'pending': job.pending
            })
        return jobs_list
    
    def start(self):
        """启动调度器 / Start scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def shutdown(self, wait: bool = True):
        """
        关闭调度器
        Shutdown scheduler
        
        Args:
            wait: 是否等待任务完成 / Whether to wait for jobs to complete
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Scheduler shutdown")
    
    def is_running(self) -> bool:
        """检查调度器是否运行 / Check if scheduler is running"""
        return self.scheduler.running
    
    def run_job_now(self, job_id: str) -> bool:
        """
        立即运行任务
        Run job immediately
        
        Args:
            job_id: 任务ID / Job ID
            
        Returns:
            是否成功运行 / Whether successfully run
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=datetime.now())
                logger.info(f"Job {job_id} scheduled to run immediately")
                return True
            else:
                logger.error(f"Job {job_id} not found")
                return False
        except Exception as e:
            logger.error(f"Error running job {job_id}: {e}")
            return False


def create_market_research_scheduler(
    scraper_func: Callable,
    analyzer_func: Callable,
    urls: List[str],
    daily: bool = True,
    weekly: bool = False,
    daily_hour: int = 8,
    weekly_day: str = 'mon',
    weekly_hour: int = 9
) -> PeriodicScheduler:
    """
    创建市场调研调度器
    Create market research scheduler
    
    Args:
        scraper_func: 爬虫函数 / Scraper function
        analyzer_func: 分析函数 / Analyzer function
        urls: URL列表 / URL list
        daily: 是否每日执行 / Whether to run daily
        weekly: 是否每周执行 / Whether to run weekly
        daily_hour: 每日执行小时 / Daily execution hour
        weekly_day: 每周执行星期 / Weekly execution day
        weekly_hour: 每周执行小时 / Weekly execution hour
        
    Returns:
        调度器实例 / Scheduler instance
    """
    scheduler = PeriodicScheduler()
    
    # 爬取和分析流程
    def scrape_and_analyze():
        logger.info("Starting scrape and analyze workflow...")
        
        # 1. 执行爬取
        products = scraper_func(urls=urls)
        
        if products:
            logger.info(f"Scraped {len(products)} products")
            
            # 2. 执行分析
            report = analyzer_func(products=products)
            logger.info(f"Analysis completed: {report}")
        else:
            logger.warning("No products scraped")
    
    # 添加任务
    if daily:
        scheduler.add_daily_job(
            'market_research_daily',
            scrape_and_analyze,
            hour=daily_hour,
            minute=0
        )
    
    if weekly:
        scheduler.add_weekly_job(
            'market_research_weekly',
            scrape_and_analyze,
            day_of_week=weekly_day,
            hour=weekly_hour,
            minute=0
        )
    
    logger.info(f"Market research scheduler created (daily={daily}, weekly={weekly})")
    return scheduler


# 使用示例 / Usage example
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建调度器
    scheduler = PeriodicScheduler()
    
    # 示例：添加每日任务
    def daily_task():
        print(f"Daily task running at {datetime.now()}")
        return "Daily task completed"
    
    scheduler.add_daily_job('test_daily', daily_task, hour=10, minute=30)
    
    # 启动调度器
    scheduler.start()
    
    # 查看任务
    print("Scheduled jobs:")
    for job in scheduler.get_jobs():
        print(f"  - {job}")
    
    # 保持运行
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
