# Amazon 爬虫程序
## Amazon Crawler

一个功能完整的Amazon网站数据采集工具，支持商品列表、详情和评论的采集，具备自动重试、错误处理和数据持久化功能。

## 功能特点

- **多类型页面支持**: 采集搜索结果页、商品详情页、评论页
- **命令行参数支持**: 灵活配置各种参数，适合自动化和脚本调用
- **自动重试机制**: 遇到网络问题或验证码时自动重试
- **数据持久化**: 将采集的数据保存为结构化JSON文件
- **多种选择器策略**: 内置多种选择器，适应Amazon页面变化
- **批量URL处理**: 支持从文件读取多个URL进行批量采集
- **详细日志记录**: 实时记录采集进度和状态
- **自定义配置**: 可配置等待时间、重试次数、代理等
- **丰富的元数据**: 记录采集时间、来源等信息

## 安装依赖

确保您已安装Python 3.6+，然后安装所需的依赖包：

```bash
pip install requests beautifulsoup4 lxml
```

## 文件结构

```
.
├── amazon_crawler.py         # 主爬虫程序文件
├── README_amazon_crawler.md   # 本说明文档
└── data/                     # 数据保存目录
    └── amazon/              # Amazon数据子目录
```

## 命令行参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--url` | Amazon搜索页面URL | 无（必需或使用--batch-file） |
| `--batch-file` | 包含多个URL的文本文件路径 | 无（必需或使用--url） |
| `--output-dir` | 数据输出目录 | `data/amazon` |
| `--max-items` | 最大采集商品数量 | `50` |
| `--deep-detail` | 采集商品详细信息 | `False` |
| `--include-reviews` | 采集商品评论 | `False` |
| `--max-reviews` | 每个商品最大评论数 | `5` |
| `--min-wait` | 最小等待时间(秒) | `1.0` |
| `--max-wait` | 最大等待时间(秒) | `3.0` |
| `--max-retries` | 最大重试次数 | `3` |
| `--timeout` | 请求超时时间(秒) | `30` |
| `--proxy` | 代理服务器地址 | 无 |

## 使用方法

### 通过启动脚本一键启动 (推荐)

现在您可以通过运行 `smart_start.bat` 一键启动爬虫程序，并使用所有功能：

1. 双击运行 `smart_start.bat`
2. 等待系统启动基础服务
3. 在弹出的功能菜单中选择：
   - 选项 1: 交互式模式 - 可配置所有爬虫参数
   - 选项 2: 基础模式 - 仅需输入URL即可快速启动
   - 选项 3: 批量模式 - 处理多个URL

启动脚本会自动处理虚拟环境和依赖安装，提供友好的交互式界面。

### 基本使用示例

```bash
# 单URL搜索结果采集
python amazon_crawler.py --url "https://www.amazon.com/s?k=您的搜索关键词" --max-items 20

# 批量URL处理
# 首先创建一个包含URL列表的文本文件（例如 urls.txt）
python amazon_crawler.py --batch-file urls.txt --max-items 10
```

### 高级使用示例

```bash
# 采集商品详细信息
python amazon_crawler.py --url "https://www.amazon.com/s?k=您的搜索关键词" --deep-detail --max-items 10

# 采集商品评论
python amazon_crawler.py --url "https://www.amazon.com/s?k=您的搜索关键词" --include-reviews --max-reviews 3

# 自定义配置
python amazon_crawler.py --url "https://www.amazon.com/s?k=您的搜索关键词" --min-wait 2.5 --max-wait 5.0 --max-retries 5
```

### 批量URL文件格式

创建一个文本文件（例如 `urls.txt`），每行一个URL：

```
https://www.amazon.com/s?k=关键词1
https://www.amazon.com/s?k=关键词2
https://www.amazon.com/s?k=关键词3
```

## 注意事项

1. **遵守Amazon的服务条款**: 使用本爬虫前请确保您的行为符合Amazon的服务条款和使用政策。

2. **合理设置请求频率**: 避免过于频繁的请求，否则可能会触发Amazon的限流机制或验证码。
   - 建议将等待时间设置在2秒以上
   - 对于大量数据采集，考虑使用代理

3. **验证码处理**: 程序会尝试自动重试遇到验证码的情况，但在某些情况下可能需要手动处理或更换IP。

4. **页面变化**: Amazon网站结构可能会定期更新，导致选择器失效。如果采集结果为空，请检查选择器是否需要更新。

5. **错误处理**: 程序内置了基本的错误处理，但在网络不稳定或Amazon网站更新时仍可能失败。

6. **数据准确性**: 采集的数据可能包含不一致或不完整的信息，建议在关键应用中进行验证。

## 许可证

本项目仅供学习和研究使用。使用前请确保遵守相关法律法规和网站服务条款。

## 免责声明

使用本爬虫程序产生的一切后果由使用者自行承担。开发者不对任何因使用本程序而导致的问题负责，包括但不限于违反网站服务条款、法律责任、数据准确性等问题。