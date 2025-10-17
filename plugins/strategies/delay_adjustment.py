"""
示例策略插件：延迟调整策略
Example Strategy Plugin: Delay Adjustment Strategy
"""
from core.plugin_system import StrategyPlugin
from typing import Dict, Any
import re


class DelayAdjustmentStrategy(StrategyPlugin):
    """延迟调整策略 / Delay adjustment strategy"""
    
    @property
    def name(self) -> str:
        return "delay_adjustment"
    
    @property
    def description(self) -> str:
        return "调整请求延迟时间 / Adjust request delay time"
    
    def apply(self, source_code: str, params: Dict[str, Any]) -> str:
        """
        应用延迟调整到源代码
        Apply delay adjustment to source code
        """
        delay_value = params.get('delay', 1.0)
        
        # 查找并替换delay相关代码 / Find and replace delay-related code
        patterns = [
            (r'time\.sleep\([\d.]+\)', f'time.sleep({delay_value})'),
            (r'delay\s*=\s*[\d.]+', f'delay = {delay_value}'),
            (r'DELAY\s*=\s*[\d.]+', f'DELAY = {delay_value}')
        ]
        
        modified_code = source_code
        for pattern, replacement in patterns:
            modified_code = re.sub(pattern, replacement, modified_code)
        
        return modified_code
    
    def get_params_schema(self) -> Dict[str, Any]:
        """获取参数模式 / Get parameter schema"""
        return {
            "type": "object",
            "properties": {
                "delay": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 10.0,
                    "default": 1.0,
                    "description": "延迟时间(秒) / Delay time (seconds)"
                }
            },
            "required": ["delay"]
        }
