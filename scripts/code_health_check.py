#!/usr/bin/env python3
"""
代码健康检查脚本
Code Health Check Script

检查所有代码是否能正常运行
Check if all code can run properly
"""

import sys
import os
import importlib
import traceback
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class HealthChecker:
    """代码健康检查器 / Code Health Checker"""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def check_module_imports(self):
        """检查模块导入 / Check module imports"""
        print("=" * 60)
        print("检查核心模块导入 / Checking Core Module Imports")
        print("=" * 60)
        
        core_modules = [
            'logging_setup',
            # 'scheduler',  # Skipping - starts automatically on import
            'scheduler_batch',
            'scrapers.amazon_scraper',
            'scrapers.multi_platform_scraper',
            'scrapers.base_scraper',
            'core.data_fetcher',
            'core.monitoring',
            'core.task_queue',
            'core.browser_automation',
            'core.data_validation',
            'core.plugin_system',
            'core.anomaly_detector',
            'core.i18n',
            'core.rl_auto_tuner',
            'core.collectors.youtube_collector',
            'core.collectors.market_collector',
            'core.collectors.policy_collector',
            'core.collectors.spider_engine',
            'core.auto_crawler_iter.iteration_engine',
            'core.auto_crawler_iter.evaluator',
            'core.auto_crawler_iter.variant_builder',
            'core.auto_crawler_iter.strategy_registry',
            'core.auto_crawler_iter.ml_strategy_ranker',
            'core.processing.anomaly_detector',
            'core.processing.recommender',
            'core.ai.evolution_engine',
            'core.ai.auto_patch',
            'core.ai.memory_manager',
            # 'core.ai.scheduler',  # Skipping - starts automatically on import
            'publishers.mail_sender',
        ]
        
        for module_name in core_modules:
            try:
                importlib.import_module(module_name)
                self.results['passed'].append(f"✓ 模块导入: {module_name}")
                print(f"✓ {module_name}")
            except Exception as e:
                self.results['failed'].append(f"✗ 模块导入失败: {module_name} - {str(e)}")
                print(f"✗ {module_name}: {str(e)[:80]}")
    
    def check_ui_modules(self):
        """检查UI模块 / Check UI modules"""
        print("\n" + "=" * 60)
        print("检查UI模块导入 / Checking UI Module Imports")
        print("=" * 60)
        
        ui_modules = [
            'ui.dashboard',
            'ui.analytics',
            'ui.prototype_view',
            'ui.api_admin',
            'ui.auto_evolution',
            'ui.auto_patch_view',
            'ui.ai_learning_center',
            'ui.source_attribution',
            'ui.authoritative_data_center',
            'ui.monitoring_view',
        ]
        
        for module_name in ui_modules:
            try:
                importlib.import_module(module_name)
                self.results['passed'].append(f"✓ UI模块导入: {module_name}")
                print(f"✓ {module_name}")
            except Exception as e:
                self.results['failed'].append(f"✗ UI模块导入失败: {module_name} - {str(e)}")
                print(f"✗ {module_name}: {str(e)[:80]}")
    
    def check_directories(self):
        """检查必需目录 / Check required directories"""
        print("\n" + "=" * 60)
        print("检查必需目录 / Checking Required Directories")
        print("=" * 60)
        
        required_dirs = [
            'config',
            'logs',
            'data',
            'checkpoint',
            'data/amazon',
            'data/telemetry',
            'plugins',
            'plugins/strategies',
            'plugins/evaluators',
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            if full_path.exists():
                self.results['passed'].append(f"✓ 目录存在: {dir_path}")
                print(f"✓ {dir_path}")
            else:
                self.results['warnings'].append(f"⚠ 目录不存在: {dir_path}")
                print(f"⚠ {dir_path} (可能需要创建)")
    
    def check_config_files(self):
        """检查配置文件 / Check configuration files"""
        print("\n" + "=" * 60)
        print("检查配置文件 / Checking Configuration Files")
        print("=" * 60)
        
        config_files = [
            'config.json',
            'requirements.txt',
            'README.md',
        ]
        
        for file_path in config_files:
            full_path = project_root / file_path
            if full_path.exists():
                self.results['passed'].append(f"✓ 配置文件存在: {file_path}")
                print(f"✓ {file_path}")
            else:
                self.results['failed'].append(f"✗ 配置文件缺失: {file_path}")
                print(f"✗ {file_path}")
    
    def check_launchers(self):
        """检查启动器 / Check launchers"""
        print("\n" + "=" * 60)
        print("检查启动器 / Checking Launchers")
        print("=" * 60)
        
        try:
            import run_launcher
            self.results['passed'].append("✓ run_launcher.py 可以导入")
            print("✓ run_launcher.py 可以导入")
            
            # 检查关键函数和变量
            if hasattr(run_launcher, 'MENU_STRUCTURE'):
                self.results['passed'].append("✓ MENU_STRUCTURE 已定义")
                print("✓ MENU_STRUCTURE 已定义")
            
            if hasattr(run_launcher, 'ensure_basic_config'):
                self.results['passed'].append("✓ ensure_basic_config 函数存在")
                print("✓ ensure_basic_config 函数存在")
                
        except Exception as e:
            self.results['failed'].append(f"✗ run_launcher.py 导入失败: {str(e)}")
            print(f"✗ run_launcher.py: {str(e)}")
    
    def check_examples(self):
        """检查示例脚本 / Check example scripts"""
        print("\n" + "=" * 60)
        print("检查示例脚本 / Checking Example Scripts")
        print("=" * 60)
        
        sys.path.insert(0, str(project_root / 'examples'))
        
        examples = [
            'amazon_scraper_examples',
            'enhanced_pipeline_demo',
            'multi_platform_scraper_examples',
        ]
        
        for example in examples:
            try:
                importlib.import_module(example)
                self.results['passed'].append(f"✓ 示例脚本可导入: {example}.py")
                print(f"✓ {example}.py")
            except Exception as e:
                self.results['failed'].append(f"✗ 示例脚本导入失败: {example}.py - {str(e)}")
                print(f"✗ {example}.py: {str(e)[:80]}")
    
    def print_summary(self):
        """打印总结 / Print summary"""
        print("\n" + "=" * 60)
        print("检查总结 / Check Summary")
        print("=" * 60)
        
        print(f"\n✓ 通过: {len(self.results['passed'])} 项")
        print(f"✗ 失败: {len(self.results['failed'])} 项")
        print(f"⚠ 警告: {len(self.results['warnings'])} 项")
        
        if self.results['failed']:
            print("\n失败项详情:")
            for failure in self.results['failed']:
                print(f"  {failure}")
        
        if self.results['warnings']:
            print("\n警告项详情:")
            for warning in self.results['warnings']:
                print(f"  {warning}")
        
        print("\n" + "=" * 60)
        if len(self.results['failed']) == 0:
            print("✅ 所有代码检查通过，系统可以正常运行!")
            print("✅ All code checks passed, system can run properly!")
            return 0
        else:
            print("⚠️  存在一些问题，请检查上述失败项")
            print("⚠️  Some issues found, please check failed items above")
            return 1


def main():
    """主函数 / Main function"""
    print("\n" + "=" * 60)
    print("代码健康检查开始 / Code Health Check Started")
    print("=" * 60 + "\n")
    
    checker = HealthChecker()
    
    # 运行所有检查
    checker.check_directories()
    checker.check_config_files()
    checker.check_module_imports()
    checker.check_ui_modules()
    checker.check_launchers()
    checker.check_examples()
    
    # 打印总结
    exit_code = checker.print_summary()
    
    print("\n" + "=" * 60)
    print("代码健康检查完成 / Code Health Check Completed")
    print("=" * 60 + "\n")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
