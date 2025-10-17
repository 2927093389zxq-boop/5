"""
Task Queue System for Distributed Scraping
任务队列系统，用于分布式抓取

Supports distributed task execution with worker pools
支持使用工作池进行分布式任务执行
"""

import json
import hashlib
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from queue import Queue, Empty
from threading import Thread, Lock
from scrapers.logger import log_info, log_error, log_warning


class TaskStatus(Enum):
    """Task status enumeration / 任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """Task class / 任务类"""
    
    def __init__(self, task_id: str, task_type: str, params: Dict[str, Any], priority: int = 0):
        """
        Initialize task
        初始化任务
        
        Args:
            task_id: Unique task ID / 唯一任务 ID
            task_type: Task type (scrape_url, scrape_list, etc.) / 任务类型
            params: Task parameters / 任务参数
            priority: Task priority (higher = more priority) / 任务优先级（越高优先级越大）
        """
        self.task_id = task_id
        self.task_type = task_type
        self.params = params
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.retries = 0
        self.max_retries = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary / 转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "params": self.params,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "retries": self.retries
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary / 从字典创建任务"""
        task = Task(
            task_id=data["task_id"],
            task_type=data["task_type"],
            params=data["params"],
            priority=data.get("priority", 0)
        )
        task.status = TaskStatus(data["status"])
        task.created_at = data["created_at"]
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")
        task.result = data.get("result")
        task.error = data.get("error")
        task.retries = data.get("retries", 0)
        return task


class TaskQueue:
    """Task queue with priority support / 支持优先级的任务队列"""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize task queue
        初始化任务队列
        
        Args:
            max_workers: Maximum number of worker threads / 最大工作线程数
        """
        self.queue = Queue()
        self.tasks: Dict[str, Task] = {}
        self.lock = Lock()
        self.workers: List[Thread] = []
        self.max_workers = max_workers
        self.running = False
        self.task_handlers: Dict[str, Callable] = {}
        
    def register_handler(self, task_type: str, handler: Callable):
        """
        Register task handler
        注册任务处理器
        
        Args:
            task_type: Task type / 任务类型
            handler: Handler function / 处理函数
        """
        self.task_handlers[task_type] = handler
        log_info(f"已注册任务处理器: {task_type}")
    
    def add_task(self, task: Task) -> bool:
        """
        Add task to queue
        添加任务到队列
        
        Args:
            task: Task to add / 要添加的任务
            
        Returns:
            Success status / 成功状态
        """
        try:
            with self.lock:
                if task.task_id in self.tasks:
                    log_warning(f"任务已存在: {task.task_id}")
                    return False
                
                self.tasks[task.task_id] = task
                # Priority queue: add with negative priority for max-heap behavior
                self.queue.put((-task.priority, task.task_id))
                log_info(f"任务已添加到队列: {task.task_id} (优先级: {task.priority})")
                return True
                
        except Exception as e:
            log_error(f"添加任务失败: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status
        获取任务状态
        
        Args:
            task_id: Task ID / 任务 ID
            
        Returns:
            Task status dictionary / 任务状态字典
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                return task.to_dict()
            return None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all tasks
        获取所有任务
        
        Returns:
            List of task dictionaries / 任务字典列表
        """
        with self.lock:
            return [task.to_dict() for task in self.tasks.values()]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics
        获取队列统计信息
        
        Returns:
            Statistics dictionary / 统计信息字典
        """
        with self.lock:
            stats = {
                "total": len(self.tasks),
                "pending": sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
                "running": sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING),
                "completed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
                "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
                "cancelled": sum(1 for t in self.tasks.values() if t.status == TaskStatus.CANCELLED),
                "queue_size": self.queue.qsize(),
                "workers": len(self.workers),
                "max_workers": self.max_workers
            }
            return stats
    
    def _worker(self):
        """Worker thread function / 工作线程函数"""
        log_info("工作线程启动")
        
        while self.running:
            try:
                # Get task with timeout
                try:
                    _, task_id = self.queue.get(timeout=1)
                except Empty:
                    continue
                
                with self.lock:
                    task = self.tasks.get(task_id)
                    if not task or task.status != TaskStatus.PENDING:
                        continue
                    
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.now(timezone.utc).isoformat()
                
                log_info(f"开始执行任务: {task_id} ({task.task_type})")
                
                # Execute task
                try:
                    handler = self.task_handlers.get(task.task_type)
                    if not handler:
                        raise ValueError(f"未找到任务处理器: {task.task_type}")
                    
                    result = handler(task.params)
                    
                    with self.lock:
                        task.status = TaskStatus.COMPLETED
                        task.completed_at = datetime.now(timezone.utc).isoformat()
                        task.result = result
                    
                    log_info(f"任务完成: {task_id}")
                    
                except Exception as e:
                    log_error(f"任务执行失败: {task_id} - {e}")
                    
                    with self.lock:
                        task.retries += 1
                        
                        if task.retries < task.max_retries:
                            # Retry task
                            task.status = TaskStatus.PENDING
                            self.queue.put((-task.priority, task_id))
                            log_info(f"任务重试 ({task.retries}/{task.max_retries}): {task_id}")
                        else:
                            # Mark as failed
                            task.status = TaskStatus.FAILED
                            task.completed_at = datetime.now(timezone.utc).isoformat()
                            task.error = str(e)
                            log_error(f"任务失败（超过最大重试次数）: {task_id}")
                
                finally:
                    self.queue.task_done()
                    
            except Exception as e:
                log_error(f"工作线程错误: {e}")
        
        log_info("工作线程停止")
    
    def start(self):
        """Start workers / 启动工作线程"""
        if self.running:
            log_warning("任务队列已在运行")
            return
        
        self.running = True
        
        for i in range(self.max_workers):
            worker = Thread(target=self._worker, name=f"Worker-{i+1}", daemon=True)
            worker.start()
            self.workers.append(worker)
        
        log_info(f"任务队列已启动，工作线程数: {self.max_workers}")
    
    def stop(self, wait: bool = True):
        """
        Stop workers
        停止工作线程
        
        Args:
            wait: Wait for workers to finish / 等待工作线程完成
        """
        if not self.running:
            log_warning("任务队列未运行")
            return
        
        log_info("正在停止任务队列...")
        self.running = False
        
        if wait:
            for worker in self.workers:
                worker.join(timeout=5)
        
        self.workers.clear()
        log_info("任务队列已停止")
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending task
        取消待处理任务
        
        Args:
            task_id: Task ID / 任务 ID
            
        Returns:
            Success status / 成功状态
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                log_warning(f"任务不存在: {task_id}")
                return False
            
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now(timezone.utc).isoformat()
                log_info(f"任务已取消: {task_id}")
                return True
            else:
                log_warning(f"任务不能取消，当前状态: {task.status.value}")
                return False


# Convenience functions / 便捷函数

def create_scrape_task(url: str, platform: str = "amazon", max_items: int = 50, priority: int = 0) -> Task:
    """
    Create a scraping task
    创建抓取任务
    
    Args:
        url: Target URL / 目标 URL
        platform: Platform name / 平台名称
        max_items: Maximum items to scrape / 最大抓取项数
        priority: Task priority / 任务优先级
        
    Returns:
        Task object / 任务对象
    """
    task_id = hashlib.md5(f"{url}_{time.time()}".encode()).hexdigest()
    
    params = {
        "url": url,
        "platform": platform,
        "max_items": max_items
    }
    
    return Task(task_id, "scrape_url", params, priority)


def create_batch_scrape_tasks(urls: List[str], platform: str = "amazon", max_items: int = 50) -> List[Task]:
    """
    Create batch scraping tasks
    创建批量抓取任务
    
    Args:
        urls: List of URLs / URL 列表
        platform: Platform name / 平台名称
        max_items: Maximum items to scrape / 最大抓取项数
        
    Returns:
        List of tasks / 任务列表
    """
    return [create_scrape_task(url, platform, max_items, priority=i) for i, url in enumerate(urls)]
