"""
Tests for Task Queue Module
任务队列模块测试
"""

import pytest
import time
from core.task_queue import (
    Task, TaskStatus, TaskQueue,
    create_scrape_task, create_batch_scrape_tasks
)


class TestTask:
    """Test Task class / 测试 Task 类"""
    
    def test_task_initialization(self):
        """Test task initialization / 测试任务初始化"""
        task = Task("task_1", "scrape_url", {"url": "https://example.com"}, priority=5)
        
        assert task.task_id == "task_1"
        assert task.task_type == "scrape_url"
        assert task.params["url"] == "https://example.com"
        assert task.priority == 5
        assert task.status == TaskStatus.PENDING
        assert task.retries == 0
        assert task.max_retries == 3
    
    def test_task_to_dict(self):
        """Test task to dictionary conversion / 测试任务转字典"""
        task = Task("task_1", "scrape_url", {"url": "https://example.com"})
        task_dict = task.to_dict()
        
        assert task_dict["task_id"] == "task_1"
        assert task_dict["task_type"] == "scrape_url"
        assert task_dict["status"] == "pending"
        assert "created_at" in task_dict
    
    def test_task_from_dict(self):
        """Test task from dictionary creation / 测试从字典创建任务"""
        task_data = {
            "task_id": "task_1",
            "task_type": "scrape_url",
            "params": {"url": "https://example.com"},
            "priority": 5,
            "status": "pending",
            "created_at": "2025-01-01T00:00:00",
            "retries": 0
        }
        
        task = Task.from_dict(task_data)
        
        assert task.task_id == "task_1"
        assert task.task_type == "scrape_url"
        assert task.status == TaskStatus.PENDING


class TestTaskQueue:
    """Test TaskQueue class / 测试 TaskQueue 类"""
    
    def test_queue_initialization(self):
        """Test queue initialization / 测试队列初始化"""
        queue = TaskQueue(max_workers=4)
        
        assert queue.max_workers == 4
        assert len(queue.workers) == 0
        assert queue.running is False
        assert len(queue.tasks) == 0
    
    def test_register_handler(self):
        """Test handler registration / 测试处理器注册"""
        queue = TaskQueue()
        
        def test_handler(params):
            return "result"
        
        queue.register_handler("test_task", test_handler)
        
        assert "test_task" in queue.task_handlers
        assert queue.task_handlers["test_task"] == test_handler
    
    def test_add_task(self):
        """Test adding task / 测试添加任务"""
        queue = TaskQueue()
        task = Task("task_1", "scrape_url", {"url": "https://example.com"})
        
        result = queue.add_task(task)
        
        assert result is True
        assert "task_1" in queue.tasks
        assert queue.queue.qsize() == 1
    
    def test_add_duplicate_task(self):
        """Test adding duplicate task / 测试添加重复任务"""
        queue = TaskQueue()
        task1 = Task("task_1", "scrape_url", {"url": "https://example.com"})
        task2 = Task("task_1", "scrape_url", {"url": "https://example.com"})
        
        result1 = queue.add_task(task1)
        result2 = queue.add_task(task2)
        
        assert result1 is True
        assert result2 is False
        assert queue.queue.qsize() == 1
    
    def test_get_task_status(self):
        """Test getting task status / 测试获取任务状态"""
        queue = TaskQueue()
        task = Task("task_1", "scrape_url", {"url": "https://example.com"})
        queue.add_task(task)
        
        status = queue.get_task_status("task_1")
        
        assert status is not None
        assert status["task_id"] == "task_1"
        assert status["status"] == "pending"
    
    def test_get_task_status_not_found(self):
        """Test getting status of non-existent task / 测试获取不存在任务的状态"""
        queue = TaskQueue()
        status = queue.get_task_status("nonexistent")
        
        assert status is None
    
    def test_get_all_tasks(self):
        """Test getting all tasks / 测试获取所有任务"""
        queue = TaskQueue()
        
        task1 = Task("task_1", "scrape_url", {"url": "https://example.com"})
        task2 = Task("task_2", "scrape_url", {"url": "https://example2.com"})
        
        queue.add_task(task1)
        queue.add_task(task2)
        
        all_tasks = queue.get_all_tasks()
        
        assert len(all_tasks) == 2
    
    def test_get_stats(self):
        """Test getting queue statistics / 测试获取队列统计"""
        queue = TaskQueue(max_workers=4)
        
        task1 = Task("task_1", "scrape_url", {"url": "https://example.com"})
        task2 = Task("task_2", "scrape_url", {"url": "https://example2.com"})
        
        queue.add_task(task1)
        queue.add_task(task2)
        
        # Manually set one task to completed
        queue.tasks["task_1"].status = TaskStatus.COMPLETED
        
        stats = queue.get_stats()
        
        assert stats["total"] == 2
        assert stats["pending"] == 1
        assert stats["completed"] == 1
        assert stats["max_workers"] == 4
    
    def test_cancel_task(self):
        """Test canceling a task / 测试取消任务"""
        queue = TaskQueue()
        task = Task("task_1", "scrape_url", {"url": "https://example.com"})
        queue.add_task(task)
        
        result = queue.cancel_task("task_1")
        
        assert result is True
        assert queue.tasks["task_1"].status == TaskStatus.CANCELLED
    
    def test_cancel_running_task(self):
        """Test canceling a running task / 测试取消运行中的任务"""
        queue = TaskQueue()
        task = Task("task_1", "scrape_url", {"url": "https://example.com"})
        queue.add_task(task)
        
        # Set task to running
        queue.tasks["task_1"].status = TaskStatus.RUNNING
        
        result = queue.cancel_task("task_1")
        
        assert result is False
    
    def test_start_stop_queue(self):
        """Test starting and stopping queue / 测试启动和停止队列"""
        queue = TaskQueue(max_workers=2)
        
        queue.start()
        assert queue.running is True
        assert len(queue.workers) == 2
        
        queue.stop(wait=False)
        assert queue.running is False
    
    def test_worker_execution(self):
        """Test worker task execution / 测试工作线程任务执行"""
        queue = TaskQueue(max_workers=1)
        
        # Register handler
        results = []
        
        def test_handler(params):
            results.append(params["url"])
            return {"success": True}
        
        queue.register_handler("scrape_url", test_handler)
        
        # Add task
        task = Task("task_1", "scrape_url", {"url": "https://example.com"})
        queue.add_task(task)
        
        # Start queue
        queue.start()
        
        # Wait for execution
        time.sleep(1)
        
        # Stop queue
        queue.stop(wait=True)
        
        # Check results
        assert len(results) == 1
        assert results[0] == "https://example.com"
        assert queue.tasks["task_1"].status == TaskStatus.COMPLETED


class TestConvenienceFunctions:
    """Test convenience functions / 测试便捷函数"""
    
    def test_create_scrape_task(self):
        """Test creating scrape task / 测试创建抓取任务"""
        task = create_scrape_task(
            url="https://example.com",
            platform="amazon",
            max_items=50,
            priority=5
        )
        
        assert task.task_type == "scrape_url"
        assert task.params["url"] == "https://example.com"
        assert task.params["platform"] == "amazon"
        assert task.params["max_items"] == 50
        assert task.priority == 5
    
    def test_create_batch_scrape_tasks(self):
        """Test creating batch scrape tasks / 测试创建批量抓取任务"""
        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ]
        
        tasks = create_batch_scrape_tasks(urls, platform="amazon", max_items=50)
        
        assert len(tasks) == 3
        assert all(t.task_type == "scrape_url" for t in tasks)
        assert all(t.params["platform"] == "amazon" for t in tasks)
        assert tasks[0].params["url"] == "https://example1.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
