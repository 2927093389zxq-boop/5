# 企业级功能升级文档
# Enterprise Features Upgrade Documentation

## 概述 Overview

本次升级为系统添加了四大企业级功能模块，全面提升团队协作和数据采集能力。

This upgrade adds four major enterprise-level feature modules to comprehensively improve team collaboration and data collection capabilities.

---

## 1. 爬虫管理中心 🕷️ Crawler Management Center

### 功能特点 Features

- **集中管理**: 统一管理所有爬虫代码，无需分散在多个文件
- **直接粘贴**: 支持直接粘贴/复制爬虫代码，无需手动创建文件
- **动态加载**: 运行时动态加载爬虫模块，无需重启系统
- **一键更新**: 在UI界面点击更新即可应用新爬虫代码
- **执行测试**: 支持在UI界面配置参数并执行爬虫

### 使用方法 Usage

1. **添加爬虫** - Add Crawler
```python
# 在UI的"添加爬虫"标签页中粘贴以下代码模板
# Paste the following code template in the "Add Crawler" tab

import requests
from bs4 import BeautifulSoup

def scrape(url, max_items=10, **kwargs):
    """主要爬取函数 Main scraping function"""
    headers = {'User-Agent': 'Mozilla/5.0...'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    items = []
    for item in soup.select('.item-selector')[:max_items]:
        items.append({
            'title': item.select_one('.title').text.strip(),
            'price': item.select_one('.price').text.strip()
        })
    
    return {
        'success': True,
        'data': items,
        'count': len(items)
    }
```

2. **执行爬虫** - Execute Crawler
   - 切换到"执行爬虫"标签页
   - 选择要执行的爬虫
   - 配置URL和参数
   - 点击"开始执行"

3. **更新爬虫** - Update Crawler
   - 在"编辑爬虫"标签页修改代码
   - 点击"保存更新"立即生效

### 技术架构 Technical Architecture

- **后端**: `core/crawler_manager.py` - 爬虫管理核心逻辑
- **前端**: `ui/crawler_management.py` - 用户界面
- **存储**: `data/custom_crawlers/` - 爬虫代码和配置

---

## 2. WPS Office 集成 📝 WPS Office Integration

### 功能特点 Features

- **账号登录**: 输入WPS账号和密码即可连接
- **在线文档**: 创建和编辑Word、Excel、PPT文档
- **文件上传**: 上传本地文件到WPS云端
- **团队协作**: 分享文档给团队成员，设置协作权限
- **实时同步**: 文档更改实时同步到云端

### 使用方法 Usage

1. **连接WPS账号** - Connect WPS Account
   - 进入"WPS协作"页面
   - 输入WPS账号（邮箱）和密码
   - 点击"登录WPS"

2. **创建文档** - Create Document
   - 在"创建文档"标签页
   - 输入文档标题
   - 选择文档类型（Word/Excel/PPT）
   - 点击"创建文档"
   - 系统会返回文档链接，点击即可在线编辑

3. **上传文件** - Upload File
   - 在"上传文件"标签页
   - 选择本地文件
   - 点击"开始上传"
   - 文件将上传到WPS云端

4. **团队协作** - Team Collaboration
   - 在"协作管理"标签页
   - 选择要分享的文档
   - 输入协作成员邮箱
   - 设置权限（查看/编辑/管理）
   - 点击"分享文档"

### 注意事项 Notes

⚠️ **重要**: 当前版本为演示实现，实际生产环境需要：
- 申请WPS开放平台应用凭证
- 实现OAuth 2.0认证流程
- 调用WPS官方API

### 技术架构 Technical Architecture

- **后端**: `core/wps_integration.py` - WPS集成核心逻辑
- **前端**: `ui/wps_integration.py` - 用户界面
- **配置**: `config/wps_config.json` - WPS配置和认证信息

---

## 3. AI模型集成管理 🤖 AI Model Integration Management

### 功能特点 Features

- **多提供商支持**: 支持10+主流AI提供商
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude 3)
  - Google AI (Gemini)
  - Cohere
  - HuggingFace
  - Azure OpenAI
  - DeepSeek
  - Moonshot AI (月之暗面)
  - Zhipu AI (智谱)
  - Baidu (文心一言)

- **统一管理**: 在API管理模块中集中配置所有AI模型
- **模型测试**: 一键测试模型连接是否正常
- **详细指南**: 提供每个平台的API密钥获取指南

### 使用方法 Usage

1. **添加AI模型** - Add AI Model
   - 进入"API管理" → "AI模型集成"标签页
   - 点击"添加模型"
   - 选择AI提供商（如OpenAI）
   - 选择模型（如gpt-4）
   - 输入API密钥
   - 配置参数（温度、最大Token等）
   - 点击"保存配置"

2. **测试模型** - Test Model
   - 在"测试模型"标签页
   - 选择已配置的模型
   - 输入测试提示词
   - 点击"开始测试"
   - 查看模型响应

3. **管理模型** - Manage Models
   - 在"已配置模型"标签页查看所有模型
   - 可以启用/禁用模型
   - 可以删除不需要的模型配置

### 支持的AI提供商 Supported AI Providers

| 提供商 | 模型示例 | API获取地址 |
|--------|---------|------------|
| OpenAI | GPT-4, GPT-3.5-Turbo | https://platform.openai.com/ |
| Anthropic | Claude 3 Opus/Sonnet | https://console.anthropic.com/ |
| Google AI | Gemini Pro | https://makersuite.google.com/ |
| Cohere | Command | https://dashboard.cohere.ai/ |
| HuggingFace | 自定义模型 | https://huggingface.co/ |
| DeepSeek | DeepSeek Chat/Coder | https://platform.deepseek.com/ |
| Moonshot | Moonshot v1 | https://platform.moonshot.cn/ |
| Zhipu AI | GLM-4 | https://open.bigmodel.cn/ |
| Baidu | 文心一言 | https://cloud.baidu.com/ |

### 技术架构 Technical Architecture

- **后端**: `core/ai_model_manager.py` - AI模型管理核心
- **前端**: `ui/ai_model_integration.py` - 用户界面
- **配置**: `config/ai_models_config.json` - AI模型配置

---

## 4. 企业协作功能 👥 Enterprise Collaboration Features

### 功能特点 Features

- **团队管理**: 创建团队，添加成员，设置团队负责人
- **项目管理**: 创建项目，关联团队，追踪项目状态
- **任务看板**: Kanban风格的任务管理（待办/进行中/审核/完成）
- **团队消息**: 成员间发送消息和通知
- **成员管理**: 统一管理所有团队成员信息

### 使用方法 Usage

1. **创建团队** - Create Team
   - 进入"企业协作" → "团队管理"
   - 点击"创建新团队"
   - 输入团队名称和描述
   - 选择团队负责人
   - 点击"创建"

2. **添加成员** - Add Members
   - 在"成员管理"标签页
   - 点击"添加成员"
   - 输入用户名、邮箱、角色、部门
   - 点击"添加"

3. **创建项目** - Create Project
   - 在"项目管理"标签页
   - 点击"创建新项目"
   - 输入项目名称和描述
   - 选择关联团队
   - 设置项目状态和优先级
   - 点击"创建"

4. **任务管理** - Task Management
   - 在"任务看板"标签页
   - 选择项目
   - 点击"创建新任务"
   - 输入任务详情
   - 分配负责人
   - 设置优先级和截止日期
   - 任务会显示在Kanban看板上
   - 点击箭头按钮移动任务状态

5. **团队消息** - Team Messages
   - 在"团队消息"标签页
   - 选择当前用户
   - 选择接收者
   - 输入消息内容
   - 点击"发送"

### 数据结构 Data Structure

系统存储以下协作数据：
- 用户信息（users.json）
- 团队信息（teams.json）
- 项目信息（projects.json）
- 任务信息（tasks.json）
- 消息记录（messages.json）

### 技术架构 Technical Architecture

- **后端**: `core/collaboration_manager.py` - 协作管理核心
- **前端**: `ui/enterprise_collaboration.py` - 用户界面
- **存储**: `data/collaboration/` - 协作数据存储

---

## 系统集成 System Integration

### 菜单结构更新 Menu Structure Update

新功能已集成到主菜单"智能体平台"中：

```
智能体平台
├── 主页
├── 智能分析
├── 权威数据中心
├── YouTube
├── TikTok
├── Amazon采集工具
├── 爬虫管理 🆕
├── WPS协作 🆕
├── API管理
│   └── AI模型集成 🆕 (新标签页)
├── 企业协作 🆕
├── 系统概览
└── 日志与设置
```

### 启动系统 Start System

```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 启动Streamlit应用
streamlit run run_launcher.py
```

### 访问功能 Access Features

1. 在浏览器中打开 `http://localhost:8501`
2. 在侧边栏选择"智能体平台"
3. 从功能列表中选择新功能：
   - 爬虫管理
   - WPS协作
   - API管理 → AI模型集成
   - 企业协作

---

## 技术特性 Technical Features

### 模块化设计 Modular Design

每个功能都采用独立的模块设计：
- **核心逻辑**: `core/` 目录下的管理类
- **用户界面**: `ui/` 目录下的Streamlit组件
- **数据存储**: `data/` 或 `config/` 目录下的JSON文件

### 安全性 Security

- API密钥采用部分隐藏显示
- 密码输入使用password类型
- 数据存储在本地，用户完全控制

### 扩展性 Extensibility

- 爬虫管理支持动态加载自定义代码
- AI模型管理支持添加新的提供商
- 协作功能可扩展更多工作流

---

## 最佳实践 Best Practices

### 爬虫管理 Crawler Management

1. **代码规范**: 确保爬虫代码包含 `scrape()`, `run()` 或 `main()` 函数
2. **错误处理**: 在爬虫中添加try-except错误处理
3. **返回格式**: 统一返回包含success、data的字典格式

### WPS协作 WPS Collaboration

1. **API凭证**: 生产环境需在WPS开放平台注册应用
2. **权限管理**: 合理设置文档分享权限
3. **备份策略**: 重要文档建议同时备份到本地

### AI模型管理 AI Model Management

1. **成本控制**: 注意各模型的调用费用
2. **速率限制**: 遵守各平台的API调用限制
3. **模型选择**: 根据任务需求选择合适的模型

### 企业协作 Enterprise Collaboration

1. **角色分配**: 合理分配成员角色（admin/manager/member）
2. **项目规划**: 先创建团队再创建项目
3. **任务追踪**: 定期更新任务状态保持看板准确

---

## 故障排除 Troubleshooting

### 爬虫无法执行

**问题**: 爬虫执行失败
**解决方案**:
1. 检查代码语法是否正确
2. 确保包含必要的入口函数
3. 查看错误信息并修复

### WPS连接失败

**问题**: 无法连接WPS账号
**解决方案**:
1. 当前版本为演示实现，检查网络连接
2. 生产环境需配置真实的WPS API凭证

### AI模型测试失败

**问题**: 模型测试返回错误
**解决方案**:
1. 验证API密钥是否正确
2. 检查API端点URL是否准确
3. 确认账户余额充足

### 协作数据丢失

**问题**: 协作数据不见了
**解决方案**:
1. 检查 `data/collaboration/` 目录
2. 确认JSON文件未被删除或损坏
3. 如有备份，恢复备份文件

---

## 版本信息 Version Information

- **版本号**: v2.0
- **发布日期**: 2025-10-18
- **主要更新**:
  - 🆕 爬虫管理中心
  - 🆕 WPS Office集成
  - 🆕 AI模型集成管理（10+提供商）
  - 🆕 企业协作功能

---

## 反馈与支持 Feedback & Support

如有问题或建议，请：
- 查看系统内的"新手指南"
- 检查本文档的故障排除章节
- 联系技术支持团队

For questions or suggestions:
- Check the "Beginner's Guide" in the system
- Review the Troubleshooting section in this document
- Contact the technical support team
