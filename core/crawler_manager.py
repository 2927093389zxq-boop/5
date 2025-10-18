"""
爬虫管理模块 - 集中管理所有爬虫代码
Crawler Manager Module - Centralized management of all crawler code
"""

import os
import json
import importlib
import importlib.util
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class CrawlerManager:
    """爬虫管理器 - 动态加载和管理爬虫代码"""
    
    def __init__(self, storage_dir: str = "data/custom_crawlers"):
        """
        初始化爬虫管理器
        
        Args:
            storage_dir: 自定义爬虫存储目录
        """
        self.storage_dir = storage_dir
        self.config_file = os.path.join(storage_dir, "crawlers_config.json")
        os.makedirs(storage_dir, exist_ok=True)
        
        # 加载配置
        self.crawlers = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载爬虫配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_config(self):
        """保存爬虫配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.crawlers, f, ensure_ascii=False, indent=2)
    
    def add_crawler(self, name: str, code: str, description: str = "", 
                   platform: str = "custom") -> Dict[str, Any]:
        """
        添加新的爬虫代码
        
        Args:
            name: 爬虫名称
            code: 爬虫代码
            description: 爬虫描述
            platform: 平台名称
            
        Returns:
            包含操作结果的字典
        """
        try:
            # Validate crawler name to prevent path injection
            # Only allow alphanumeric characters and underscores
            if not name or not name.replace('_', '').isalnum():
                return {
                    'success': False,
                    'message': '爬虫名称只能包含字母、数字和下划线',
                    'error': 'Invalid crawler name'
                }
            
            # 验证代码是否可以编译
            compile(code, '<string>', 'exec')
            
            # 保存代码到文件 - 使用安全的路径构建
            # Sanitize filename to prevent directory traversal
            safe_name = os.path.basename(name)  # Remove any path components
            crawler_file = os.path.join(self.storage_dir, f"{safe_name}.py")
            
            # Ensure the file path is within storage_dir
            real_storage_dir = os.path.realpath(self.storage_dir)
            real_crawler_file = os.path.realpath(crawler_file)
            if not real_crawler_file.startswith(real_storage_dir):
                return {
                    'success': False,
                    'message': '非法的文件路径',
                    'error': 'Path traversal attempt detected'
                }
            
            with open(crawler_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 更新配置
            self.crawlers[name] = {
                'name': name,
                'description': description,
                'platform': platform,
                'file_path': crawler_file,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'enabled': True
            }
            
            self._save_config()
            
            return {
                'success': True,
                'message': f'爬虫 "{name}" 添加成功',
                'crawler': self.crawlers[name]
            }
            
        except SyntaxError as e:
            return {
                'success': False,
                'message': f'代码语法错误: {str(e)}',
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'添加爬虫失败: {str(e)}',
                'error': str(e)
            }
    
    def update_crawler(self, name: str, code: str = None, 
                      description: str = None, enabled: bool = None) -> Dict[str, Any]:
        """
        更新现有爬虫
        
        Args:
            name: 爬虫名称
            code: 新的爬虫代码（可选）
            description: 新的描述（可选）
            enabled: 是否启用（可选）
            
        Returns:
            包含操作结果的字典
        """
        if name not in self.crawlers:
            return {
                'success': False,
                'message': f'爬虫 "{name}" 不存在'
            }
        
        try:
            # 更新代码
            if code is not None:
                # 验证代码
                compile(code, '<string>', 'exec')
                
                crawler_file = self.crawlers[name]['file_path']
                with open(crawler_file, 'w', encoding='utf-8') as f:
                    f.write(code)
            
            # 更新描述
            if description is not None:
                self.crawlers[name]['description'] = description
            
            # 更新启用状态
            if enabled is not None:
                self.crawlers[name]['enabled'] = enabled
            
            # 更新时间戳
            self.crawlers[name]['updated_at'] = datetime.now().isoformat()
            
            self._save_config()
            
            return {
                'success': True,
                'message': f'爬虫 "{name}" 更新成功',
                'crawler': self.crawlers[name]
            }
            
        except SyntaxError as e:
            return {
                'success': False,
                'message': f'代码语法错误: {str(e)}',
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'更新爬虫失败: {str(e)}',
                'error': str(e)
            }
    
    def delete_crawler(self, name: str) -> Dict[str, Any]:
        """
        删除爬虫
        
        Args:
            name: 爬虫名称
            
        Returns:
            包含操作结果的字典
        """
        if name not in self.crawlers:
            return {
                'success': False,
                'message': f'爬虫 "{name}" 不存在'
            }
        
        try:
            # 删除文件
            crawler_file = self.crawlers[name]['file_path']
            if os.path.exists(crawler_file):
                os.remove(crawler_file)
            
            # 从配置中删除
            del self.crawlers[name]
            self._save_config()
            
            return {
                'success': True,
                'message': f'爬虫 "{name}" 删除成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'删除爬虫失败: {str(e)}',
                'error': str(e)
            }
    
    def get_crawler(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取爬虫信息
        
        Args:
            name: 爬虫名称
            
        Returns:
            爬虫信息字典，如果不存在返回None
        """
        return self.crawlers.get(name)
    
    def list_crawlers(self, platform: str = None, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        列出所有爬虫
        
        Args:
            platform: 过滤平台（可选）
            enabled_only: 只返回启用的爬虫
            
        Returns:
            爬虫列表
        """
        crawlers = list(self.crawlers.values())
        
        if platform:
            crawlers = [c for c in crawlers if c.get('platform') == platform]
        
        if enabled_only:
            crawlers = [c for c in crawlers if c.get('enabled', True)]
        
        return crawlers
    
    def get_crawler_code(self, name: str) -> Optional[str]:
        """
        获取爬虫代码
        
        Args:
            name: 爬虫名称
            
        Returns:
            爬虫代码字符串，如果不存在返回None
        """
        if name not in self.crawlers:
            return None
        
        crawler_file = self.crawlers[name]['file_path']
        if not os.path.exists(crawler_file):
            return None
        
        try:
            with open(crawler_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def load_crawler_module(self, name: str) -> Optional[Any]:
        """
        动态加载爬虫模块
        
        Args:
            name: 爬虫名称
            
        Returns:
            加载的模块对象，如果失败返回None
        """
        if name not in self.crawlers:
            return None
        
        crawler_file = self.crawlers[name]['file_path']
        if not os.path.exists(crawler_file):
            return None
        
        try:
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(name, crawler_file)
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            print(f"加载爬虫模块失败: {e}")
            return None
    
    def execute_crawler(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        执行爬虫
        
        Args:
            name: 爬虫名称
            **kwargs: 传递给爬虫的参数
            
        Returns:
            包含执行结果的字典
        """
        if name not in self.crawlers:
            return {
                'success': False,
                'message': f'爬虫 "{name}" 不存在'
            }
        
        if not self.crawlers[name].get('enabled', True):
            return {
                'success': False,
                'message': f'爬虫 "{name}" 未启用'
            }
        
        try:
            # 加载模块
            module = self.load_crawler_module(name)
            if module is None:
                return {
                    'success': False,
                    'message': f'加载爬虫模块失败'
                }
            
            # 尝试调用标准函数
            if hasattr(module, 'scrape'):
                result = module.scrape(**kwargs)
            elif hasattr(module, 'run'):
                result = module.run(**kwargs)
            elif hasattr(module, 'main'):
                result = module.main(**kwargs)
            else:
                return {
                    'success': False,
                    'message': '爬虫代码中未找到 scrape(), run() 或 main() 函数'
                }
            
            return {
                'success': True,
                'message': f'爬虫 "{name}" 执行成功',
                'result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'执行爬虫失败: {str(e)}',
                'error': str(e)
            }
