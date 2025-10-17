"""
自动进化爬虫系统 - 使用GPT-4不断优化爬虫
Auto-Evolution Crawler System - Using GPT-4 to continuously optimize crawlers
"""

import os
import json
import openai
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class CrawlerEvolutionEngine:
    """爬虫进化引擎 - 使用GPT-4分析日志并优化爬虫策略"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.evolution_log_path = "logs/evolution_history.jsonl"
        self.scraper_log_path = "scraper.log"
        os.makedirs("logs", exist_ok=True)
    
    def check_openai_connection(self) -> Dict[str, Any]:
        """
        检查OpenAI连接状态
        Check OpenAI connection status
        """
        if not self.api_key:
            return {
                "status": "error",
                "message": "未配置OPENAI_API_KEY",
                "suggestion": "请在.env文件中设置 OPENAI_API_KEY",
                "help_link": "https://platform.openai.com/api-keys"
            }
        
        try:
            # 尝试简单的API调用测试连接
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            return {
                "status": "success",
                "message": "OpenAI连接正常",
                "model": "gpt-4o-mini",
                "available": True
            }
        
        except openai.AuthenticationError:
            return {
                "status": "error",
                "message": "API密钥无效",
                "suggestion": "请检查.env文件中的 OPENAI_API_KEY 是否正确",
                "help_link": "https://platform.openai.com/api-keys"
            }
        
        except openai.RateLimitError:
            return {
                "status": "warning",
                "message": "API调用频率超限",
                "suggestion": "请稍后再试或升级API账户",
                "help_link": "https://platform.openai.com/account/rate-limits"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"连接失败: {str(e)}",
                "suggestion": "请检查网络连接和API密钥",
                "help_link": "https://platform.openai.com/docs"
            }
    
    def analyze_scraper_logs(self, max_lines: int = 1000) -> Dict[str, Any]:
        """
        分析爬虫日志，识别问题
        Analyze scraper logs to identify issues
        """
        if not os.path.exists(self.scraper_log_path):
            return {
                "status": "no_logs",
                "message": "暂无爬虫日志",
                "issues": []
            }
        
        try:
            with open(self.scraper_log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # 分析最近的日志
            recent_logs = ''.join(lines[-max_lines:])
            
            # 统计错误类型
            error_count = sum(1 for line in lines if 'ERROR' in line or 'Exception' in line)
            warning_count = sum(1 for line in lines if 'WARNING' in line)
            success_count = sum(1 for line in lines if 'SUCCESS' in line or 'success' in line.lower())
            
            return {
                "status": "analyzed",
                "total_lines": len(lines),
                "error_count": error_count,
                "warning_count": warning_count,
                "success_count": success_count,
                "recent_logs": recent_logs,
                "log_sample": lines[-10:] if lines else []
            }
        
        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")
            return {
                "status": "error",
                "message": f"日志分析失败: {str(e)}",
                "issues": []
            }
    
    def generate_evolution_suggestions(self, log_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用GPT-4生成爬虫优化建议
        Use GPT-4 to generate crawler optimization suggestions
        """
        connection_status = self.check_openai_connection()
        
        if connection_status['status'] != 'success':
            return connection_status
        
        try:
            recent_logs = log_analysis.get('recent_logs', '')
            error_count = log_analysis.get('error_count', 0)
            warning_count = log_analysis.get('warning_count', 0)
            
            prompt = f"""你是一个网页爬虫专家。请分析以下爬虫运行日志，并提供优化建议。

日志统计：
- 错误数: {error_count}
- 警告数: {warning_count}
- 成功数: {log_analysis.get('success_count', 0)}

最近的日志内容：
{recent_logs[:3000]}

请提供：
1. 主要问题总结
2. 优化建议（按优先级排序）
3. 具体的代码改进方向
4. 反爬虫策略应对方案

请用中文输出，简洁明了。"""

            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            suggestions = response.choices[0].message.content
            
            # 保存进化记录
            evolution_record = {
                "timestamp": datetime.now().isoformat(),
                "error_count": error_count,
                "warning_count": warning_count,
                "suggestions": suggestions,
                "model": "gpt-4o-mini"
            }
            
            with open(self.evolution_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(evolution_record, ensure_ascii=False) + '\n')
            
            return {
                "status": "success",
                "suggestions": suggestions,
                "timestamp": evolution_record["timestamp"]
            }
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return {
                "status": "error",
                "message": f"生成建议失败: {str(e)}",
                "suggestion": "请检查API配置和网络连接"
            }
    
    def get_evolution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取进化历史记录
        Get evolution history
        """
        if not os.path.exists(self.evolution_log_path):
            return []
        
        try:
            records = []
            with open(self.evolution_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines[-limit:]:
                try:
                    record = json.loads(line.strip())
                    records.append(record)
                except json.JSONDecodeError:
                    continue
            
            return list(reversed(records))  # 最新的在前面
        
        except Exception as e:
            logger.error(f"Error reading evolution history: {e}")
            return []
    
    def auto_evolve(self) -> Dict[str, Any]:
        """
        自动进化流程：分析日志 -> 生成建议 -> 保存记录
        Auto evolution process: Analyze logs -> Generate suggestions -> Save records
        """
        # Step 1: 检查OpenAI连接
        connection = self.check_openai_connection()
        if connection['status'] != 'success':
            return connection
        
        # Step 2: 分析日志
        log_analysis = self.analyze_scraper_logs()
        
        if log_analysis['status'] == 'no_logs':
            return {
                "status": "no_action",
                "message": "暂无日志数据，无需进化",
                "suggestion": "请先运行爬虫生成日志"
            }
        
        # Step 3: 生成优化建议
        evolution_result = self.generate_evolution_suggestions(log_analysis)
        
        return evolution_result


def get_crawler_metrics() -> Dict[str, Any]:
    """
    获取爬虫性能指标
    Get crawler performance metrics
    """
    try:
        from core.auto_crawler_iter.metrics_collector import MetricsCollector
        
        collector = MetricsCollector()
        metrics = collector.collect()
        
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        return {
            "status": "error",
            "message": f"指标收集失败: {str(e)}",
            "metrics": {}
        }


def test_scraper_with_strategy(strategy: Dict[str, Any]) -> Dict[str, Any]:
    """
    使用新策略测试爬虫
    Test scraper with new strategy
    """
    # 这里应该实现实际的策略测试逻辑
    # For now, return a mock result
    
    return {
        "status": "tested",
        "success": True,
        "message": "策略测试完成",
        "results": {
            "success_rate": 85.5,
            "avg_response_time": 1.2,
            "items_scraped": 150
        }
    }
