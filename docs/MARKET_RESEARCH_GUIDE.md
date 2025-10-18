# 市场调研和竞品分析指南
# Market Research and Competitive Analysis Guide

本指南介绍如何使用增强型爬虫和高级分析模块进行市场调研和竞品分析。
This guide explains how to use the enhanced scraper and advanced analysis modules for market research and competitive analysis.

---

## 目录 / Table of Contents

1. [功能概述 / Features Overview](#功能概述--features-overview)
2. [快速开始 / Quick Start](#快速开始--quick-start)
3. [增强型爬虫 / Enhanced Scraper](#增强型爬虫--enhanced-scraper)
4. [高级分析 / Advanced Analysis](#高级分析--advanced-analysis)
5. [周期性调度 / Periodic Scheduling](#周期性调度--periodic-scheduling)
6. [完整工作流程 / Complete Workflow](#完整工作流程--complete-workflow)
7. [最佳实践 / Best Practices](#最佳实践--best-practices)

---

## 功能概述 / Features Overview

### 增强型爬虫功能 / Enhanced Scraper Features

- ✅ **User-Agent 轮换** - 14个不同浏览器的User-Agent自动轮换
- ✅ **智能延时** - 2-5秒随机延时，避免被检测
- ✅ **错误重试** - 自动重试失败的请求（最多3次）
- ✅ **缓存系统** - 基于MD5的缓存，避免重复抓取（24小时TTL）
- ✅ **双格式导出** - 支持CSV和JSON格式
- ✅ **抽样采集** - 智能抽样策略，每类目50-200商品

### 高级分析功能 / Advanced Analysis Features

- ✅ **竞品矩阵分析** - 不同卖家/品牌的价格和评分对比
- ✅ **价格分布图** - 箱线图、直方图、区间统计
- ✅ **关键词云** - 使用jieba分词生成词云图
- ✅ **品牌集中度** - HHI指数、CR4/CR8集中度、市场份额饼图
- ✅ **市场趋势** - 价格、评分、评论数趋势分析
- ✅ **综合报告** - 一键生成包含所有分析的JSON报告

### 周期性调度功能 / Periodic Scheduling Features

- ✅ **每日任务** - 设置固定时间执行（如每天8:00）
- ✅ **每周任务** - 设置特定星期执行（如每周一9:00）
- ✅ **间隔任务** - 按固定间隔执行（如每小时一次）
- ✅ **任务管理** - 暂停、恢复、移除、立即运行

---

## 快速开始 / Quick Start

### 安装依赖 / Install Dependencies

```bash
pip install -r requirements.txt
```

新增依赖包括：
- `jieba` - 中文分词
- `wordcloud` - 词云生成

### 运行示例 / Run Example

```bash
python examples/market_research_example.py
```

选择要运行的示例（1-8）或输入0运行所有示例。

---

## 增强型爬虫 / Enhanced Scraper

### 基本使用 / Basic Usage

```python
from core.enhanced_scraper import EnhancedScraper

# 创建爬虫实例
scraper = EnhancedScraper(
    cache_dir="data/cache",        # 缓存目录
    data_dir="data/enhanced",       # 数据目录
    delay_range=(2.0, 5.0),        # 延时范围(秒)
    max_retries=3,                  # 最大重试次数
    cache_ttl_hours=24              # 缓存有效期(小时)
)

# 获取页面（带缓存和重试）
html = scraper.fetch_page(
    url="https://example.com/products",
    use_cache=True
)

# 抽样采集
products = scraper.sample_scrape(
    urls=[
        "https://example.com/category1",
        "https://example.com/category2",
        "https://example.com/category3"
    ],
    sample_size=150,  # 总共采集150个商品
    use_cache=True
)

# 保存数据
csv_path = scraper.save_to_csv(products, "products.csv")
json_path = scraper.save_to_json(products, "products.json")
```

### User-Agent 轮换 / User-Agent Rotation

系统自动从14个不同的User-Agent中随机选择：

```python
# 自动随机选择User-Agent
agent = scraper._get_random_user_agent()

# 包含的浏览器类型：
# - Chrome (Windows, macOS, Linux)
# - Firefox (Windows, macOS)
# - Safari (macOS)
# - Edge (Windows)
```

### 缓存管理 / Cache Management

```python
# 清理旧缓存（24小时以前）
cleared_count = scraper.clear_cache(older_than_hours=24)

# 清理所有缓存
cleared_count = scraper.clear_cache(older_than_hours=0)
```

### 抽样策略 / Sampling Strategy

```python
# 从多个类目采集样本
categories = {
    "Electronics": "https://example.com/electronics",
    "Books": "https://example.com/books",
    "Home": "https://example.com/home"
}

all_products = []
for category, url in categories.items():
    # 每个类目采集50-100个商品
    products = scraper.sample_scrape([url], sample_size=100)
    all_products.extend(products)
```

---

## 高级分析 / Advanced Analysis

### 基本使用 / Basic Usage

```python
from core.advanced_analysis import AdvancedAnalyzer

# 创建分析器
analyzer = AdvancedAnalyzer(output_dir="data/analysis")

# 准备商品数据
products = [
    {
        'brand': 'Apple',
        'title': 'MacBook Pro',
        'price': '$1299.00',
        'rating': '4.7 out of 5 stars',
        'review_count': '2,456 ratings'
    },
    # ... 更多商品
]
```

### 竞品矩阵分析 / Competitor Matrix Analysis

```python
# 按品牌分析竞品
matrix = analyzer.analyze_competitor_matrix(products, group_by='brand')

print(matrix)
# 输出包括：
# - 平均价格、最低价、最高价、标准差
# - 平均评分、最低评分、最高评分
# - 平均评论数、总评论数
# - 市场份额百分比
```

结果示例：
```
brand    price_mean  price_min  price_max  rating_mean  market_share_percent
Apple    1149.00     999.00     1299.00    4.75         40.0
Dell     1099.00     1099.00    1099.00    4.50         20.0
HP       799.00      799.00     799.00     4.30         20.0
```

### 价格分布分析 / Price Distribution Analysis

```python
# 分析价格分布
price_stats = analyzer.analyze_price_distribution(products, save_plot=True)

print(f"平均价格: ${price_stats['mean']:.2f}")
print(f"中位数: ${price_stats['median']:.2f}")
print(f"标准差: ${price_stats['std']:.2f}")

# 价格区间分布
for range_name, count in price_stats['price_ranges'].items():
    print(f"{range_name}: {count}个商品")
```

生成的图表包括：
- 箱线图（Box Plot）- 显示价格分布和异常值
- 直方图（Histogram）- 显示价格频率分布

### 关键词分析 / Keyword Analysis

```python
# 提取关键词并生成词云
keywords = analyzer.analyze_keywords(
    products,
    text_field='title',      # 分析字段
    top_n=50,                # 返回前50个关键词
    save_wordcloud=True      # 保存词云图
)

# 显示热门关键词
for word, freq in keywords.items():
    print(f"{word}: {freq}次")
```

支持：
- 中文分词（使用jieba）
- 英文分词（基础空格分割）
- 停用词过滤
- 词云图生成

### 品牌集中度分析 / Brand Concentration Analysis

```python
# 分析品牌集中度
brand_analysis = analyzer.analyze_brand_concentration(products)

print(f"总品牌数: {brand_analysis['total_brands']}")
print(f"HHI指数: {brand_analysis['hhi_index']}")
print(f"CR4集中度: {brand_analysis['cr4_percent']}%")
print(f"市场类型: {brand_analysis['concentration_type']}")

# 前10品牌
for brand_info in brand_analysis['top_brands']:
    print(f"{brand_info['brand']}: {brand_info['market_share_percent']}%")
```

集中度指标说明：
- **HHI指数** (Herfindahl-Hirschman Index)
  - > 2500: 高度集中（寡头垄断）
  - 1500-2500: 中度集中
  - < 1500: 低度集中（竞争市场）

- **CR4/CR8**: 前4/8名品牌的市场份额总和

### 市场趋势分析 / Market Trend Analysis

```python
# 分析市场趋势
trends = analyzer.analyze_market_trends(products)

# 价格趋势
print(f"平均价格: ${trends['price_trends']['average']:.2f}")
print(f"价格区间: ${trends['price_trends']['range'][0]:.2f} - ${trends['price_trends']['range'][1]:.2f}")

# 评分趋势
print(f"平均评分: {trends['rating_trends']['average']:.2f}")
print(f"评分分布: {trends['rating_trends']['distribution']}")

# 热销点
for point in trends['hot_selling_points']:
    print(f"- {point}")
```

### 综合报告生成 / Comprehensive Report Generation

```python
# 生成包含所有分析的综合报告
report_path = analyzer.generate_comprehensive_report(
    products,
    report_name="market_report_20251018.json"
)

print(f"报告已保存到: {report_path}")
```

综合报告包含：
1. 竞品矩阵分析数据
2. 价格分布统计
3. 热门关键词
4. 品牌集中度分析
5. 市场趋势分析

同时自动生成：
- 价格分布图（PNG）
- 关键词云图（PNG）
- 品牌份额饼图（PNG）

---

## 周期性调度 / Periodic Scheduling

### 基本使用 / Basic Usage

```python
from core.periodic_scheduler import PeriodicScheduler

# 创建调度器
scheduler = PeriodicScheduler(config_file="config/scheduler_config.json")

# 定义任务函数
def daily_scrape_task():
    print("执行每日市场调研...")
    # 添加你的爬取和分析逻辑
    return "任务完成"

# 添加每日任务（每天8:00执行）
scheduler.add_daily_job(
    job_id='daily_market_research',
    func=daily_scrape_task,
    hour=8,
    minute=0
)

# 添加每周任务（每周一9:00执行）
scheduler.add_weekly_job(
    job_id='weekly_market_report',
    func=daily_scrape_task,
    day_of_week='mon',
    hour=9,
    minute=0
)

# 启动调度器
scheduler.start()

# 查看所有任务
for job in scheduler.get_jobs():
    print(f"任务: {job['id']}, 类型: {job['type']}, 计划: {job['schedule']}")
```

### 任务管理 / Job Management

```python
# 暂停任务
scheduler.pause_job('daily_market_research')

# 恢复任务
scheduler.resume_job('daily_market_research')

# 立即运行任务
scheduler.run_job_now('daily_market_research')

# 移除任务
scheduler.remove_job('daily_market_research')

# 停止调度器
scheduler.shutdown(wait=True)
```

### 间隔任务 / Interval Jobs

```python
# 每小时执行一次
scheduler.add_interval_job(
    job_id='hourly_check',
    func=daily_scrape_task,
    hours=1
)

# 每30分钟执行一次
scheduler.add_interval_job(
    job_id='half_hourly_check',
    func=daily_scrape_task,
    minutes=30
)
```

---

## 完整工作流程 / Complete Workflow

### 端到端市场调研流程 / End-to-End Market Research

```python
from core.enhanced_scraper import EnhancedScraper
from core.advanced_analysis import AdvancedAnalyzer
from core.periodic_scheduler import PeriodicScheduler

# 1. 创建爬虫和分析器
scraper = EnhancedScraper(delay_range=(2.0, 5.0))
analyzer = AdvancedAnalyzer(output_dir="data/analysis")

# 2. 定义市场调研任务
def market_research_task():
    # 2.1 定义要采集的类目
    categories = {
        "Laptops": "https://example.com/laptops",
        "Tablets": "https://example.com/tablets",
        "Smartphones": "https://example.com/smartphones"
    }
    
    # 2.2 采集数据
    all_products = []
    for category, url in categories.items():
        print(f"采集类目: {category}")
        products = scraper.sample_scrape([url], sample_size=100)
        all_products.extend(products)
    
    print(f"总共采集 {len(all_products)} 个商品")
    
    # 2.3 保存原始数据
    scraper.save_to_csv(all_products, "market_data.csv")
    scraper.save_to_json(all_products, "market_data.json")
    
    # 2.4 执行分析
    report_path = analyzer.generate_comprehensive_report(
        all_products,
        report_name=f"market_report_{datetime.now().strftime('%Y%m%d')}.json"
    )
    
    print(f"分析报告已生成: {report_path}")
    return report_path

# 3. 设置周期性执行
scheduler = PeriodicScheduler()

# 每天早上8点执行
scheduler.add_daily_job(
    'daily_market_research',
    market_research_task,
    hour=8,
    minute=0
)

# 每周一生成周报
scheduler.add_weekly_job(
    'weekly_market_report',
    market_research_task,
    day_of_week='mon',
    hour=9,
    minute=0
)

# 4. 启动调度器
scheduler.start()
print("市场调研系统已启动！")

# 保持运行
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    scheduler.shutdown()
    print("系统已关闭")
```

---

## 最佳实践 / Best Practices

### 1. 爬虫设置 / Scraper Settings

**推荐配置：**
```python
scraper = EnhancedScraper(
    delay_range=(2.0, 5.0),   # 2-5秒延时，避免被检测
    max_retries=3,             # 最多重试3次
    cache_ttl_hours=24         # 缓存24小时
)
```

**注意事项：**
- ⚠️ 延时设置：建议2-5秒，太短容易被封IP
- ⚠️ 并发控制：避免同时发起过多请求
- ⚠️ 缓存使用：合理使用缓存避免重复抓取
- ⚠️ 遵守规则：遵守网站的robots.txt和服务条款

### 2. 抽样策略 / Sampling Strategy

**推荐方案：**
```python
# 每个类目采集50-200个商品
sample_sizes = {
    "热门类目": 200,
    "一般类目": 100,
    "小众类目": 50
}

# 均匀分布采集
for category, size in sample_sizes.items():
    products = scraper.sample_scrape([url], sample_size=size)
```

### 3. 数据质量 / Data Quality

**数据验证：**
```python
# 检查必要字段
required_fields = ['title', 'price', 'brand']
valid_products = [
    p for p in products 
    if all(field in p and p[field] for field in required_fields)
]

# 去重
unique_products = {p['id']: p for p in products}.values()
```

### 4. 分析优化 / Analysis Optimization

**批量处理：**
```python
# 分批处理大量数据
batch_size = 1000
for i in range(0, len(products), batch_size):
    batch = products[i:i+batch_size]
    # 处理批次数据
```

**性能监控：**
```python
import time

start_time = time.time()
# 执行分析
elapsed = time.time() - start_time
print(f"分析耗时: {elapsed:.2f}秒")
```

### 5. 调度管理 / Schedule Management

**错误处理：**
```python
def safe_task():
    try:
        # 执行任务
        market_research_task()
    except Exception as e:
        # 记录错误
        logger.error(f"任务执行失败: {e}")
        # 发送通知
        send_notification(f"任务失败: {e}")

scheduler.add_daily_job('safe_daily_task', safe_task, hour=8)
```

**监控和告警：**
```python
# 记录任务执行状态
def monitored_task():
    start_time = datetime.now()
    try:
        result = market_research_task()
        status = "成功"
    except Exception as e:
        result = str(e)
        status = "失败"
    
    duration = (datetime.now() - start_time).seconds
    
    # 保存执行记录
    log_execution({
        'timestamp': start_time,
        'status': status,
        'duration': duration,
        'result': result
    })
```

### 6. 存储管理 / Storage Management

**定期清理：**
```python
# 清理旧缓存
scraper.clear_cache(older_than_hours=48)

# 归档旧数据
import shutil
shutil.move('data/old', 'archive/')
```

**数据备份：**
```python
# 定期备份重要数据
def backup_data():
    timestamp = datetime.now().strftime('%Y%m%d')
    shutil.copytree('data/analysis', f'backup/analysis_{timestamp}')

# 每周备份一次
scheduler.add_weekly_job('backup', backup_data, day_of_week='sun')
```

---

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

**1. 缓存不工作**
```python
# 检查缓存目录权限
import os
print(os.access(scraper.cache_dir, os.W_OK))

# 手动清理缓存
scraper.clear_cache(older_than_hours=0)
```

**2. 分析图表不显示中文**
```python
# 安装中文字体
# Ubuntu: sudo apt-get install fonts-wqy-zenhei
# macOS: 系统自带中文字体

# 设置matplotlib字体
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
```

**3. 内存占用过高**
```python
# 分批处理大数据集
def process_in_batches(products, batch_size=1000):
    for i in range(0, len(products), batch_size):
        batch = products[i:i+batch_size]
        yield analyzer.analyze_competitor_matrix(batch)
```

---

## 技术支持 / Support

如有问题，请查看：
- 示例代码: `examples/market_research_example.py`
- 单元测试: `test/unit/test_*.py`
- 主README: `README.md`

或提交Issue到GitHub仓库。

---

## 更新日志 / Changelog

### v1.0.0 (2025-10-18)
- ✅ 初始版本发布
- ✅ 增强型爬虫引擎
- ✅ 高级分析模块
- ✅ 周期性调度器
- ✅ 完整测试覆盖
- ✅ 详细文档和示例
