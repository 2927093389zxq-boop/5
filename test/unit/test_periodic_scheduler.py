"""
Unit tests for periodic scheduler module
周期性调度器模块单元测试
"""

import unittest
import tempfile
import os
import time
from datetime import datetime

from core.periodic_scheduler import PeriodicScheduler


class TestPeriodicScheduler(unittest.TestCase):
    """周期性调度器测试类 / Periodic Scheduler Test Class"""
    
    def setUp(self):
        """测试前设置 / Setup before tests"""
        self.config_file = tempfile.mktemp(suffix='.json')
        self.scheduler = PeriodicScheduler(config_file=self.config_file)
        self.test_results = []
    
    def tearDown(self):
        """测试后清理 / Cleanup after tests"""
        if self.scheduler.is_running():
            self.scheduler.shutdown(wait=False)
        
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
    
    def test_initialization(self):
        """测试初始化 / Test initialization"""
        self.assertIsNotNone(self.scheduler)
        self.assertIsNotNone(self.scheduler.config)
        self.assertFalse(self.scheduler.is_running())
    
    def test_add_daily_job(self):
        """测试添加每日任务 / Test adding daily job"""
        def test_job():
            self.test_results.append('daily')
            return 'daily completed'
        
        success = self.scheduler.add_daily_job('test_daily', test_job, hour=10, minute=30)
        
        self.assertTrue(success)
        self.assertIn('test_daily', self.scheduler.jobs)
        self.assertEqual(self.scheduler.jobs['test_daily']['type'], 'daily')
        self.assertEqual(self.scheduler.jobs['test_daily']['schedule'], '10:30')
    
    def test_add_weekly_job(self):
        """测试添加每周任务 / Test adding weekly job"""
        def test_job():
            self.test_results.append('weekly')
            return 'weekly completed'
        
        success = self.scheduler.add_weekly_job(
            'test_weekly',
            test_job,
            day_of_week='mon',
            hour=9,
            minute=0
        )
        
        self.assertTrue(success)
        self.assertIn('test_weekly', self.scheduler.jobs)
        self.assertEqual(self.scheduler.jobs['test_weekly']['type'], 'weekly')
        self.assertEqual(self.scheduler.jobs['test_weekly']['day'], 'mon')
    
    def test_add_interval_job(self):
        """测试添加间隔任务 / Test adding interval job"""
        def test_job():
            self.test_results.append('interval')
            return 'interval completed'
        
        success = self.scheduler.add_interval_job(
            'test_interval',
            test_job,
            hours=1,
            minutes=30,
            seconds=0
        )
        
        self.assertTrue(success)
        self.assertIn('test_interval', self.scheduler.jobs)
        self.assertEqual(self.scheduler.jobs['test_interval']['type'], 'interval')
    
    def test_remove_job(self):
        """测试移除任务 / Test removing job"""
        def test_job():
            return 'test'
        
        # Add job
        self.scheduler.add_daily_job('test_remove', test_job, hour=10)
        self.assertIn('test_remove', self.scheduler.jobs)
        
        # Remove job
        success = self.scheduler.remove_job('test_remove')
        
        self.assertTrue(success)
        self.assertNotIn('test_remove', self.scheduler.jobs)
    
    def test_pause_resume_job(self):
        """测试暂停和恢复任务 / Test pausing and resuming job"""
        def test_job():
            return 'test'
        
        # Add job
        self.scheduler.add_daily_job('test_pause', test_job, hour=10)
        
        # Pause job
        success = self.scheduler.pause_job('test_pause')
        self.assertTrue(success)
        
        # Resume job
        success = self.scheduler.resume_job('test_pause')
        self.assertTrue(success)
    
    def test_get_jobs(self):
        """测试获取任务列表 / Test getting job list"""
        def test_job():
            return 'test'
        
        # Add multiple jobs
        self.scheduler.add_daily_job('daily1', test_job, hour=8)
        self.scheduler.add_weekly_job('weekly1', test_job, day_of_week='mon', hour=9)
        self.scheduler.add_interval_job('interval1', test_job, hours=1)
        
        jobs = self.scheduler.get_jobs()
        
        self.assertEqual(len(jobs), 3)
        
        # Check job IDs
        job_ids = [job['id'] for job in jobs]
        self.assertIn('daily1', job_ids)
        self.assertIn('weekly1', job_ids)
        self.assertIn('interval1', job_ids)
        
        # Check job types
        job_types = [job['type'] for job in jobs]
        self.assertIn('daily', job_types)
        self.assertIn('weekly', job_types)
        self.assertIn('interval', job_types)
    
    def test_start_stop_scheduler(self):
        """测试启动和停止调度器 / Test starting and stopping scheduler"""
        self.assertFalse(self.scheduler.is_running())
        
        # Start scheduler
        self.scheduler.start()
        time.sleep(0.1)  # Give it time to start
        self.assertTrue(self.scheduler.is_running())
        
        # Stop scheduler
        self.scheduler.shutdown(wait=False)
        time.sleep(0.1)  # Give it time to stop
        self.assertFalse(self.scheduler.is_running())
    
    def test_job_execution_on_error(self):
        """测试任务执行错误处理 / Test job execution error handling"""
        def failing_job():
            raise ValueError("Test error")
        
        # This should not raise an exception when the job runs
        # The error should be caught and logged
        success = self.scheduler.add_interval_job('failing_job', failing_job, seconds=1)
        self.assertTrue(success)
        
        # Start scheduler briefly
        self.scheduler.start()
        time.sleep(0.5)
        self.scheduler.shutdown(wait=False)
        
        # Scheduler should still be functional
        jobs = self.scheduler.get_jobs()
        self.assertGreaterEqual(len(jobs), 1)
    
    def test_duplicate_job_replacement(self):
        """测试重复任务替换 / Test duplicate job replacement"""
        def test_job1():
            return 'job1'
        
        def test_job2():
            return 'job2'
        
        # Add first job
        self.scheduler.add_daily_job('duplicate', test_job1, hour=8)
        jobs = self.scheduler.get_jobs()
        self.assertEqual(len(jobs), 1)
        
        # Add second job with same ID (should replace)
        self.scheduler.add_daily_job('duplicate', test_job2, hour=9)
        jobs = self.scheduler.get_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['schedule'], '09:00')
    
    def test_config_persistence(self):
        """测试配置持久化 / Test config persistence"""
        # Create scheduler and modify config
        scheduler1 = PeriodicScheduler(config_file=self.config_file)
        scheduler1.config['test_value'] = 'test123'
        scheduler1._save_config()
        
        # Create new scheduler with same config file
        scheduler2 = PeriodicScheduler(config_file=self.config_file)
        
        # Config should be loaded
        self.assertEqual(scheduler2.config['test_value'], 'test123')
        
        # Cleanup
        scheduler1.shutdown(wait=False)
        scheduler2.shutdown(wait=False)


if __name__ == '__main__':
    unittest.main()
