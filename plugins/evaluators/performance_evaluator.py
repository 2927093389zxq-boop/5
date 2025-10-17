"""
示例评估器插件：性能评估器
Example Evaluator Plugin: Performance Evaluator
"""
from core.plugin_system import EvaluatorPlugin
from typing import Dict, Any


class PerformanceEvaluator(EvaluatorPlugin):
    """性能评估器 / Performance evaluator"""
    
    @property
    def name(self) -> str:
        return "performance_evaluator"
    
    @property
    def description(self) -> str:
        return "基于性能指标评估策略效果 / Evaluate strategy effectiveness based on performance metrics"
    
    def evaluate(
        self,
        base_metrics: Dict[str, float],
        new_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        评估性能变化
        Evaluate performance change
        """
        # 计算关键指标的变化 / Calculate key metric changes
        items_change = new_metrics.get('items_total', 0) - base_metrics.get('items_total', 0)
        errors_change = new_metrics.get('errors_total', 0) - base_metrics.get('errors_total', 0)
        time_change = new_metrics.get('avg_list_time', 0) - base_metrics.get('avg_list_time', 0)
        
        # 计算综合得分 / Calculate composite score
        score = 0.0
        
        # 更多条目是好的 / More items is good
        if items_change > 0:
            score += items_change * 0.5
        
        # 更少错误是好的 / Fewer errors is good
        if errors_change < 0:
            score += abs(errors_change) * 1.0
        
        # 更快时间是好的 / Faster time is good
        if time_change < 0:
            score += abs(time_change) * 0.3
        
        # 判断是否通过 / Determine if passed
        passed = score > 0 and errors_change <= 0
        
        return {
            'score': score,
            'passed': passed,
            'details': {
                'items_change': items_change,
                'errors_change': errors_change,
                'time_change': time_change
            },
            'recommendation': 'apply' if passed else 'reject'
        }
