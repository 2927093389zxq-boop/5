# Security Notice - 安全提示

⚠️ **重要安全提示 / Important Security Notice**

## Demo vs Production 演示版 vs 生产环境

### 当前状态 Current State

本仓库包含的配置文件是**演示用途**，包含测试凭证和示例数据：
- `config/wps_config.json` - WPS演示配置
- `config/ai_models_config.json` - AI模型演示配置
- `demo_enterprise_features.py` - 演示脚本

These configuration files are for **DEMONSTRATION PURPOSES ONLY** and contain test credentials and sample data.

### 生产环境部署 Production Deployment

**在生产环境中，您必须：**

1. **删除或替换演示配置文件**
   ```bash
   rm config/wps_config.json
   rm config/ai_models_config.json
   ```

2. **使用环境变量存储敏感信息**
   ```bash
   export OPENAI_API_KEY="your-real-key"
   export WPS_APP_ID="your-wps-app-id"
   export WPS_APP_SECRET="your-wps-secret"
   ```

3. **将敏感配置添加到 .gitignore**
   ```
   config/api_keys.json
   config/ai_models_config.json
   config/wps_config.json
   ```

4. **使用密钥管理服务**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - 其他企业级密钥管理系统

### API密钥安全最佳实践 API Key Security Best Practices

✅ **应该做 DO:**
- 使用环境变量存储API密钥
- 使用密钥管理服务
- 定期轮换API密钥
- 使用最小权限原则
- 监控API使用情况

❌ **不应该做 DON'T:**
- 将API密钥提交到Git仓库
- 在代码中硬编码密钥
- 将密钥分享给未授权人员
- 使用同一密钥用于开发和生产
- 忽略密钥泄露警告

### 检测泄露的密钥 Detecting Leaked Keys

如果您的API密钥被泄露：

1. **立即撤销密钥**
   - OpenAI: https://platform.openai.com/api-keys
   - Google Cloud: https://console.cloud.google.com/
   - 其他平台的相应控制台

2. **生成新密钥**
   - 在相应平台生成新的API密钥
   - 更新您的生产环境配置

3. **检查使用记录**
   - 查看API调用日志
   - 检查是否有未授权使用
   - 如有异常，联系平台支持

### 合规性 Compliance

根据您所在行业和地区，您可能需要遵守：
- GDPR (欧盟通用数据保护条例)
- CCPA (加州消费者隐私法案)
- SOC 2 (服务组织控制)
- ISO 27001 (信息安全管理)
- 其他相关法规

### 联系支持 Contact Support

如有安全问题或疑虑，请：
- 查看项目文档
- 联系系统管理员
- 咨询安全团队

---

**最后更新 Last Updated:** 2025-10-18
