"""
插件系统基础框架 - 策略和评估器插件化
Plugin System Foundation - Pluggable strategies and evaluators
"""
import os
import importlib.util
import inspect
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional
import json


class StrategyPlugin(ABC):
    """策略插件基类 / Base class for strategy plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """策略名称 / Strategy name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """策略描述 / Strategy description"""
        pass
    
    @abstractmethod
    def apply(self, source_code: str, params: Dict[str, Any]) -> str:
        """
        应用策略到源代码
        Apply strategy to source code
        
        Args:
            source_code: 原始代码 / Original source code
            params: 策略参数 / Strategy parameters
        
        Returns:
            修改后的代码 / Modified source code
        """
        pass
    
    @abstractmethod
    def get_params_schema(self) -> Dict[str, Any]:
        """
        获取参数模式
        Get parameter schema
        
        Returns:
            JSON Schema格式的参数定义 / Parameter definition in JSON Schema format
        """
        pass


class EvaluatorPlugin(ABC):
    """评估器插件基类 / Base class for evaluator plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """评估器名称 / Evaluator name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """评估器描述 / Evaluator description"""
        pass
    
    @abstractmethod
    def evaluate(
        self,
        base_metrics: Dict[str, float],
        new_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        评估指标变化
        Evaluate metrics change
        
        Args:
            base_metrics: 基准指标 / Baseline metrics
            new_metrics: 新指标 / New metrics
        
        Returns:
            评估结果 / Evaluation result
        """
        pass


class PluginManager:
    """插件管理器 / Plugin Manager"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.strategy_plugins: Dict[str, Type[StrategyPlugin]] = {}
        self.evaluator_plugins: Dict[str, Type[EvaluatorPlugin]] = {}
        
        # 确保插件目录存在 / Ensure plugin directory exists
        os.makedirs(plugin_dir, exist_ok=True)
        os.makedirs(os.path.join(plugin_dir, "strategies"), exist_ok=True)
        os.makedirs(os.path.join(plugin_dir, "evaluators"), exist_ok=True)
        
        # 加载所有插件 / Load all plugins
        self._load_plugins()
    
    def _load_plugins(self):
        """加载所有插件 / Load all plugins"""
        self._load_strategy_plugins()
        self._load_evaluator_plugins()
    
    def _load_strategy_plugins(self):
        """加载策略插件 / Load strategy plugins"""
        strategy_dir = os.path.join(self.plugin_dir, "strategies")
        self._load_plugins_from_dir(strategy_dir, StrategyPlugin, self.strategy_plugins)
    
    def _load_evaluator_plugins(self):
        """加载评估器插件 / Load evaluator plugins"""
        evaluator_dir = os.path.join(self.plugin_dir, "evaluators")
        self._load_plugins_from_dir(evaluator_dir, EvaluatorPlugin, self.evaluator_plugins)
    
    def _load_plugins_from_dir(
        self,
        directory: str,
        base_class: type,
        registry: Dict[str, type]
    ):
        """
        从目录加载插件
        Load plugins from directory
        """
        if not os.path.exists(directory):
            return
        
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                filepath = os.path.join(directory, filename)
                module_name = filename[:-3]  # 去掉.py后缀 / Remove .py suffix
                
                try:
                    # 动态导入模块 / Dynamically import module
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # 查找插件类 / Find plugin classes
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if issubclass(obj, base_class) and obj != base_class:
                                instance = obj()
                                registry[instance.name] = obj
                                print(f"已加载插件 / Loaded plugin: {instance.name}")
                
                except Exception as e:
                    print(f"加载插件失败 / Failed to load plugin {filename}: {e}")
    
    def get_strategy(self, name: str) -> Optional[StrategyPlugin]:
        """
        获取策略插件实例
        Get strategy plugin instance
        """
        if name in self.strategy_plugins:
            return self.strategy_plugins[name]()
        return None
    
    def get_evaluator(self, name: str) -> Optional[EvaluatorPlugin]:
        """
        获取评估器插件实例
        Get evaluator plugin instance
        """
        if name in self.evaluator_plugins:
            return self.evaluator_plugins[name]()
        return None
    
    def list_strategies(self) -> List[str]:
        """列出所有策略插件 / List all strategy plugins"""
        return list(self.strategy_plugins.keys())
    
    def list_evaluators(self) -> List[str]:
        """列出所有评估器插件 / List all evaluator plugins"""
        return list(self.evaluator_plugins.keys())
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """
        获取所有插件信息
        Get all plugin information
        """
        strategies_info = []
        for name, plugin_class in self.strategy_plugins.items():
            instance = plugin_class()
            strategies_info.append({
                'name': instance.name,
                'description': instance.description,
                'params_schema': instance.get_params_schema()
            })
        
        evaluators_info = []
        for name, plugin_class in self.evaluator_plugins.items():
            instance = plugin_class()
            evaluators_info.append({
                'name': instance.name,
                'description': instance.description
            })
        
        return {
            'strategies': strategies_info,
            'evaluators': evaluators_info
        }


# 全局插件管理器实例 / Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器 / Get global plugin manager"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
