"""
Real-time Monitoring Dashboard Module
实时监控仪表板模块

Provides real-time monitoring of scraping operations
提供抓取操作的实时监控
"""

import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Set
from collections import deque
from threading import Lock
from scrapers.logger import log_info, log_error, log_warning


class MetricsCollector:
    """Metrics collector for monitoring / 用于监控的指标收集器"""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize metrics collector
        初始化指标收集器
        
        Args:
            max_history: Maximum number of historical records / 最大历史记录数
        """
        self.max_history = max_history
        self.lock = Lock()
        
        # Current metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_items_scraped = 0
        self.total_errors = 0
        self.captcha_hits = 0
        
        # Performance metrics
        self.total_response_time = 0.0
        self.min_response_time = float('inf')
        self.max_response_time = 0.0
        
        # Historical data (time-series)
        self.request_history = deque(maxlen=max_history)
        self.error_history = deque(maxlen=max_history)
        self.performance_history = deque(maxlen=max_history)
        
        # Platform-specific metrics
        self.platform_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Start time
        self.start_time = datetime.now(timezone.utc)
    
    def record_request(self, platform: str, success: bool, response_time: float, 
                      items_count: int = 0, error_type: str = None):
        """
        Record a scraping request
        记录一次抓取请求
        
        Args:
            platform: Platform name / 平台名称
            success: Whether request was successful / 请求是否成功
            response_time: Response time in seconds / 响应时间（秒）
            items_count: Number of items scraped / 抓取的项目数
            error_type: Type of error if failed / 失败时的错误类型
        """
        with self.lock:
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Update global metrics
            self.total_requests += 1
            
            if success:
                self.successful_requests += 1
                self.total_items_scraped += items_count
            else:
                self.failed_requests += 1
                self.total_errors += 1
                
                if error_type == "captcha":
                    self.captcha_hits += 1
            
            # Update performance metrics
            self.total_response_time += response_time
            self.min_response_time = min(self.min_response_time, response_time)
            self.max_response_time = max(self.max_response_time, response_time)
            
            # Update platform-specific metrics
            if platform not in self.platform_metrics:
                self.platform_metrics[platform] = {
                    "requests": 0,
                    "successful": 0,
                    "failed": 0,
                    "items": 0
                }
            
            platform_stats = self.platform_metrics[platform]
            platform_stats["requests"] += 1
            
            if success:
                platform_stats["successful"] += 1
                platform_stats["items"] += items_count
            else:
                platform_stats["failed"] += 1
            
            # Add to history
            self.request_history.append({
                "timestamp": timestamp,
                "platform": platform,
                "success": success,
                "response_time": response_time,
                "items_count": items_count
            })
            
            if not success:
                self.error_history.append({
                    "timestamp": timestamp,
                    "platform": platform,
                    "error_type": error_type
                })
            
            self.performance_history.append({
                "timestamp": timestamp,
                "response_time": response_time
            })
    
    def get_current_stats(self) -> Dict[str, Any]:
        """
        Get current statistics
        获取当前统计信息
        
        Returns:
            Current statistics / 当前统计信息
        """
        with self.lock:
            uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            avg_response_time = (self.total_response_time / self.total_requests 
                               if self.total_requests > 0 else 0)
            success_rate = (self.successful_requests / self.total_requests * 100 
                          if self.total_requests > 0 else 0)
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": uptime,
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": success_rate,
                "total_items_scraped": self.total_items_scraped,
                "total_errors": self.total_errors,
                "captcha_hits": self.captcha_hits,
                "avg_response_time": avg_response_time,
                "min_response_time": self.min_response_time if self.min_response_time != float('inf') else 0,
                "max_response_time": self.max_response_time,
                "requests_per_minute": (self.total_requests / uptime * 60) if uptime > 0 else 0
            }
    
    def get_platform_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get platform-specific statistics
        获取平台特定统计信息
        
        Returns:
            Platform statistics / 平台统计信息
        """
        with self.lock:
            return self.platform_metrics.copy()
    
    def get_recent_requests(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent request history
        获取最近的请求历史
        
        Args:
            count: Number of records to return / 返回的记录数
            
        Returns:
            Recent request records / 最近的请求记录
        """
        with self.lock:
            return list(self.request_history)[-count:]
    
    def get_recent_errors(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent error history
        获取最近的错误历史
        
        Args:
            count: Number of records to return / 返回的记录数
            
        Returns:
            Recent error records / 最近的错误记录
        """
        with self.lock:
            return list(self.error_history)[-count:]
    
    def get_time_series_data(self, minutes: int = 60) -> Dict[str, List[Any]]:
        """
        Get time-series data for charting
        获取用于图表的时间序列数据
        
        Args:
            minutes: Number of minutes to include / 包含的分钟数
            
        Returns:
            Time-series data / 时间序列数据
        """
        with self.lock:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            
            # Filter recent data
            recent_requests = [
                r for r in self.request_history 
                if datetime.fromisoformat(r["timestamp"]) > cutoff_time
            ]
            
            recent_performance = [
                p for p in self.performance_history
                if datetime.fromisoformat(p["timestamp"]) > cutoff_time
            ]
            
            return {
                "requests": recent_requests,
                "performance": recent_performance
            }
    
    def reset(self):
        """Reset all metrics / 重置所有指标"""
        with self.lock:
            self.total_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.total_items_scraped = 0
            self.total_errors = 0
            self.captcha_hits = 0
            
            self.total_response_time = 0.0
            self.min_response_time = float('inf')
            self.max_response_time = 0.0
            
            self.request_history.clear()
            self.error_history.clear()
            self.performance_history.clear()
            
            self.platform_metrics.clear()
            
            self.start_time = datetime.now(timezone.utc)
            
            log_info("指标收集器已重置")


class MonitoringDashboard:
    """Monitoring dashboard manager / 监控仪表板管理器"""
    
    def __init__(self):
        """Initialize dashboard / 初始化仪表板"""
        self.metrics_collector = MetricsCollector()
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% error rate
            "captcha_rate": 0.05,  # 5% captcha rate
            "avg_response_time": 10.0,  # 10 seconds
        }
        self.recent_alert_types: Set[str] = set()  # Track recent alerts to avoid duplicates
    
    def record_scraping_operation(self, platform: str, success: bool, response_time: float,
                                  items_count: int = 0, error_type: str = None):
        """
        Record a scraping operation
        记录一次抓取操作
        
        Args:
            platform: Platform name / 平台名称
            success: Whether operation was successful / 操作是否成功
            response_time: Response time in seconds / 响应时间（秒）
            items_count: Number of items scraped / 抓取的项目数
            error_type: Type of error if failed / 失败时的错误类型
        """
        self.metrics_collector.record_request(platform, success, response_time, items_count, error_type)
        self._check_alerts()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get complete dashboard data
        获取完整的仪表板数据
        
        Returns:
            Dashboard data / 仪表板数据
        """
        return {
            "current_stats": self.metrics_collector.get_current_stats(),
            "platform_stats": self.metrics_collector.get_platform_stats(),
            "recent_requests": self.metrics_collector.get_recent_requests(50),
            "recent_errors": self.metrics_collector.get_recent_errors(20),
            "time_series": self.metrics_collector.get_time_series_data(60),
            "alerts": self.alerts[-10:]  # Last 10 alerts
        }
    
    def _check_alerts(self):
        """Check for alert conditions / 检查警报条件"""
        stats = self.metrics_collector.get_current_stats()
        
        # Check error rate
        if stats["total_requests"] > 10:  # Only check if we have enough data
            error_rate = stats["failed_requests"] / stats["total_requests"]
            if error_rate > self.alert_thresholds["error_rate"]:
                # Only add alert if not recently added
                if "high_error_rate" not in self.recent_alert_types:
                    self._add_alert(
                        "high_error_rate",
                        f"错误率过高: {error_rate:.1%}",
                        "warning"
                    )
                    self.recent_alert_types.add("high_error_rate")
            else:
                # Clear the recent alert if rate is back to normal
                self.recent_alert_types.discard("high_error_rate")
            
            # Check captcha rate
            captcha_rate = stats["captcha_hits"] / stats["total_requests"]
            if captcha_rate > self.alert_thresholds["captcha_rate"]:
                if "high_captcha_rate" not in self.recent_alert_types:
                    self._add_alert(
                        "high_captcha_rate",
                        f"验证码触发率过高: {captcha_rate:.1%}",
                        "warning"
                    )
                    self.recent_alert_types.add("high_captcha_rate")
            else:
                self.recent_alert_types.discard("high_captcha_rate")
            
            # Check average response time
            if stats["avg_response_time"] > self.alert_thresholds["avg_response_time"]:
                if "slow_response" not in self.recent_alert_types:
                    self._add_alert(
                        "slow_response",
                        f"平均响应时间过长: {stats['avg_response_time']:.2f}秒",
                        "info"
                    )
                    self.recent_alert_types.add("slow_response")
            else:
                self.recent_alert_types.discard("slow_response")
    
    def _add_alert(self, alert_type: str, message: str, severity: str):
        """
        Add alert
        添加警报
        
        Args:
            alert_type: Alert type / 警报类型
            message: Alert message / 警报信息
            severity: Alert severity (info, warning, error) / 警报严重程度
        """
        alert = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": alert_type,
            "message": message,
            "severity": severity
        }
        
        self.alerts.append(alert)
        
        # Log alert
        if severity == "error":
            log_error(f"[ALERT] {message}")
        elif severity == "warning":
            log_warning(f"[ALERT] {message}")
        else:
            log_info(f"[ALERT] {message}")
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """
        Set alert threshold
        设置警报阈值
        
        Args:
            metric: Metric name / 指标名称
            threshold: Threshold value / 阈值
        """
        if metric in self.alert_thresholds:
            self.alert_thresholds[metric] = threshold
            log_info(f"警报阈值已更新: {metric} = {threshold}")
    
    def reset(self):
        """Reset dashboard / 重置仪表板"""
        self.metrics_collector.reset()
        self.alerts.clear()
        self.recent_alert_types.clear()
        log_info("监控仪表板已重置")


# Global monitoring dashboard instance / 全局监控仪表板实例
_global_dashboard: Optional[MonitoringDashboard] = None


def get_monitoring_dashboard() -> MonitoringDashboard:
    """
    Get global monitoring dashboard instance
    获取全局监控仪表板实例
    
    Returns:
        Monitoring dashboard / 监控仪表板
    """
    global _global_dashboard
    if _global_dashboard is None:
        _global_dashboard = MonitoringDashboard()
    return _global_dashboard
