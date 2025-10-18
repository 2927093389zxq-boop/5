# 数据政策说明 / Data Policy

## 📢 重要声明 / Important Declaration

**本系统不包含任何AI生成的示例数据或预置数据。**

**This system does NOT contain any AI-generated sample data or pre-populated data.**

---

## 🚫 无示例数据 / No Sample Data

本系统设计为"零示例数据"架构，确保：

This system is designed with a "zero sample data" architecture, ensuring:

1. **真实性** - 所有分析基于真实数据
2. **隐私性** - 无预置数据泄露风险
3. **灵活性** - 用户完全控制数据来源
4. **合规性** - 符合数据保护法规要求

---

## 📥 数据获取方式 / Data Acquisition Methods

### 方式1: 用户上传 / Method 1: User Upload

**位置**: 智能分析 → 文件上传与分析

**支持格式**:
- Word文档 (.docx, .doc)
- PDF文件 (.pdf)
- Excel表格 (.xlsx, .xls)
- CSV数据 (.csv)
- JSON数据 (.json)
- 文本文件 (.txt)

**使用场景**:
- 上传您自己的市场调研报告
- 导入现有的产品数据
- 分析第三方提供的数据文件

### 方式2: 爬虫采集 / Method 2: Crawler Collection

**配置位置**: 
- 智能分析 → 数据爬取配置
- Amazon采集工具（专用）

**支持平台**:
- Amazon
- eBay
- Etsy
- Shopee
- TikTok
- YouTube
- 其他28个主流电商平台

**使用场景**:
- 自动采集电商平台数据
- 定时更新市场信息
- 批量获取产品数据

### 方式3: API接入 / Method 3: API Integration

**配置位置**: API管理 → 添加新API

**支持服务**:
- **OpenAI API** - AI分析和智能总结
- **Google APIs** - YouTube数据、搜索数据
- **Amazon Product APIs** - 第三方Amazon数据服务
- **其他第三方APIs** - RapidAPI, ScraperAPI等

**使用场景**:
- 接入企业级数据服务
- 使用第三方数据提供商
- 整合多个数据源

---

## 📁 数据存储位置 / Data Storage Locations

### 本地存储 / Local Storage

```
data/
├── amazon/          # Amazon爬虫采集的数据（空目录）
├── youtube/         # YouTube分析数据（空目录）
├── tiktokshop/      # TikTok Shop数据
│   └── example_tiktokshop.json  # ⚠️ 仅为数据格式示例
├── analysis_results_*.json  # 分析结果（用户生成）
└── uploads/         # 用户上传的文件（空目录）
```

**注意**: 
- `example_tiktokshop.json` 仅展示数据结构格式，不包含真实产品信息
- 所有 `*_example.json` 文件仅用于说明数据格式，非实际数据

### 云端存储（可选）/ Cloud Storage (Optional)

支持配置以下云存储服务：
- 阿里云 OSS
- 腾讯云 COS
- AWS S3
- Google Cloud Storage

---

## 🔍 示例文件说明 / Example File Explanation

### `tiktokshop/example_tiktokshop.json`

**目的**: 展示TikTok Shop数据的JSON格式结构

**内容**: 
```json
{
  "platform": "tiktokshop",
  "items": [
    {
      "title": "Test Product 1",
      "price": "$19.99"
    }
  ],
  "total_count": 2
}
```

**状态**: 这是一个格式模板，不是真实的产品数据

**用途**: 
- 让开发者了解数据结构
- 帮助用户准备自己的数据格式
- 供系统测试使用（不用于生产分析）

---

## ✅ 首次使用指南 / First-Time Setup Guide

### 步骤1: 配置API密钥

1. 进入"API管理"
2. 添加所需的API服务（OpenAI、YouTube等）
3. 参考平台提供的获取指南

### 步骤2: 选择数据获取方式

**选项A: 立即开始分析**
- 上传您已有的数据文件
- 系统立即进行分析

**选项B: 配置自动采集**
- 设置爬虫采集目标平台
- 配置采集频率和数量
- 等待自动采集完成

**选项C: 接入API数据源**
- 配置第三方数据API
- 设置数据同步规则
- 实时获取最新数据

### 步骤3: 开始分析

1. 确保有数据可用（上传、采集或API获取）
2. 进入"智能分析"
3. 选择数据源
4. 点击"开始智能分析"

---

## 🛡️ 数据安全与隐私 / Data Security & Privacy

### 本地存储

- 所有数据默认存储在本地 `data/` 目录
- 您完全控制数据的访问和使用
- 系统不会自动上传数据到任何云服务

### 云存储（可选）

- 仅在您明确配置后才使用云存储
- 您需要提供自己的云服务凭证
- 数据加密传输和存储

### API调用

- API密钥加密存储
- 仅在需要时调用第三方API
- 您可以随时删除API配置

### 数据删除

所有用户数据可随时删除：
```bash
# 删除所有采集数据
rm -rf data/amazon/*
rm -rf data/youtube/*

# 删除分析结果
rm -f data/analysis_results_*.json
```

---

## 📊 数据使用合规 / Data Usage Compliance

### 爬虫采集注意事项

1. **遵守robots.txt** - 系统会检查目标网站的爬虫规则
2. **速率限制** - 自动控制请求频率，避免对服务器造成压力
3. **个人使用** - 采集数据仅用于个人研究和学习
4. **商业使用** - 需获得相应平台的授权

### API使用注意事项

1. **遵守API服务条款** - 各平台API有使用限制
2. **密钥保密** - 不要分享您的API密钥
3. **费用管理** - 注意API调用产生的费用
4. **数据使用权限** - 了解API数据的使用范围

---

## ❓ 常见问题 / FAQ

### Q1: 系统是否包含示例产品数据？

**A**: 不包含。唯一的 `example_tiktokshop.json` 只是格式示例，不是真实产品数据。

### Q2: 首次使用时如何获取数据？

**A**: 三种方式：
1. 上传您自己的数据文件
2. 配置爬虫自动采集
3. 接入第三方API服务

### Q3: 能否使用公开的示例数据集？

**A**: 可以！您可以：
1. 下载Kaggle、GitHub等平台的公开数据集
2. 通过"文件上传"功能导入系统
3. 进行分析和研究

### Q4: 数据存储在哪里？

**A**: 
- 默认：本地 `data/` 目录
- 可选：您配置的云存储服务

### Q5: 如何确保数据安全？

**A**: 
- 本地存储由您完全控制
- API密钥加密保存
- 支持自定义云存储加密
- 可随时删除数据

---

## 📞 技术支持 / Technical Support

如有数据相关问题，请：

1. 查看"系统概览"中的"新手指南"
2. 阅读"API管理"中的获取指南
3. 检查各模块的提示信息（ℹ️ 图标）
4. 联系技术支持团队

---

## 📅 更新日期 / Last Updated

2025-10-18

---

**总结 / Summary**: 本系统是一个"自带数据"（Bring Your Own Data）平台，不预置任何真实或AI生成的示例数据。您完全控制数据的来源、存储和使用方式。
