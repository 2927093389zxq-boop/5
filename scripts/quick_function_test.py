#!/usr/bin/env python3
"""
快速功能测试脚本
Quick Functionality Test Script

测试核心功能是否能正常工作
Test if core functionalities work properly
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_amazon_scraper():
    """测试 Amazon 爬虫基础功能"""
    print("\n测试 Amazon 爬虫...")
    try:
        from scrapers.amazon_scraper import AmazonScraper, SELECTORS
        
        # 创建实例
        scraper = AmazonScraper()
        assert scraper.data_dir == "data/amazon"
        assert os.path.exists(scraper.data_dir)
        
        # 验证选择器配置
        assert 'list' in SELECTORS
        assert 'title' in SELECTORS
        assert 'price' in SELECTORS
        
        print("✓ Amazon 爬虫基础功能正常")
        return True
    except Exception as e:
        print(f"✗ Amazon 爬虫测试失败: {e}")
        return False

def test_data_validation():
    """测试数据验证功能"""
    print("\n测试数据验证...")
    try:
        from core.data_validation import DataValidator, ValidationRule
        
        # 创建验证器
        validator = DataValidator()
        
        # 添加规则
        validator.add_rule(ValidationRule(
            field='title',
            required=True,
            field_type=str
        ))
        
        # 测试验证
        valid_data = {'title': 'Test Product'}
        is_valid, errors = validator.validate(valid_data)
        assert is_valid == True
        
        invalid_data = {}
        is_valid, errors = validator.validate(invalid_data)
        assert is_valid == False
        
        print("✓ 数据验证功能正常")
        return True
    except Exception as e:
        print(f"✗ 数据验证测试失败: {e}")
        return False

def test_task_queue():
    """测试任务队列功能"""
    print("\n测试任务队列...")
    try:
        from core.task_queue import TaskQueue, Task
        
        # 创建任务队列
        queue = TaskQueue()
        
        # 创建任务
        task = Task(
            task_id='test_task_1',
            task_type='scrape',
            payload={'url': 'https://example.com'}
        )
        
        # 获取统计
        stats = queue.get_stats()
        assert 'total' in stats
        assert 'pending' in stats
        
        print("✓ 任务队列功能正常")
        return True
    except Exception as e:
        print(f"✗ 任务队列测试失败: {e}")
        return False

def test_monitoring():
    """测试监控功能"""
    print("\n测试监控系统...")
    try:
        from core.monitoring import MonitoringSystem
        
        # 创建监控系统
        monitor = MonitoringSystem()
        
        # 记录指标
        monitor.record_metric('test_metric', 100)
        
        # 获取统计
        stats = monitor.get_stats()
        assert isinstance(stats, dict)
        
        print("✓ 监控系统功能正常")
        return True
    except Exception as e:
        print(f"✗ 监控系统测试失败: {e}")
        return False

def test_i18n():
    """测试国际化功能"""
    print("\n测试国际化...")
    try:
        from core.i18n import get_text, set_language
        
        # 设置语言为中文
        set_language('zh_CN')
        text = get_text('system.name')
        assert text is not None
        
        # 设置语言为英文
        set_language('en_US')
        text = get_text('system.name')
        assert text is not None
        
        print("✓ 国际化功能正常")
        return True
    except Exception as e:
        print(f"✗ 国际化测试失败: {e}")
        return False

def test_plugin_system():
    """测试插件系统"""
    print("\n测试插件系统...")
    try:
        from core.plugin_system import PluginManager
        
        # 创建插件管理器
        manager = PluginManager()
        
        # 加载插件
        manager.load_plugins()
        
        # 获取策略和评估器
        strategies = manager.get_strategies()
        evaluators = manager.get_evaluators()
        
        assert isinstance(strategies, list)
        assert isinstance(evaluators, list)
        
        print("✓ 插件系统功能正常")
        return True
    except Exception as e:
        print(f"✗ 插件系统测试失败: {e}")
        return False

def test_iteration_engine():
    """测试自迭代引擎"""
    print("\n测试自迭代引擎...")
    try:
        from core.auto_crawler_iter.iteration_engine import IterationEngine
        from core.auto_crawler_iter.strategy_registry import StrategyRegistry
        
        # 创建引擎
        engine = IterationEngine()
        
        # 检查策略注册表
        registry = StrategyRegistry()
        available_strategies = registry.list_strategies()
        assert isinstance(available_strategies, list)
        
        print("✓ 自迭代引擎功能正常")
        return True
    except Exception as e:
        print(f"✗ 自迭代引擎测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("快速功能测试开始 / Quick Functionality Test Started")
    print("=" * 60)
    
    tests = [
        ("Amazon 爬虫", test_amazon_scraper),
        ("数据验证", test_data_validation),
        ("任务队列", test_task_queue),
        ("监控系统", test_monitoring),
        ("国际化", test_i18n),
        ("插件系统", test_plugin_system),
        ("自迭代引擎", test_iteration_engine),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ {name} 测试出错: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("测试总结 / Test Summary")
    print("=" * 60)
    print(f"✓ 通过: {passed}/{len(tests)}")
    print(f"✗ 失败: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ 所有核心功能测试通过!")
        print("✅ All core functionality tests passed!")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")
        print("⚠️  Some tests failed, please check error messages above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
