# 京盛传媒 企业版智能体

## 概述
多源数据采集 / 自迭代策略引擎 / AI 分析与演化 / SaaS & ERP 示例集成的统一平台。

## 核心功能
- **Amazon 实时爬虫** - 真实Amazon数据采集，支持商品列表和详情页抓取
- **WPS Office 集成** - 正式接入WPS开放平台，支持在线文档协作 🆕
- **数据自动记录** - 所有采集数据自动保存到JSON文件，支持多种存储模式
- **自迭代引擎** - 收集指标 → 发现问题 → 策略组合 → 生成变体 → 沙箱对比评估 → 候选补丁
- **AI 演化** - 日志分析 + 补丁建议生成
- **数据来源与政策追踪** - 多平台数据源管理
- **Telemetry 匿名使用数据**（可选）
- **调度系统** - APScheduler统一管理采集/报告/演化/自学习

## 快速开始

### 1. 环境准备
```bash
# 克隆仓库
git clone <repo-url>
cd 5

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件或设置以下环境变量：
```bash
OPENAI_API_KEY=sk-xxx                    # OpenAI API密钥(可选)
MASTER_KEY=your_master_license_sign_key  # 许可证签名密钥(可选)

# WPS Office 集成 (可选 - 用于生产模式)
WPS_APP_ID=your-wps-app-id              # WPS开放平台应用ID
WPS_APP_SECRET=your-wps-app-secret      # WPS开放平台应用密钥
```

**WPS集成说明：**
- 不配置凭证时，系统使用演示模式（功能体验但数据仅本地存储）
- 配置凭证后，系统使用生产模式（真实调用WPS API，数据同步到云端）
- 详细配置指南请查看：[docs/WPS_INTEGRATION_GUIDE.md](docs/WPS_INTEGRATION_GUIDE.md)

### 3. 启动系统
```bash
# 启动Web界面
streamlit run run_launcher.py

# 或使用批处理文件(Windows)
smart_start.bat
```

## 快速示例代码

### 方式1: 使用示例脚本
```bash
# 运行示例脚本查看所有用法
python examples/amazon_scraper_examples.py
```

### 方式2: Python交互式使用
```python
from scrapers.amazon_scraper import AmazonScraper

# 创建爬虫实例
scraper = AmazonScraper()

# 采集商品列表
products = scraper.scrape_list_page(
    url="https://www.amazon.com/s?k=laptop",
    max_items=50
)

# 采集商品详情
detail = scraper.scrape_product_detail(asin="B08N5WRWNW")

# 保存数据
scraper.save_data(products)
```

### 方式3: 使用便捷函数
```python
from scrapers.amazon_scraper import scrape_amazon

# 快速采集
products = scrape_amazon(
    url="https://www.amazon.com/bestsellers",
    max_items=100,
    deep_detail=True  # 是否采集详情页
)
```

## Amazon爬虫使用指南

### 基础使用

#### 方式1: 通过Web界面
1. 启动系统后，在浏览器中打开 `http://localhost:8501`
2. 选择 "Amazon采集工具" 页面
3. 选择采集模式：
   - **单页采集**: 适合测试或小规模数据采集
   - **批量URL采集**: 适合大规模数据采集

#### 方式2: 通过Python代码
```python
from scrapers.amazon_scraper import AmazonScraper

# 创建爬虫实例
scraper = AmazonScraper()

# 采集商品列表
products = scraper.scrape_list_page(
    url="https://www.amazon.com/s?k=laptop",
    max_items=50
)

# 采集商品详情
detail = scraper.scrape_product_detail(asin="B08N5WRWNW")

# 保存数据
scraper.save_data(products)
```

#### 方式3: 使用便捷函数
```python
from scrapers.amazon_scraper import scrape_amazon

# 快速采集
products = scrape_amazon(
    url="https://www.amazon.com/bestsellers",
    max_items=100,
    deep_detail=True  # 是否采集详情页
)
```

### 支持的URL类型
1. **搜索结果页**: `https://www.amazon.com/s?k=关键词`
2. **分类页面**: `https://www.amazon.com/bestsellers`
3. **具体分类**: `https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics`

### 数据存储

#### 本地存储（默认）
- 所有数据自动保存到 `data/amazon/` 目录
- 文件命名格式: `amazon_products_YYYYMMDD_HHMMSS.json`
- JSON格式包含：
  ```json
  {
    "items": [...],           // 商品列表
    "total_count": 50,        // 总数量
    "scraped_at": "2025-..."  // 采集时间
  }
  ```

#### 商品数据字段
```json
{
  "asin": "B08N5WRWNW",                    // Amazon商品ID
  "title": "Apple MacBook Pro",            // 商品标题
  "price": "$1,299.00",                    // 价格
  "rating": "4.8 out of 5 stars",         // 评分
  "review_count": "1,234 ratings",        // 评论数
  "url": "https://www.amazon.com/dp/...", // 商品链接
  "scraped_at": "2025-10-17T...",         // 采集时间
  "source_url": "https://...",            // 来源URL
  "description": [...],                    // 商品描述(详情模式)
  "brand": "Apple"                         // 品牌(详情模式)
}
```

### 采集策略配置

爬虫支持自动调优，配置文件位于 `config/crawler_iter_config.yaml`:

```yaml
# 测试URL列表
test_urls:
  - "https://www.amazon.com/bestsellers"
  - "https://www.amazon.com/s?k=usb+hub"

# 选择器策略
selector_bundles:
  base:
    list_selectors:
      - "div.s-result-item"
      - "div[data-asin]"
    title_selectors:
      - "span.a-size-medium"
      - "h2 a span"
    price_selectors:
      - "span.a-price-whole"

# 用户代理策略
ua_set:
  desktop:
    - "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
  
# 等待时间配置
wait_time_base:
  min: 1.0
  max: 1.6
```

## 数据自迭代系统

系统自动分析采集效果，发现问题并生成优化策略，在沙箱中测试后自动应用改进。

详细工作流程说明请查看: [自迭代工作流程文档](docs/ITERATION_WORKFLOW.md)

### 工作原理
1. **数据采集** → 爬虫运行并保存数据到 `data/amazon/`
2. **指标收集** → 系统自动分析采集结果和日志
3. **问题检测** → 识别空结果、错误、验证码等问题
4. **策略优化** → 生成改进策略（调整选择器、等待时间等）
5. **沙箱测试** → 在隔离环境测试新策略
6. **自动应用** → 如果改进效果明显，自动应用补丁

### 监控指标
系统自动追踪以下指标：

| 指标 | 说明 | 权重 |
|------|------|------|
| items_total | 抓取到的总商品数 | +0.55 |
| pages_zero | 空结果页面数量 | -0.30 |
| errors_total | 错误次数 | -0.40 |
| captcha_hits | 验证码命中次数 | -0.15 |
| avg_list_time | 平均页面加载时间 | -0.10 |

### 迭代历史记录
所有迭代记录保存在 `logs/iter_history.jsonl`:
```json
{
  "status": "candidate",
  "tag": "abc123",
  "strategies": ["extend_selectors", "adjust_wait_time"],
  "metrics_before": {...},
  "metrics_after": {...},
  "evaluation": {
    "passed": true,
    "raw_score": 0.25
  }
}
```

### 查看迭代结果
```python
# 读取迭代历史
import json

with open('logs/iter_history.jsonl', 'r') as f:
    for line in f:
        record = json.loads(line)
        print(f"状态: {record['status']}")
        print(f"策略: {record.get('strategies', [])}")
        print("---")
```

## 批量采集

### 使用调度器
```python
from core.crawl.dispatcher import run_batch

# 准备URL列表
urls = [
    "https://www.amazon.com/bestsellers",
    "https://www.amazon.com/s?k=laptop",
    "https://www.amazon.com/s?k=headphones"
]

# 批量运行
run_batch(urls, storage_mode="local")
```

### 使用Web界面
1. 选择 "批量URL采集" 模式
2. 输入多个URL（每行一个）
3. 选择存储模式（local/mongo/mysql/cloud）
4. 点击"开始批量采集"

### 定时采集
编辑 `scheduler.py` 配置定时任务：
```python
from apscheduler.schedulers.background import BackgroundScheduler
from scrapers.amazon_scraper import scrape_amazon

scheduler = BackgroundScheduler()

# 每天早上8点采集
scheduler.add_job(
    func=lambda: scrape_amazon("https://www.amazon.com/bestsellers"),
    trigger='cron',
    hour=8,
    minute=0
)

scheduler.start()
```

## 常见问题解决

### 1. 遇到验证码
**问题**: Amazon检测到爬虫并显示验证码
**解决方案**:
- 调整 `WAIT_TIME` 增加延迟
- 启用代理IP轮换
- 减少并发请求数
- 使用更多User-Agent轮换

### 2. 采集数据为空
**问题**: `items_total = 0`
**解决方案**:
- 检查选择器是否有效（Amazon可能更新页面结构）
- 查看 `scraper.log` 日志获取详细错误
- 启用自迭代引擎自动优化

### 3. 请求超时
**问题**: 网络请求超时
**解决方案**:
- 增加 `timeout` 参数
- 检查网络连接
- 使用代理服务器

### 4. 数据格式不统一
**问题**: 不同页面数据格式不一致
**解决方案**:
- 系统已内置多种选择器策略
- 自迭代引擎会自动尝试不同选择器
- 可在配置文件中添加新的选择器

## 高级功能

### 1. 插件系统
扩展策略插件（位于 `plugins/strategies/`）:
```python
# plugins/strategies/my_strategy.py
from core.plugin_system import StrategyPlugin

class MyCustomStrategy(StrategyPlugin):
    name = "my_strategy"
    
    def apply(self, config):
        # 实现自定义策略
        return modified_config
```

### 2. 强化学习调参
启用RL自动调参（`core/rl_auto_tuner.py`）:
- 基于Q-Learning优化参数
- 持续学习和自动调优
- 历史数据驱动决策

### 3. 多平台支持 (28个平台)
系统现已支持28个主流电商平台：
- **Amazon** - 亚马逊（美国、全球）
- **Shopee** - 虾皮（东南亚）
- **eBay** - eBay（全球）
- **AliExpress** - 速卖通
- **Etsy** - 手工艺品市场
- **Mercari** - 日本二手交易
- **Tokopedia** - 印尼电商
- **Lazada** - 东南亚电商
- **Flipkart** - 印度电商
- **Coupang** - 韩国电商
- **Rakuten Japan** - 乐天日本
- **TikTok Shop** - 抖音商城
- **Target** - 塔吉特（美国）
- **Temu** - 拼多多海外版
- **Ozon** - 俄罗斯电商
- **Wildberries** - 俄罗斯电商
- **Yandex Market** - 俄罗斯电商
- **Mercadolibre** - 拉美电商
- **Allegro** - 波兰电商
- **Cdiscount** - 法国电商
- **Otto** - 德国电商
- **Jumia** - 非洲电商
- **Noon** - 中东电商
- **Onbuy** - 英国电商
- **Joom** - 拉脱维亚电商
- **Faire** - 批发市场
- **Fordeal** - 阿联酋电商
- **Fyndia** - 印度电商
- **Falabella** - 智利/拉美电商

快速使用多平台采集：
```python
from scrapers.multi_platform_scraper import scrape_platform

# 采集任意平台数据 / Scrape from any platform
products = scrape_platform(
    platform_name="shopee",
    url="https://shopee.ph/search?keyword=phone",
    max_items=50
)
```

详细文档：[多平台爬虫使用指南](docs/MULTI_PLATFORM_SCRAPER_GUIDE.md)

## 性能优化建议

1. **并发控制**: 单个IP不要超过10个并发请求
2. **延迟设置**: 建议设置1-3秒随机延迟
3. **代理使用**: 大规模采集时使用代理IP池
4. **增量采集**: 避免重复采集已有数据
5. **错误重试**: 设置合理的重试次数和退避策略

## 数据合规说明

⚠️ **重要提示**:
- 遵守Amazon的robots.txt和服务条款
- 合理控制采集频率，避免对服务器造成压力
- 采集的数据仅用于个人研究和学习
- 商业使用需获得相应授权

## 许可证激活
上传 `license.json`（结构参考 `config/schema/license_schema.json`）。未配置 `MASTER_KEY` 的分发节点无法验证签名。

## 日志和监控

### 日志文件
- `scraper.log`: 主日志文件，记录所有采集活动
- `logs/iter_history.jsonl`: 迭代历史记录
- `data/telemetry/`: 遥测数据（可选）

### 日志格式
```
2025-10-17 10:30:45 - scrapers - INFO - 正在获取页面: https://...
2025-10-17 10:30:46 - scrapers - INFO - [LIST_TIME] secs=1.23
2025-10-17 10:30:46 - scrapers - INFO - 使用选择器找到 48 个商品
```

### 监控指标
通过Web界面 "路线图" 页面查看：
- 采集成功率
- 平均响应时间
- 错误趋势
- 迭代优化记录

## 路线图
### 短期 (已完成 ✅)
- ✅ 增加更多平台适配 (Shopee, eBay)
  - 模块：`core/data_fetcher.py`
  - 支持 Amazon, Shopee, eBay 三大平台

### 中期 (已完成 ✅)
- ✅ 策略效果数据驱动 ML 排序
  - 模块：`core/auto_crawler_iter/ml_strategy_ranker.py`
  - 基于随机森林的策略排序
  - 从历史数据学习最优策略
- ✅ i18n 国际化
  - 模块：`core/i18n.py`
  - 支持中文 (zh_CN) 和英文 (en_US)
  - 配置文件：`config/i18n/`

### 长期 (已完成 ✅)
- ✅ 插件化策略与评估器
  - 模块：`core/plugin_system.py`
  - 策略插件接口：`plugins/strategies/`
  - 评估器插件接口：`plugins/evaluators/`
- ✅ 强化学习自动调参
  - 模块：`core/rl_auto_tuner.py`
  - 基于 Q-Learning 的参数优化
  - 支持持续学习和自动调优

查看路线图详情请访问 UI 中的 "路线图" 页面

## 未来增强功能 / Future Enhancements

✅ **已实现 / Implemented:**

### 1. Selenium/Playwright for JavaScript-rendered content
为 JavaScript 呈现的内容添加 Selenium/Playwright

- **模块**: `core/browser_automation.py`
- **功能**: 使用 Playwright 支持抓取 JavaScript 渲染的网站
- **特性**: 支持 Chromium/Firefox/WebKit，无头模式，页面滚动，截图

### 2. Distributed scraping with task queues
使用任务队列实现分布式抓取

- **模块**: `core/task_queue.py`
- **功能**: 基于优先级的任务队列系统，支持多线程工作池
- **特性**: 自动重试，任务状态跟踪，队列统计

### 3. Data validation and deduplication
添加数据验证和重复数据删除

- **模块**: `core/data_validation.py`
- **功能**: 灵活的验证规则，基于哈希的去重
- **特性**: 类型检查，正则验证，长度/范围验证，质量报告

### 4. Real-time monitoring dashboard
创建监控仪表板以查看实时状态

- **模块**: `core/monitoring.py`, `ui/monitoring_view.py`
- **功能**: 实时指标收集和可视化仪表板
- **特性**: 性能跟踪，自动警报，平台统计，时间序列数据

📖 **详细文档**: [docs/FUTURE_ENHANCEMENTS.md](docs/FUTURE_ENHANCEMENTS.md)

🚀 **快速开始**: 运行 `python examples/enhanced_pipeline_demo.py` 查看所有功能的集成演示

---

## 旧组件
`core/ai/scheduler.py` 已被 `scheduler.py` 取代，不建议继续使用。