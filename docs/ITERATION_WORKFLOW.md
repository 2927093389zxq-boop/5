# Amazon爬虫自迭代工作流程说明
# Amazon Scraper Self-Iteration Workflow Documentation

## 概述 / Overview

本系统实现了Amazon爬虫的自动化迭代优化，通过持续收集运行数据、检测问题、生成优化策略，并在沙箱环境中测试验证，最终自动应用有效的改进。

The system implements automated iterative optimization for the Amazon scraper by continuously collecting runtime data, detecting issues, generating optimization strategies, testing in sandbox environments, and automatically applying effective improvements.

## 工作流程图 / Workflow Diagram

```
┌─────────────────┐
│  1. 数据采集     │
│  Data Collection │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  2. 指标收集     │
│  Metrics Collect │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  3. 问题检测     │
│  Issue Detection │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  4. 策略生成     │
│  Strategy Gen    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  5. 变体构建     │
│  Variant Build   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  6. 沙箱测试     │
│  Sandbox Test    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  7. 评估决策     │
│  Evaluation      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ↓         ↓
 通过/Pass  拒绝/Reject
    │         │
    ↓         ↓
 应用补丁    记录失败
 Apply      Record
    │         │
    └────┬────┘
         │
         ↓
    循环/Loop
```

## 详细说明 / Detailed Description

### 1. 数据采集阶段 / Data Collection Phase

**功能**: 爬虫运行并采集Amazon商品数据

**输出文件**: `data/amazon/amazon_products_YYYYMMDD_HHMMSS.json`

**数据结构**:
```json
{
  "items": [...],
  "total_count": 50,
  "scraped_at": "2025-10-17T10:30:00+00:00"
}
```

### 2. 指标收集阶段 / Metrics Collection Phase

**模块**: `core/auto_crawler_iter/metrics_collector.py`

**收集的指标**:
- `items_total`: 商品总数
- `pages_zero`: 零结果页数
- `errors_total`: 错误总数
- `captcha_hits`: 验证码次数
- `avg_list_time`: 平均耗时

### 3. 问题检测阶段 / Issue Detection Phase

**模块**: `core/auto_crawler_iter/issue_detector.py`

**检测的问题**:
- low_yield (低产出)
- captcha_detected (验证码)
- high_error_rate (高错误率)
- zero_results (零结果)
- slow_performance (性能慢)

### 4. 策略生成阶段 / Strategy Generation Phase

**模块**: `core/auto_crawler_iter/strategy_registry.py`

**可用策略**:
- extend_selectors
- adjust_wait_time
- switch_user_agent
- add_second_pass
- increase_scroll_cycles

### 5-7. 测试评估阶段 / Testing & Evaluation Phase

**模块**: 
- `variant_builder.py` - 构建变体
- `sandbox_executor.py` - 沙箱执行
- `evaluator.py` - 评估结果

**评估公式**:
```
score = Σ (metric_delta * weight)
```

## 快速开始 / Quick Start

### 手动运行一次迭代
```python
from core.auto_crawler_iter.iteration_engine import CrawlerIterationEngine

engine = CrawlerIterationEngine()
result = engine.run_once()

if result['status'] == 'candidate':
    print(f"发现改进! Tag: {result['tag']}")
    engine.apply_patch(result['tag'])
```

### 查看迭代历史
```python
import json

with open('logs/iter_history.jsonl', 'r') as f:
    for line in f:
        record = json.loads(line)
        print(f"{record['status']}: {record.get('strategies', [])}")
```

## 配置文件 / Configuration

主配置: `config/crawler_iter_config.yaml`

```yaml
enabled: true
min_interval_minutes: 30
score_threshold: 0.12
require_error_drop: true

weights:
  items: 0.55
  zero: -0.30
  errors: -0.40
  captcha: -0.15
  time: -0.10
```

## 相关文档 / Related Documentation

- [README.md](../README.md) - 主文档
- [scrapers/amazon_scraper.py](../scrapers/amazon_scraper.py) - 爬虫代码
- [examples/amazon_scraper_examples.py](../examples/amazon_scraper_examples.py) - 使用示例
- [test/unit/test_amazon_scraper.py](../test/unit/test_amazon_scraper.py) - 测试代码

## 监控命令 / Monitoring Commands

```bash
# 查看最新数据
ls -lth data/amazon/ | head -5

# 查看日志
tail -f scraper.log

# 统计指标
jq '.total_count' data/amazon/*.json | awk '{sum+=$1} END {print sum}'

# 查看迭代历史
cat logs/iter_history.jsonl | jq '.status' | sort | uniq -c
```

## 故障排除 / Troubleshooting

1. **无候选补丁**: 降低 `score_threshold`
2. **补丁失败**: 检查文件冲突
3. **性能下降**: 调整等待时间权重

更多详情请参考 README.md
