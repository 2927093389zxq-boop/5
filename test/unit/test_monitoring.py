"""
Tests for Monitoring Module
监控模块测试
"""

import pytest
import time
from core.monitoring import MetricsCollector, MonitoringDashboard, get_monitoring_dashboard


class TestMetricsCollector:
    """Test MetricsCollector class / 测试 MetricsCollector 类"""
    
    def test_collector_initialization(self):
        """Test collector initialization / 测试收集器初始化"""
        collector = MetricsCollector(max_history=100)
        
        assert collector.max_history == 100
        assert collector.total_requests == 0
        assert collector.successful_requests == 0
        assert collector.failed_requests == 0
        assert len(collector.request_history) == 0
    
    def test_record_successful_request(self):
        """Test recording successful request / 测试记录成功请求"""
        collector = MetricsCollector()
        
        collector.record_request(
            platform="amazon",
            success=True,
            response_time=1.5,
            items_count=50
        )
        
        assert collector.total_requests == 1
        assert collector.successful_requests == 1
        assert collector.failed_requests == 0
        assert collector.total_items_scraped == 50
    
    def test_record_failed_request(self):
        """Test recording failed request / 测试记录失败请求"""
        collector = MetricsCollector()
        
        collector.record_request(
            platform="amazon",
            success=False,
            response_time=2.0,
            error_type="timeout"
        )
        
        assert collector.total_requests == 1
        assert collector.successful_requests == 0
        assert collector.failed_requests == 1
        assert collector.total_errors == 1
    
    def test_record_captcha_error(self):
        """Test recording captcha error / 测试记录验证码错误"""
        collector = MetricsCollector()
        
        collector.record_request(
            platform="amazon",
            success=False,
            response_time=1.0,
            error_type="captcha"
        )
        
        assert collector.captcha_hits == 1
    
    def test_performance_metrics(self):
        """Test performance metrics / 测试性能指标"""
        collector = MetricsCollector()
        
        collector.record_request("amazon", True, 1.0, 10)
        collector.record_request("amazon", True, 2.0, 20)
        collector.record_request("amazon", True, 1.5, 15)
        
        assert collector.min_response_time == 1.0
        assert collector.max_response_time == 2.0
        assert collector.total_response_time == 4.5
    
    def test_platform_specific_metrics(self):
        """Test platform-specific metrics / 测试平台特定指标"""
        collector = MetricsCollector()
        
        collector.record_request("amazon", True, 1.0, 10)
        collector.record_request("shopee", True, 1.5, 20)
        collector.record_request("amazon", False, 2.0, error_type="timeout")
        
        assert "amazon" in collector.platform_metrics
        assert "shopee" in collector.platform_metrics
        
        amazon_stats = collector.platform_metrics["amazon"]
        assert amazon_stats["requests"] == 2
        assert amazon_stats["successful"] == 1
        assert amazon_stats["failed"] == 1
        assert amazon_stats["items"] == 10
    
    def test_get_current_stats(self):
        """Test getting current statistics / 测试获取当前统计"""
        collector = MetricsCollector()
        
        collector.record_request("amazon", True, 1.0, 10)
        collector.record_request("amazon", True, 2.0, 20)
        
        stats = collector.get_current_stats()
        
        assert stats["total_requests"] == 2
        assert stats["successful_requests"] == 2
        assert stats["success_rate"] == 100.0
        assert stats["total_items_scraped"] == 30
        assert stats["avg_response_time"] == 1.5
        assert "uptime_seconds" in stats
        assert "requests_per_minute" in stats
    
    def test_get_platform_stats(self):
        """Test getting platform statistics / 测试获取平台统计"""
        collector = MetricsCollector()
        
        collector.record_request("amazon", True, 1.0, 10)
        collector.record_request("shopee", True, 1.5, 20)
        
        platform_stats = collector.get_platform_stats()
        
        assert len(platform_stats) == 2
        assert "amazon" in platform_stats
        assert "shopee" in platform_stats
    
    def test_get_recent_requests(self):
        """Test getting recent requests / 测试获取最近请求"""
        collector = MetricsCollector()
        
        for i in range(5):
            collector.record_request("amazon", True, 1.0, 10)
        
        recent = collector.get_recent_requests(count=3)
        
        assert len(recent) == 3
    
    def test_get_recent_errors(self):
        """Test getting recent errors / 测试获取最近错误"""
        collector = MetricsCollector()
        
        collector.record_request("amazon", False, 1.0, error_type="timeout")
        collector.record_request("amazon", False, 1.0, error_type="captcha")
        
        recent_errors = collector.get_recent_errors(count=10)
        
        assert len(recent_errors) == 2
    
    def test_request_history_limit(self):
        """Test request history limit / 测试请求历史限制"""
        collector = MetricsCollector(max_history=10)
        
        # Add more than max_history
        for i in range(20):
            collector.record_request("amazon", True, 1.0, 10)
        
        # Should only keep last 10
        assert len(collector.request_history) == 10
    
    def test_reset(self):
        """Test resetting collector / 测试重置收集器"""
        collector = MetricsCollector()
        
        collector.record_request("amazon", True, 1.0, 10)
        collector.record_request("amazon", False, 2.0, error_type="timeout")
        
        assert collector.total_requests == 2
        
        collector.reset()
        
        assert collector.total_requests == 0
        assert collector.successful_requests == 0
        assert collector.failed_requests == 0
        assert len(collector.request_history) == 0
        assert len(collector.platform_metrics) == 0


class TestMonitoringDashboard:
    """Test MonitoringDashboard class / 测试 MonitoringDashboard 类"""
    
    def test_dashboard_initialization(self):
        """Test dashboard initialization / 测试仪表板初始化"""
        dashboard = MonitoringDashboard()
        
        assert dashboard.metrics_collector is not None
        assert len(dashboard.alerts) == 0
        assert "error_rate" in dashboard.alert_thresholds
    
    def test_record_scraping_operation(self):
        """Test recording scraping operation / 测试记录抓取操作"""
        dashboard = MonitoringDashboard()
        
        dashboard.record_scraping_operation(
            platform="amazon",
            success=True,
            response_time=1.0,
            items_count=10
        )
        
        stats = dashboard.metrics_collector.get_current_stats()
        assert stats["total_requests"] == 1
    
    def test_get_dashboard_data(self):
        """Test getting dashboard data / 测试获取仪表板数据"""
        dashboard = MonitoringDashboard()
        
        dashboard.record_scraping_operation("amazon", True, 1.0, 10)
        
        data = dashboard.get_dashboard_data()
        
        assert "current_stats" in data
        assert "platform_stats" in data
        assert "recent_requests" in data
        assert "recent_errors" in data
        assert "time_series" in data
        assert "alerts" in data
    
    def test_alert_high_error_rate(self):
        """Test alert for high error rate / 测试高错误率警报"""
        dashboard = MonitoringDashboard()
        
        # Set low threshold for testing
        dashboard.set_alert_threshold("error_rate", 0.3)
        
        # Record requests with high error rate (11 requests, need >10 for alert check)
        for i in range(11):
            if i < 6:
                dashboard.record_scraping_operation("amazon", True, 1.0, 10)
            else:
                dashboard.record_scraping_operation("amazon", False, 1.0, error_type="timeout")
        
        # Should have triggered alert
        assert len(dashboard.alerts) > 0
    
    def test_alert_high_captcha_rate(self):
        """Test alert for high captcha rate / 测试高验证码率警报"""
        dashboard = MonitoringDashboard()
        
        # Set low threshold for testing
        dashboard.set_alert_threshold("captcha_rate", 0.3)
        
        # Record requests with high captcha rate (11 requests, need >10 for alert check)
        for i in range(11):
            if i < 6:
                dashboard.record_scraping_operation("amazon", True, 1.0, 10)
            else:
                dashboard.record_scraping_operation("amazon", False, 1.0, error_type="captcha")
        
        # Should have triggered alert
        assert len(dashboard.alerts) > 0
    
    def test_alert_slow_response(self):
        """Test alert for slow response / 测试慢响应警报"""
        dashboard = MonitoringDashboard()
        
        # Set low threshold for testing
        dashboard.set_alert_threshold("avg_response_time", 5.0)
        
        # Record requests with slow response
        for i in range(15):
            dashboard.record_scraping_operation("amazon", True, 10.0, 10)
        
        # Should have triggered alert
        assert len(dashboard.alerts) > 0
    
    def test_set_alert_threshold(self):
        """Test setting alert threshold / 测试设置警报阈值"""
        dashboard = MonitoringDashboard()
        
        original = dashboard.alert_thresholds["error_rate"]
        new_threshold = 0.5
        
        dashboard.set_alert_threshold("error_rate", new_threshold)
        
        assert dashboard.alert_thresholds["error_rate"] == new_threshold
        assert dashboard.alert_thresholds["error_rate"] != original
    
    def test_reset(self):
        """Test resetting dashboard / 测试重置仪表板"""
        dashboard = MonitoringDashboard()
        
        dashboard.record_scraping_operation("amazon", True, 1.0, 10)
        dashboard.record_scraping_operation("amazon", False, 2.0, error_type="timeout")
        
        dashboard.reset()
        
        stats = dashboard.metrics_collector.get_current_stats()
        assert stats["total_requests"] == 0
        assert len(dashboard.alerts) == 0


class TestGlobalDashboard:
    """Test global dashboard instance / 测试全局仪表板实例"""
    
    def test_get_monitoring_dashboard(self):
        """Test getting global monitoring dashboard / 测试获取全局监控仪表板"""
        dashboard1 = get_monitoring_dashboard()
        dashboard2 = get_monitoring_dashboard()
        
        # Should return same instance
        assert dashboard1 is dashboard2
    
    def test_global_dashboard_persistence(self):
        """Test global dashboard persistence / 测试全局仪表板持久性"""
        dashboard = get_monitoring_dashboard()
        
        dashboard.record_scraping_operation("amazon", True, 1.0, 10)
        
        # Get dashboard again
        dashboard2 = get_monitoring_dashboard()
        
        stats = dashboard2.metrics_collector.get_current_stats()
        assert stats["total_requests"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
