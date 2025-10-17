# 京盛传媒 企业版智能体

## 概述
多源数据采集 / 自迭代策略引擎 / AI 分析与演化 / SaaS & ERP 示例集成的统一平台。

## 核心功能
- Amazon 爬虫与自动调优（配置块注入 # === AUTO_TUNING_CONFIG_START/END ===）
- 自迭代引擎：收集指标 -> 发现问题 -> 策略组合 -> 生成变体 -> 沙箱对比评估 -> 候选补丁
- AI 演化：日志分析 + 补丁建议生成
- 数据来源与政策追踪
- Telemetry 匿名使用数据（可选）
- 调度系统（APScheduler）统一管理采集/报告/演化/自学习

## 快速开始
```bash
git clone <repo-url>
cd -4
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run run_launcher.py
```

## 环境变量示例
```
OPENAI_API_KEY=sk-xxx
MASTER_KEY=your_master_license_sign_key
```

## 许可证激活
上传 `license.json`（结构参考 `config/schema/license_schema.json`）。未配置 `MASTER_KEY` 的分发节点无法验证签名。

## 自迭代配置
- 主配置：`config/crawler_iter_config.yaml`
- 阈值：`config/auto_iter_thresholds.yaml`
- 历史记录：`logs/iter_history.jsonl`

## 指标统一
| 字段 | 含义 |
|------|------|
| items_total | 抓取到的总条目（测试用） |
| pages_zero | 空结果页面数量 |
| errors_total | 错误次数（异常或失败） |
| captcha_hits | 验证码命中次数（日志检测） |
| avg_list_time | 每测试 URL 平均耗时 (s) |

## 权重示例
在 `crawler_iter_config.yaml` 中：
```
weights:
  items_total: 0.55
  pages_zero: -0.30
  avg_list_time: -0.10
  errors_total: -0.40
  captcha_hits: -0.15
```

## Telemetry
- 每日单文件：`data/telemetry/telemetry_YYYYMMDD.jsonl`
- 可在许可证上传时关闭或启用
- 特征使用短窗口去重与可选匿名化

## 数据管道 (Data Pipeline)
自动化数据获取、验证、匿名化和种子生成流程：
- 多源数据获取：REST API、文件、手动导入
- JSON Schema 验证
- 字段级匿名化（邮箱、电话等）
- 种子数据生成与血缘追踪
- CI 集成与自动化测试

详细文档：
- 快速开始：[QUICKSTART.md](QUICKSTART.md)
- 完整文档：[data/README.md](data/README.md)

基本使用：
```bash
# 获取数据
node scripts/fetch_source.mjs

# 处理与验证
node scripts/process_data.mjs

# 生成种子文件
node scripts/generate_seeds.mjs
```

## 调度
`scheduler.py` 使用 APScheduler：
- 市场采集：interval
- 每日报告：cron
- 演化检查：interval
- 自学习：cron（占位）

## 测试（示例）
安装 pytest 后运行：
```bash
pytest -q
```

## 安全注意
- 不要提交真实 MASTER_KEY 到公共仓库
- 建议使用代理与限速防封禁
- 日志中避免包含敏感数据（已简化）

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

## 旧组件
`core/ai/scheduler.py` 已被 `scheduler.py` 取代，不建议继续使用。