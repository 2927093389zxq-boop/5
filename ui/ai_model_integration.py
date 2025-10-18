"""
AI模型管理界面 - 集成到API管理模块
AI Model Management UI - Integrated into API management module
"""

import streamlit as st
from core.ai_model_manager import AIModelManager
import json


def render_ai_model_integration():
    """渲染AI模型集成界面（作为API管理的一个标签页）"""
    st.markdown("### 🤖 AI模型接入管理")
    st.info("统一管理多个AI模型提供商的接入，支持OpenAI、Claude、Gemini等主流AI模型")
    
    # 初始化AI模型管理器
    if 'ai_model_manager' not in st.session_state:
        st.session_state.ai_model_manager = AIModelManager()
    
    manager = st.session_state.ai_model_manager
    
    # 创建子标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 已配置模型",
        "➕ 添加模型",
        "📚 支持的提供商",
        "🧪 测试模型"
    ])
    
    with tab1:
        render_configured_models(manager)
    
    with tab2:
        render_add_model(manager)
    
    with tab3:
        render_providers_info(manager)
    
    with tab4:
        render_test_model(manager)


def render_configured_models(manager: AIModelManager):
    """渲染已配置的AI模型列表"""
    st.markdown("#### 📋 已配置的AI模型")
    
    models = manager.list_models()
    
    if not models:
        st.info("暂无配置的AI模型，请在'添加模型'标签页中添加")
        return
    
    # 统计信息
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总模型数", len(models))
    
    with col2:
        enabled = len([m for m in models if m.get('enabled', True)])
        st.metric("已启用", enabled)
    
    with col3:
        providers = len(set([m['provider'] for m in models]))
        st.metric("提供商数", providers)
    
    st.markdown("---")
    
    # 过滤选项
    col1, col2 = st.columns(2)
    
    with col1:
        search = st.text_input("🔍 搜索模型", placeholder="输入模型名称或提供商...")
    
    with col2:
        all_providers = list(set([m.get('provider_name', m['provider']) for m in models]))
        provider_filter = st.selectbox("提供商筛选", ["全部"] + all_providers)
    
    # 应用过滤
    filtered_models = models
    
    if provider_filter != "全部":
        filtered_models = [
            m for m in filtered_models 
            if m.get('provider_name', m['provider']) == provider_filter
        ]
    
    if search:
        filtered_models = [
            m for m in filtered_models
            if search.lower() in m.get('model_name', '').lower()
            or search.lower() in m.get('provider_name', '').lower()
        ]
    
    # 显示模型列表
    for model in filtered_models:
        with st.expander(
            f"🤖 {model.get('provider_name', 'N/A')} - {model.get('model_name', 'N/A')}",
            expanded=False
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**提供商:** {model.get('provider_name', 'N/A')}")
                st.markdown(f"**模型名称:** {model.get('model_name', 'N/A')}")
                st.markdown(f"**API端点:** `{model.get('api_base', 'N/A')}`")
                
                # 显示密钥（部分隐藏）
                api_key = model.get('api_key', '')
                if api_key:
                    if len(api_key) > 12:
                        masked = api_key[:8] + '*' * (len(api_key) - 12) + api_key[-4:]
                    else:
                        masked = '****'
                    st.markdown(f"**API密钥:** `{masked}`")
                
                status = "✅ 已启用" if model.get('enabled', True) else "❌ 已禁用"
                st.markdown(f"**状态:** {status}")
                
                st.caption(f"创建时间: {model.get('created_at', 'N/A')[:19]}")
                st.caption(f"更新时间: {model.get('updated_at', 'N/A')[:19]}")
            
            with col2:
                # 操作按钮
                if model.get('enabled', True):
                    if st.button("🚫 禁用", key=f"disable_{model['id']}", use_container_width=True):
                        result = manager.update_model(model['id'], enabled=False)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                else:
                    if st.button("✅ 启用", key=f"enable_{model['id']}", use_container_width=True):
                        result = manager.update_model(model['id'], enabled=True)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                
                if st.button("🧪 测试", key=f"test_{model['id']}", use_container_width=True):
                    with st.spinner("测试中..."):
                        result = manager.test_model(model['id'])
                    if result['success']:
                        st.success(result['message'])
                    else:
                        st.error(result['message'])
                
                if st.button("🗑️ 删除", key=f"delete_{model['id']}", use_container_width=True):
                    result = manager.delete_model(model['id'])
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()


def render_add_model(manager: AIModelManager):
    """渲染添加AI模型界面"""
    st.markdown("#### ➕ 添加新AI模型")
    st.info("配置新的AI模型接入，支持多种主流AI提供商")
    
    with st.form("add_ai_model_form"):
        # 选择提供商
        providers = manager.list_providers()
        provider_options = {p['name']: p['id'] for p in providers}
        
        selected_provider_name = st.selectbox(
            "选择AI提供商",
            list(provider_options.keys()),
            help="选择AI服务提供商"
        )
        
        selected_provider = provider_options[selected_provider_name]
        provider_info = manager.get_provider_info(selected_provider)
        
        # 显示提供商信息
        with st.expander("📖 查看提供商信息", expanded=False):
            st.markdown(f"**提供商:** {provider_info['name']}")
            st.markdown(f"**API基础URL:** `{provider_info['api_base']}`")
            st.markdown(f"**支持的模型:** {', '.join(provider_info['models'])}")
            
            # 显示端点信息
            st.markdown("**API端点:**")
            for endpoint_name, endpoint_path in provider_info['endpoints'].items():
                st.code(f"{endpoint_name}: {endpoint_path}", language=None)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 选择模型
            if provider_info['models'] == ['custom']:
                model_name = st.text_input(
                    "模型名称",
                    placeholder="输入自定义模型名称",
                    help="例如: meta-llama/Llama-2-7b-chat-hf"
                )
            else:
                model_name = st.selectbox(
                    "选择模型",
                    provider_info['models'],
                    help="选择要使用的模型"
                )
            
            api_key = st.text_input(
                "API密钥",
                type="password",
                help="从AI提供商获取的API密钥"
            )
        
        with col2:
            # 自定义端点（可选）
            custom_endpoint = st.text_input(
                "自定义API端点（可选）",
                value=provider_info['api_base'],
                help="如果需要使用自定义端点，请在此填写"
            )
            
            # 显示获取API密钥的指南
            with st.expander("📚 如何获取API密钥？"):
                if selected_provider == 'openai':
                    st.markdown("""
                    **OpenAI API密钥获取步骤:**
                    1. 访问 [OpenAI平台](https://platform.openai.com/)
                    2. 注册并登录账号
                    3. 进入 [API Keys](https://platform.openai.com/api-keys)
                    4. 点击 "Create new secret key"
                    5. 复制生成的密钥（只显示一次）
                    """)
                elif selected_provider == 'anthropic':
                    st.markdown("""
                    **Anthropic API密钥获取步骤:**
                    1. 访问 [Anthropic Console](https://console.anthropic.com/)
                    2. 注册账号
                    3. 进入 API Keys 页面
                    4. 创建新的API密钥
                    5. 复制密钥
                    """)
                elif selected_provider == 'google':
                    st.markdown("""
                    **Google AI API密钥获取步骤:**
                    1. 访问 [Google AI Studio](https://makersuite.google.com/)
                    2. 登录Google账号
                    3. 点击 "Get API key"
                    4. 创建或选择项目
                    5. 复制API密钥
                    """)
                elif selected_provider == 'cohere':
                    st.markdown("""
                    **Cohere API密钥获取步骤:**
                    1. 访问 [Cohere Dashboard](https://dashboard.cohere.ai/)
                    2. 注册账号
                    3. 进入API Keys页面
                    4. 复制Production或Trial密钥
                    """)
                elif selected_provider == 'huggingface':
                    st.markdown("""
                    **HuggingFace API密钥获取步骤:**
                    1. 访问 [HuggingFace](https://huggingface.co/)
                    2. 注册并登录
                    3. 进入 Settings → Access Tokens
                    4. 创建新的token
                    5. 复制token
                    """)
                elif selected_provider in ['deepseek', 'moonshot', 'zhipu', 'baidu']:
                    st.markdown(f"""
                    **{provider_info['name']} API密钥获取:**
                    请访问官方网站注册账号并获取API密钥。
                    """)
        
        # 高级选项
        with st.expander("⚙️ 高级选项"):
            col1, col2 = st.columns(2)
            
            with col1:
                max_tokens = st.number_input(
                    "最大Token数",
                    min_value=1,
                    max_value=100000,
                    value=2000,
                    help="单次请求的最大token数"
                )
            
            with col2:
                temperature = st.slider(
                    "温度参数",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.7,
                    step=0.1,
                    help="控制输出的随机性，越高越随机"
                )
            
            description = st.text_area(
                "备注说明",
                placeholder="添加关于此模型配置的说明...",
                height=80
            )
        
        submitted = st.form_submit_button("💾 保存配置", use_container_width=True)
        
        if submitted:
            if not model_name or not api_key:
                st.error("❌ 请填写模型名称和API密钥")
            else:
                result = manager.add_model(
                    provider=selected_provider,
                    model_name=model_name,
                    api_key=api_key,
                    custom_endpoint=custom_endpoint if custom_endpoint != provider_info['api_base'] else None,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    description=description
                )
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")


def render_providers_info(manager: AIModelManager):
    """渲染支持的提供商信息"""
    st.markdown("#### 📚 支持的AI提供商")
    st.info("以下是系统支持的所有AI模型提供商及其详细信息")
    
    providers = manager.list_providers()
    
    for provider in providers:
        with st.expander(
            f"🤖 {provider['name']}",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**提供商ID:** `{provider['id']}`")
                st.markdown(f"**API基础URL:** `{provider['api_base']}`")
                
                st.markdown("**支持的模型:**")
                for model in provider['models']:
                    st.markdown(f"- {model}")
            
            with col2:
                # 提供商特色说明
                if provider['id'] == 'openai':
                    st.markdown("""
                    **特色:**
                    - 业界领先的GPT系列模型
                    - 支持聊天、补全、嵌入等多种功能
                    - 强大的自然语言理解能力
                    """)
                elif provider['id'] == 'anthropic':
                    st.markdown("""
                    **特色:**
                    - Claude系列模型，注重安全性
                    - 支持长上下文（100K+ tokens）
                    - 优秀的代码理解能力
                    """)
                elif provider['id'] == 'google':
                    st.markdown("""
                    **特色:**
                    - Gemini系列多模态模型
                    - 支持文本和图像输入
                    - 与Google生态系统集成
                    """)
                elif provider['id'] == 'cohere':
                    st.markdown("""
                    **特色:**
                    - 企业级NLP解决方案
                    - 支持多语言
                    - 优化的嵌入模型
                    """)
                elif provider['id'] == 'huggingface':
                    st.markdown("""
                    **特色:**
                    - 开源模型托管平台
                    - 支持大量社区模型
                    - 灵活的自定义能力
                    """)


def render_test_model(manager: AIModelManager):
    """渲染测试AI模型界面"""
    st.markdown("#### 🧪 测试AI模型")
    st.info("测试已配置的AI模型是否正常工作")
    
    models = manager.list_models(enabled_only=True)
    
    if not models:
        st.warning("暂无已启用的AI模型，请先添加并启用模型")
        return
    
    # 选择要测试的模型
    model_options = {
        f"{m.get('provider_name', 'N/A')} - {m.get('model_name', 'N/A')}": m['id']
        for m in models
    }
    
    selected_model_name = st.selectbox(
        "选择要测试的模型",
        list(model_options.keys())
    )
    
    selected_model_id = model_options[selected_model_name]
    model = manager.get_model(selected_model_id)
    
    if model:
        st.markdown(f"#### 测试模型: {selected_model_name}")
        
        # 显示模型信息
        with st.expander("模型配置信息", expanded=False):
            st.json({
                'provider': model.get('provider_name', 'N/A'),
                'model': model.get('model_name', 'N/A'),
                'api_base': model.get('api_base', 'N/A'),
                'created_at': model.get('created_at', 'N/A')
            })
        
        # 测试提示词
        test_prompt = st.text_area(
            "测试提示词",
            value="你好，请用一句话介绍你自己。",
            height=100,
            help="输入要发送给AI模型的测试提示词"
        )
        
        if st.button("🚀 开始测试", use_container_width=True):
            with st.spinner(f"正在测试模型 {selected_model_name}..."):
                result = manager.test_model(selected_model_id, test_prompt)
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                
                # 显示响应
                if 'response' in result:
                    st.markdown("#### 🎯 模型响应")
                    st.json(result['response'])
            else:
                st.error(f"❌ {result['message']}")
                if 'error' in result:
                    with st.expander("查看详细错误信息"):
                        st.code(result['error'])
