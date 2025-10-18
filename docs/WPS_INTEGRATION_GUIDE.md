# WPS Office 集成指南 / WPS Office Integration Guide

## 概述 / Overview

本系统已正式接入WPS开放平台，支持真实的WPS在线文档协作功能。系统支持两种运行模式：

The system has been formally integrated with WPS Open Platform, supporting real WPS online document collaboration. The system supports two operation modes:

1. **演示模式 (Demo Mode)** - 无需配置，用于测试和演示
2. **生产模式 (Production Mode)** - 需要WPS API凭证，支持真实API调用

---

## 快速开始 / Quick Start

### 方式一：演示模式 (Demo Mode)

无需任何配置，直接使用：

```bash
# 启动系统
streamlit run run_launcher.py

# 在浏览器中打开 http://localhost:8501
# 选择 "WPS协作" 菜单
# 使用任意账号密码登录（仅用于演示）
```

演示模式特点：
- ✅ 无需注册WPS开放平台账号
- ✅ 可以体验所有功能界面
- ⚠️ 数据仅保存在本地，不会同步到云端
- ⚠️ 不支持真实的多人协作

---

### 方式二：生产模式 (Production Mode)

需要在WPS开放平台注册并获取API凭证。

#### 步骤1：注册WPS开放平台

1. 访问 [WPS开放平台](https://open.wps.cn/)
2. 注册账号并登录
3. 创建应用，获取：
   - `App ID` (应用ID)
   - `App Secret` (应用密钥)

#### 步骤2：配置凭证

**推荐方式：使用环境变量**

```bash
# Linux/macOS
export WPS_APP_ID="your-wps-app-id"
export WPS_APP_SECRET="your-wps-app-secret"

# Windows (PowerShell)
$env:WPS_APP_ID="your-wps-app-id"
$env:WPS_APP_SECRET="your-wps-app-secret"

# Windows (CMD)
set WPS_APP_ID=your-wps-app-id
set WPS_APP_SECRET=your-wps-app-secret
```

**备选方式：通过UI配置**

1. 启动系统并进入"WPS协作"页面
2. 选择"API密钥配置"标签
3. 输入App ID和App Secret
4. 点击"保存配置"

#### 步骤3：OAuth授权登录

生产模式使用OAuth 2.0授权流程，更加安全：

1. 在"OAuth授权"标签页，点击"生成授权链接"
2. 点击生成的链接，在浏览器中完成WPS账号授权
3. 授权成功后，从回调URL中复制`code`参数
4. 在"授权码"输入框中粘贴code，点击"确认授权"

#### 步骤4：开始使用

授权成功后，即可使用所有真实的WPS功能：
- ✅ 创建在线文档（Word/Excel/PPT）
- ✅ 上传本地文件到WPS云端
- ✅ 分享文档给其他用户
- ✅ 实时协作编辑
- ✅ 文档历史版本管理

---

## 功能说明 / Features

### 1. 文档管理 / Document Management

**创建文档 (Create Document)**
- 支持Word、Excel、PPT三种文档类型
- 可设置初始内容
- 自动生成编辑和查看链接

**查看文档列表 (List Documents)**
- 查看所有已创建的文档
- 按类型筛选
- 搜索文档标题
- 快速访问和编辑

### 2. 文件上传 / File Upload

**支持的文件格式**
- Microsoft Office: .doc, .docx, .xls, .xlsx, .ppt, .pptx
- PDF: .pdf
- 文本: .txt

**上传流程**
1. 选择本地文件
2. 点击"开始上传"
3. 文件自动上传到WPS云端
4. 获取在线访问链接

### 3. 协作管理 / Collaboration

**分享文档**
- 支持分享给多个用户
- 可设置权限：查看、编辑、管理
- 自动生成分享链接

**权限说明**
- 👁️ **查看 (View)**: 只能查看文档内容
- ✏️ **编辑 (Edit)**: 可以编辑文档
- 👑 **管理 (Admin)**: 完全控制权限

---

## API参考 / API Reference

### 认证相关 / Authentication

```python
from core.wps_integration import WPSIntegration

wps = WPSIntegration()

# 方式1：密码登录（如API支持）
result = wps.authenticate(username="user@example.com", password="password")

# 方式2：OAuth授权码登录
result = wps.authenticate(code="auth_code", redirect_uri="http://localhost:8501")

# 刷新令牌
result = wps.refresh_token()
```

### 文档操作 / Document Operations

```python
# 创建文档
result = wps.create_document(
    title="项目计划书",
    content="文档初始内容",
    doc_type="doc"  # doc/sheet/ppt
)

# 列出文档
result = wps.list_documents(doc_type="doc", limit=50)

# 分享文档
result = wps.share_document(
    doc_id="doc_123",
    users=["user1@example.com", "user2@example.com"],
    permission="edit"  # view/edit/admin
)
```

### 文件操作 / File Operations

```python
# 上传文件
result = wps.upload_file(
    file_path="/path/to/file.docx",
    folder_id=None  # 可选：指定文件夹
)
```

### 用户信息 / User Info

```python
# 获取用户信息
user_info = wps.get_user_info()

# 获取协作统计
stats = wps.get_collaboration_info()
```

---

## 配置文件 / Configuration

### 配置文件位置
- `config/wps_config.json` - WPS集成配置

### 配置文件结构
```json
{
  "app_id": "your-app-id",
  "app_secret": "your-app-secret",
  "username": "user@example.com",
  "authenticated": true,
  "access_token": "token",
  "refresh_token": "refresh_token",
  "token_expires_at": "2025-10-19T12:00:00",
  "demo_mode": false,
  "documents": [],
  "files": [],
  "shares": []
}
```

### 安全提示 / Security Tips

⚠️ **重要安全建议：**

1. **不要将配置文件提交到Git**
   - 配置文件已添加到`.gitignore`
   - 使用环境变量存储凭证更安全

2. **定期轮换密钥**
   - 建议每3-6个月更换一次App Secret
   - 如发现密钥泄露，立即在WPS平台撤销

3. **最小权限原则**
   - 只申请必需的API权限
   - 不同环境使用不同的应用凭证

4. **监控API使用**
   - 定期检查WPS开放平台的使用统计
   - 注意异常的API调用模式

---

## 故障排查 / Troubleshooting

### 常见问题

**Q1: 提示"未配置WPS API凭证"**
- 检查环境变量是否设置正确
- 或在UI的"API密钥配置"标签页中配置

**Q2: OAuth授权失败**
- 确认App ID和App Secret配置正确
- 检查回调地址是否与WPS平台设置一致
- 确认授权码未过期（通常5-10分钟有效期）

**Q3: API调用返回401错误**
- Access Token可能已过期
- 尝试使用`refresh_token()`刷新令牌
- 或重新进行OAuth授权

**Q4: 文档创建成功但无法打开**
- 检查是否是演示模式（演示模式的URL是模拟的）
- 生产模式下确认WPS API返回的URL格式

**Q5: 文件上传失败**
- 检查文件大小（WPS可能有大小限制）
- 确认文件格式在支持范围内
- 检查网络连接

### 日志查看

系统会记录详细的调试日志：

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)
```

日志会显示：
- API请求和响应
- 认证流程详情
- 错误堆栈信息

---

## 开发指南 / Development Guide

### 添加新功能

扩展WPS集成功能的步骤：

1. 在`core/wps_integration.py`中添加新方法
2. 实现真实API调用和演示模式回退
3. 在`ui/wps_integration.py`中添加UI组件
4. 更新文档

示例：添加删除文档功能

```python
# core/wps_integration.py
def delete_document(self, doc_id: str) -> Dict[str, Any]:
    """删除文档"""
    if self.config.get('demo_mode', True):
        # 演示模式
        self.config['documents'] = [
            d for d in self.config.get('documents', [])
            if d.get('doc_id') != doc_id
        ]
        self._save_config()
        return {'success': True, 'message': '文档已删除 (演示模式)'}
    
    # 生产模式
    result = self._make_api_request('DELETE', f'documents/{doc_id}')
    return result
```

### 测试

创建测试文件 `test/unit/test_wps_integration.py`:

```python
import pytest
from core.wps_integration import WPSIntegration

def test_wps_integration_demo_mode():
    wps = WPSIntegration()
    result = wps.authenticate("test@example.com", "password")
    assert result['success'] is True
    assert result.get('demo_mode') is True

def test_create_document():
    wps = WPSIntegration()
    wps.authenticate("test@example.com", "password")
    result = wps.create_document("Test Doc", "Content", "doc")
    assert result['success'] is True
    assert 'document' in result
```

---

## 更新日志 / Changelog

### v2.0.0 (2025-10-18)
- ✅ 正式接入WPS开放平台
- ✅ 实现OAuth 2.0认证流程
- ✅ 支持真实的文档创建和管理
- ✅ 支持文件上传到WPS云端
- ✅ 支持文档分享和协作
- ✅ 添加Token刷新机制
- ✅ 实现演示模式和生产模式切换
- ✅ 完善错误处理和日志记录

### v1.0.0 (Initial)
- 基础WPS集成框架
- 演示模式实现

---

## 技术支持 / Support

### 资源链接
- [WPS开放平台官网](https://open.wps.cn/)
- [WPS API文档](https://open.wps.cn/docs/)
- [项目GitHub](https://github.com/2927093389zxq-boop/5)

### 联系方式
如有问题或建议，请：
1. 查看本文档的"故障排查"部分
2. 查看系统日志文件
3. 提交GitHub Issue
4. 联系技术支持团队

---

## 许可证 / License

本集成遵循项目整体许可证。使用WPS API需遵守WPS开放平台的服务条款。

---

**最后更新 / Last Updated:** 2025-10-18
**版本 / Version:** 2.0.0
