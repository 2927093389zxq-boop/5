"""
API管理模块 - 保存和管理第三方API配置
API Management Module - Save and manage third-party API configurations
"""

import streamlit as st
import json
import os
from datetime import datetime

CONF_PATH = "config/api_keys.json"

def save_apis(apis):
    """Saves the list of APIs to the JSON file."""
    os.makedirs(os.path.dirname(CONF_PATH), exist_ok=True)
    with open(CONF_PATH, "w", encoding="utf-8") as f:
        json.dump(apis, f, ensure_ascii=False, indent=2)

def load_apis():
    """Loads the list of APIs from the JSON file."""
    if not os.path.exists(CONF_PATH):
        return []
    try:
        with open(CONF_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def render_api_admin():
    """Renders the optimized API management page."""
    st.header("🔗 API配置管理中心")
    st.markdown("统一管理所有第三方API配置，支持多平台数据接口")
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📋 已保存API", "➕ 添加新API", "📊 使用统计"])
    
    apis = load_apis()
    
    with tab1:
        st.markdown("### 📋 已配置的API接口")
        
        if not apis:
            st.info("暂无API配置，请在'添加新API'标签页中添加")
        else:
            # 搜索功能
            search = st.text_input("🔍 搜索API", placeholder="输入名称或平台...")
            
            filtered_apis = apis
            if search:
                filtered_apis = [
                    api for api in apis 
                    if search.lower() in api.get('name', '').lower() 
                    or search.lower() in api.get('platform', '').lower()
                ]
            
            # 显示API列表
            for i, api in enumerate(filtered_apis):
                with st.expander(
                    f"🔌 {api.get('name', 'N/A')} - {api.get('platform', 'N/A')}", 
                    expanded=False
                ):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**平台:** {api.get('platform', 'N/A')}")
                        st.markdown(f"**名称:** {api.get('name', 'N/A')}")
                        st.markdown(f"**端点:** `{api.get('url', 'N/A')}`")
                        
                        # 显示密钥（部分隐藏）
                        api_key = api.get('api_key', '')
                        if api_key:
                            masked_key = api_key[:8] + '*' * (len(api_key) - 12) + api_key[-4:] if len(api_key) > 12 else '****'
                            st.markdown(f"**密钥:** `{masked_key}`")
                        
                        if api.get('description'):
                            st.caption(f"说明: {api['description']}")
                        
                        if api.get('updated_at'):
                            st.caption(f"最后更新: {api['updated_at'][:19]}")
                    
                    with col2:
                        # 操作按钮
                        if st.button("✏️ 编辑", key=f"edit_{i}", use_container_width=True):
                            st.session_state[f'editing_{i}'] = True
                        
                        if st.button("🗑️ 删除", key=f"delete_{i}", use_container_width=True):
                            apis.remove(api)
                            save_apis(apis)
                            st.success(f"已删除 {api.get('name')}")
                            st.rerun()
                        
                        if st.button("🧪 测试", key=f"test_{i}", use_container_width=True):
                            st.info("测试功能待实现")
            
            # 显示统计信息
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总API数", len(apis))
            with col2:
                platforms = set(api.get('platform', '') for api in apis)
                st.metric("平台数", len(platforms))
            with col3:
                active_count = len([api for api in apis if api.get('status') == 'active'])
                st.metric("活跃API", active_count if active_count > 0 else len(apis))
    
    with tab2:
        st.markdown("### ➕ 添加新API配置")
        st.info("支持添加Amazon、TikTok、YouTube、OpenAI、Google等平台的第三方API")
        
        # API端点URL解释
        with st.expander("❓ 什么是API端点URL？", expanded=False):
            st.markdown("""
            ### 📖 API端点URL说明
            
            **API端点（API Endpoint）**是指API服务器上的一个特定URL地址，用于接收和处理API请求。
            
            #### 📝 基本结构
            ```
            https://api.example.com/v1/resource
            ├── https://          协议（通常是HTTPS）
            ├── api.example.com   API服务器域名
            ├── /v1/              API版本号
            └── /resource         具体的资源路径
            ```
            
            #### 💡 实际示例
            
            **OpenAI API:**
            - 端点: `https://api.openai.com/v1/chat/completions`
            - 用途: 调用ChatGPT进行对话
            
            **Google YouTube API:**
            - 端点: `https://www.googleapis.com/youtube/v3/search`
            - 用途: 搜索YouTube视频
            
            **Amazon Product API (第三方):**
            - 端点: `https://api.rainforestapi.com/request`
            - 用途: 获取Amazon产品数据
            
            #### 🎯 使用场景
            - 不同的端点对应不同的功能
            - 同一个API服务可能有多个端点
            - 每个端点都需要正确的认证（API密钥）
            
            #### ⚠️ 注意事项
            - API端点URL通常不能随意修改
            - 必须使用API提供商文档中指定的准确URL
            - 包含版本号（如/v1/、/v3/）的端点可能会随版本更新
            """)
        
        with st.form(key="api_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                platform = st.selectbox(
                    "平台类型",
                    [
                        "OpenAI", 
                        "Google (YouTube/Search)", 
                        "Amazon", 
                        "TikTok", 
                        "Shopee", 
                        "eBay", 
                        "其他"
                    ],
                    help="选择API所属平台"
                )
                
                name = st.text_input(
                    "API名称",
                    placeholder="例如：OpenAI GPT-4 API",
                    help="为API起一个易识别的名称"
                )
                
                url = st.text_input(
                    "API端点URL",
                    placeholder="https://api.openai.com/v1/chat/completions",
                    help="API的完整URL地址（端点）"
                )
                
                # 根据选择的平台显示提示信息
                if platform == "OpenAI":
                    st.info("💡 OpenAI常用端点: https://api.openai.com/v1/chat/completions")
                elif platform == "Google (YouTube/Search)":
                    st.info("💡 YouTube Data API: https://www.googleapis.com/youtube/v3/")
            
            with col2:
                api_key = st.text_input(
                    "API密钥",
                    type="password",
                    placeholder="sk-... (OpenAI) 或 AIza... (Google)",
                    help="从API提供商获取的密钥"
                )
                
                description = st.text_area(
                    "API描述（可选）",
                    placeholder="描述此API的用途和注意事项",
                    height=100
                )
                
                # 显示获取API密钥的链接
                st.markdown("**📚 如何获取API密钥:**")
                if platform == "OpenAI":
                    st.markdown("1. 访问 [OpenAI平台](https://platform.openai.com/)")
                    st.markdown("2. 注册并登录账号")
                    st.markdown("3. 进入 [API Keys 页面](https://platform.openai.com/api-keys)")
                    st.markdown("4. 点击 'Create new secret key'")
                    st.markdown("5. 复制密钥（只显示一次）")
                elif platform == "Google (YouTube/Search)":
                    st.markdown("1. 访问 [Google Cloud Console](https://console.cloud.google.com/)")
                    st.markdown("2. 创建新项目")
                    st.markdown("3. 启用所需API（YouTube Data API v3）")
                    st.markdown("4. 创建凭据 → API密钥")
                    st.markdown("5. 复制API密钥")
                elif platform == "Amazon":
                    st.markdown("**推荐第三方API服务:**")
                    st.markdown("- [Rainforest API](https://www.rainforestapi.com/)")
                    st.markdown("- [ScraperAPI](https://www.scraperapi.com/)")
                    st.markdown("- [RapidAPI Amazon](https://rapidapi.com/)")
                elif platform == "TikTok":
                    st.markdown("1. 访问 [TikTok开发者平台](https://developers.tiktok.com/)")
                    st.markdown("2. 注册开发者账号")
                    st.markdown("3. 创建应用")
                    st.markdown("4. 获取Client Key和Secret")
            
            # 高级选项
            with st.expander("⚙️ 高级选项"):
                col1, col2 = st.columns(2)
                
                with col1:
                    rate_limit = st.number_input(
                        "速率限制（每分钟）",
                        min_value=1,
                        max_value=10000,
                        value=60,
                        help="API调用频率限制"
                    )
                
                with col2:
                    timeout = st.number_input(
                        "超时时间（秒）",
                        min_value=1,
                        max_value=300,
                        value=30,
                        help="API请求超时时间"
                    )
                
                headers = st.text_area(
                    "自定义请求头（JSON格式）",
                    value='{\n  "Content-Type": "application/json"\n}',
                    height=100,
                    help="API请求的自定义HTTP头"
                )
            
            submitted = st.form_submit_button("💾 保存API配置", type="primary", use_container_width=True)

            if submitted:
                if not name or not url:
                    st.error("API名称和URL不能为空")
                else:
                    # 验证URL格式
                    if not url.startswith(('http://', 'https://')):
                        st.error("URL必须以http://或https://开头")
                    else:
                        new_api = {
                            "platform": platform,
                            "name": name,
                            "url": url,
                            "api_key": api_key,
                            "description": description,
                            "rate_limit": rate_limit,
                            "timeout": timeout,
                            "status": "active",
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat()
                        }
                        
                        # 尝试解析自定义头
                        try:
                            custom_headers = json.loads(headers)
                            new_api["headers"] = custom_headers
                        except json.JSONDecodeError:
                            st.warning("自定义请求头格式不正确，已跳过")
                        
                        apis.append(new_api)
                        save_apis(apis)
                        st.success(f"✅ API '{name}' 添加成功！")
                        st.balloons()
                        st.rerun()
    
    with tab3:
        st.markdown("### 📊 API使用统计")
        st.info("此功能将显示每个API的调用次数、成功率等统计信息")
        
        if not apis:
            st.warning("暂无API配置数据")
        else:
            # 按平台分组显示
            platforms = {}
            for api in apis:
                platform = api.get('platform', '其他')
                if platform not in platforms:
                    platforms[platform] = []
                platforms[platform].append(api)
            
            st.markdown("#### 平台分布")
            
            for platform, platform_apis in platforms.items():
                with st.expander(f"📊 {platform} ({len(platform_apis)} 个API)", expanded=True):
                    for api in platform_apis:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{api.get('name')}**")
                        
                        with col2:
                            # 这里应该显示实际的调用统计
                            st.caption("调用次数: N/A")
                        
                        with col3:
                            st.caption("成功率: N/A")
            
            # 导出配置
            st.markdown("---")
            if st.button("📥 导出所有API配置", use_container_width=True):
                config_json = json.dumps(apis, ensure_ascii=False, indent=2)
                st.download_button(
                    label="💾 下载JSON文件",
                    data=config_json,
                    file_name=f"api_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
