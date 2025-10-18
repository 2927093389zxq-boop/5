"""
WPS集成界面 - WPS在线文档连接和协作UI
WPS Integration UI - WPS online document connection and collaboration interface
"""

import streamlit as st
from core.wps_integration import WPSIntegration
from datetime import datetime
import os


def render_wps_integration():
    """渲染WPS集成界面"""
    st.header("📝 WPS Office 在线协作")
    st.markdown("连接WPS账号，实现在线文档编辑和团队协作")
    
    # 初始化WPS集成
    if 'wps_integration' not in st.session_state:
        st.session_state.wps_integration = WPSIntegration()
    
    wps = st.session_state.wps_integration
    
    # 检查登录状态
    user_info = wps.get_user_info()
    is_authenticated = user_info.get('success', False)
    
    if not is_authenticated:
        render_wps_login(wps)
    else:
        render_wps_workspace(wps, user_info)


def render_wps_login(wps: WPSIntegration):
    """渲染WPS登录界面"""
    st.markdown("### 🔐 连接WPS账号")
    
    # 检查是否配置了API凭证
    has_credentials = bool(wps.app_id and wps.app_secret)
    
    if has_credentials:
        st.success("✅ WPS API凭证已配置 (使用生产模式)")
    else:
        st.warning("⚠️ 未配置WPS API凭证，将使用演示模式")
        st.info("""
        **如需使用真实的WPS API：**
        1. 在 [WPS开放平台](https://open.wps.cn/) 注册并创建应用
        2. 设置环境变量：
           ```bash
           export WPS_APP_ID="your-app-id"
           export WPS_APP_SECRET="your-app-secret"
           ```
        3. 或在下方"API密钥配置"标签页中配置
        """)
    
    # 提供两种登录方式的说明
    tab1, tab2, tab3 = st.tabs(["账号密码登录", "OAuth授权", "API密钥配置"])
    
    with tab1:
        st.info("""
        **使用WPS账号登录**
        
        输入您的WPS账号和密码即可连接到WPS云端，实现：
        - 📄 创建和编辑在线文档
        - 📤 上传本地文件到云端
        - 👥 与团队成员协作
        - 🔗 生成分享链接
        
        注意：密码模式需要WPS API支持，如果不支持会自动使用演示模式。
        """)
        
        with st.form("wps_login_form"):
            username = st.text_input(
                "WPS账号/邮箱",
                placeholder="example@email.com",
                help="输入您的WPS账号或注册邮箱"
            )
            
            password = st.text_input(
                "密码",
                type="password",
                help="输入您的WPS账号密码"
            )
            
            remember = st.checkbox("记住登录状态", value=True)
            
            submitted = st.form_submit_button("🔑 登录WPS", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error("❌ 请输入账号和密码")
                else:
                    with st.spinner("正在连接WPS..."):
                        result = wps.authenticate(username=username, password=password)
                    
                    if result['success']:
                        mode = "演示模式" if result.get('demo_mode') else "生产模式"
                        st.success(f"✅ {result['message']} ({mode})")
                        if result.get('demo_mode'):
                            st.info("💡 当前使用演示模式。如需使用真实API，请配置WPS应用凭证。")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
    
    with tab2:
        st.info("""
        **OAuth 2.0 授权登录**
        
        推荐的安全登录方式，适用于生产环境：
        1. 点击下方"生成授权链接"按钮
        2. 在新窗口完成WPS账号授权
        3. 复制回调URL中的授权码
        4. 在下方输入授权码完成登录
        
        注意：需要先配置WPS应用凭证才能使用OAuth登录。
        """)
        
        if has_credentials:
            # 生成OAuth授权链接
            redirect_uri = st.text_input(
                "回调地址",
                value="http://localhost:8501",
                help="应用的OAuth回调地址"
            )
            
            if st.button("🔗 生成授权链接", use_container_width=True):
                auth_url = wps.get_auth_url(redirect_uri)
                if auth_url:
                    st.markdown(f"### [点击此处进行OAuth授权]({auth_url})")
                    st.code(auth_url, language=None)
                    st.info("👆 点击链接或复制到浏览器打开，完成授权后复制回调URL中的code参数")
                else:
                    st.error("生成授权链接失败")
            
            st.markdown("---")
            
            # OAuth授权码登录
            with st.form("oauth_login_form"):
                auth_code = st.text_input(
                    "授权码 (code)",
                    placeholder="从回调URL中复制的授权码",
                    help="完成OAuth授权后，从回调URL的code参数中获取"
                )
                
                callback_uri = st.text_input(
                    "回调地址 (需与上方一致)",
                    value=redirect_uri,
                    help="必须与授权链接中的redirect_uri一致"
                )
                
                submitted = st.form_submit_button("✅ 确认授权", use_container_width=True)
                
                if submitted:
                    if not auth_code:
                        st.error("❌ 请输入授权码")
                    else:
                        with st.spinner("正在验证授权..."):
                            result = wps.authenticate(code=auth_code, redirect_uri=callback_uri)
                        
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
        else:
            st.warning("⚠️ 请先配置WPS API凭证才能使用OAuth登录")
    
    with tab3:
        st.info("""
        **配置WPS开放平台API凭证**
        
        获取步骤：
        1. 访问 [WPS开放平台](https://open.wps.cn/)
        2. 注册并创建应用
        3. 获取 App ID 和 App Secret
        4. 在下方填入凭证信息
        
        推荐：使用环境变量存储凭证更安全
        ```bash
        export WPS_APP_ID="your-app-id"
        export WPS_APP_SECRET="your-app-secret"
        ```
        """)
        
        # 显示当前凭证状态
        if has_credentials:
            st.success(f"✅ App ID: {wps.app_id[:8]}... (已配置)")
            st.success("✅ App Secret: ******** (已配置)")
        
        with st.form("wps_api_config_form"):
            app_id = st.text_input(
                "WPS App ID",
                value=wps.app_id if not has_credentials else "",
                help="在WPS开放平台获取"
            )
            
            app_secret = st.text_input(
                "WPS App Secret",
                type="password",
                help="在WPS开放平台获取"
            )
            
            submitted = st.form_submit_button("💾 保存配置", use_container_width=True)
            
            if submitted:
                if app_id and app_secret:
                    result = wps.save_credentials(
                        username="api_user",
                        app_id=app_id,
                        app_secret=app_secret
                    )
                    st.success("✅ API配置已保存，请刷新页面重新登录")
                    st.info("💡 配置已保存到配置文件。建议使用环境变量以提高安全性。")
                else:
                    st.warning("请填写完整的API凭证")


def render_wps_workspace(wps: WPSIntegration, user_info: dict):
    """渲染WPS工作空间"""
    
    # 顶部用户信息和登出按钮
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        user = user_info.get('user', {})
        st.success(f"✅ 已连接WPS账号: **{user.get('username', 'N/A')}**")
    
    with col2:
        # 显示连接模式
        is_demo = wps.config.get('demo_mode', True)
        if is_demo:
            st.warning("🔧 演示模式")
        else:
            st.info("🚀 生产模式")
    
    with col3:
        if st.button("🚪 登出", use_container_width=True):
            result = wps.logout()
            if result['success']:
                st.success(result['message'])
                st.rerun()
    
    # 显示连接状态提示
    if wps.config.get('demo_mode', True):
        st.info("""
        💡 **当前使用演示模式**
        - 所有操作都是模拟的，不会真实调用WPS API
        - 数据仅保存在本地配置文件中
        - 如需使用真实API，请配置WPS应用凭证后重新登录
        """)
    else:
        st.success("""
        ✅ **已连接到WPS开放平台**
        - 所有操作将通过真实的WPS API执行
        - 文档和文件会保存到您的WPS云端账号
        - 支持与其他WPS用户实时协作
        """)
    
    st.markdown("---")
    
    # 获取协作统计
    collab_info = wps.get_collaboration_info()
    if collab_info['success']:
        stats = collab_info['stats']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("文档数", stats.get('total_documents', 0))
        
        with col2:
            st.metric("文件数", stats.get('total_files', 0))
        
        with col3:
            st.metric("分享数", stats.get('total_shares', 0))
    
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 我的文档", 
        "➕ 创建文档", 
        "📤 上传文件", 
        "👥 协作管理"
    ])
    
    with tab1:
        render_document_list(wps)
    
    with tab2:
        render_create_document(wps)
    
    with tab3:
        render_upload_file(wps)
    
    with tab4:
        render_collaboration(wps)


def render_document_list(wps: WPSIntegration):
    """渲染文档列表"""
    st.markdown("### 📄 我的文档")
    
    # 过滤选项
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search = st.text_input("🔍 搜索文档", placeholder="输入文档标题...")
    
    with col2:
        doc_type = st.selectbox("文档类型", ["全部", "doc", "sheet", "ppt"])
    
    # 获取文档列表
    filter_type = None if doc_type == "全部" else doc_type
    result = wps.list_documents(doc_type=filter_type)
    
    if result['success']:
        documents = result['documents']
        
        # 搜索过滤
        if search:
            documents = [d for d in documents if search.lower() in d.get('title', '').lower()]
        
        if not documents:
            st.info("暂无文档，请创建新文档")
        else:
            for doc in documents:
                with st.expander(
                    f"📝 {doc.get('title', 'N/A')} ({doc.get('type', 'doc')})",
                    expanded=False
                ):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**文档ID:** `{doc.get('doc_id', 'N/A')}`")
                        st.markdown(f"**类型:** {doc.get('type', 'N/A')}")
                        st.markdown(f"**创建者:** {doc.get('creator', 'N/A')}")
                        st.markdown(f"**创建时间:** {doc.get('created_at', 'N/A')[:19]}")
                        
                        # 显示链接
                        if doc.get('url'):
                            st.markdown(f"**查看链接:** [打开文档]({doc['url']})")
                        if doc.get('edit_url'):
                            st.markdown(f"**编辑链接:** [编辑文档]({doc['edit_url']})")
                    
                    with col2:
                        if st.button("📤 分享", key=f"share_{doc['doc_id']}", use_container_width=True):
                            st.session_state[f'sharing_{doc["doc_id"]}'] = True
                        
                        if st.button("📋 复制链接", key=f"copy_{doc['doc_id']}", use_container_width=True):
                            st.code(doc.get('url', ''), language=None)
                            st.success("链接已显示，请手动复制")
    else:
        st.error(result['message'])


def render_create_document(wps: WPSIntegration):
    """渲染创建文档界面"""
    st.markdown("### ➕ 创建新文档")
    st.info("在WPS云端创建新的在线文档，支持实时协作编辑")
    
    with st.form("create_document_form"):
        title = st.text_input(
            "文档标题",
            placeholder="例如: 项目计划书",
            help="为您的文档起一个有意义的标题"
        )
        
        doc_type = st.selectbox(
            "文档类型",
            ["doc", "sheet", "ppt"],
            format_func=lambda x: {
                "doc": "📄 文档 (Word)",
                "sheet": "📊 表格 (Excel)",
                "ppt": "📽️ 演示 (PowerPoint)"
            }[x]
        )
        
        content = st.text_area(
            "初始内容（可选）",
            placeholder="输入文档的初始内容...",
            height=200,
            help="为文档添加初始内容，创建后可在线编辑"
        )
        
        submitted = st.form_submit_button("✨ 创建文档", use_container_width=True)
        
        if submitted:
            if not title:
                st.error("❌ 请输入文档标题")
            else:
                with st.spinner("正在创建文档..."):
                    result = wps.create_document(
                        title=title,
                        content=content,
                        doc_type=doc_type
                    )
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    doc = result['document']
                    
                    # 显示文档信息
                    st.markdown("#### 文档已创建")
                    st.json(doc)
                    
                    # 显示打开链接
                    if doc.get('edit_url'):
                        st.markdown(f"### [🔗 点击打开文档]({doc['edit_url']})")
                    
                    st.balloons()
                else:
                    st.error(f"❌ {result['message']}")


def render_upload_file(wps: WPSIntegration):
    """渲染上传文件界面"""
    st.markdown("### 📤 上传文件到WPS云端")
    st.info("将本地文件上传到WPS云端，方便在线访问和协作")
    
    uploaded_file = st.file_uploader(
        "选择文件",
        type=["doc", "docx", "xls", "xlsx", "ppt", "pptx", "pdf", "txt"],
        help="支持Office文档、PDF等格式"
    )
    
    if uploaded_file:
        st.markdown("#### 文件信息")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**文件名:** {uploaded_file.name}")
            st.markdown(f"**文件大小:** {uploaded_file.size / 1024:.2f} KB")
        
        with col2:
            st.markdown(f"**文件类型:** {uploaded_file.type}")
        
        if st.button("🚀 开始上传", use_container_width=True):
            # 保存临时文件
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            
            try:
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                with st.spinner("正在上传文件..."):
                    result = wps.upload_file(temp_path)
                
                # 删除临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    file_info = result['file']
                    
                    # 显示文件信息
                    st.markdown("#### 文件已上传")
                    st.json(file_info)
                    
                    # 显示访问链接
                    if file_info.get('url'):
                        st.markdown(f"### [🔗 访问文件]({file_info['url']})")
                    
                    st.balloons()
                else:
                    st.error(f"❌ {result['message']}")
                    
            except Exception as e:
                st.error(f"❌ 上传失败: {str(e)}")


def render_collaboration(wps: WPSIntegration):
    """渲染协作管理界面"""
    st.markdown("### 👥 协作管理")
    st.info("分享文档给团队成员，设置协作权限")
    
    # 获取文档列表
    result = wps.list_documents()
    
    if result['success'] and result['documents']:
        documents = result['documents']
        doc_titles = {f"{d['title']} ({d['doc_id'][:8]})": d['doc_id'] for d in documents}
        
        with st.form("share_document_form"):
            selected_doc = st.selectbox(
                "选择要分享的文档",
                list(doc_titles.keys())
            )
            
            users_input = st.text_area(
                "协作用户",
                placeholder="输入用户邮箱，每行一个\nuser1@email.com\nuser2@email.com",
                help="输入要分享给的用户邮箱地址"
            )
            
            permission = st.selectbox(
                "权限设置",
                ["view", "edit", "admin"],
                format_func=lambda x: {
                    "view": "👁️ 查看 - 只能查看文档",
                    "edit": "✏️ 编辑 - 可以编辑文档",
                    "admin": "👑 管理 - 完全控制权限"
                }[x]
            )
            
            submitted = st.form_submit_button("📤 分享文档", use_container_width=True)
            
            if submitted:
                if not users_input.strip():
                    st.error("❌ 请输入至少一个用户邮箱")
                else:
                    # 解析用户列表
                    users = [u.strip() for u in users_input.split('\n') if u.strip()]
                    doc_id = doc_titles[selected_doc]
                    
                    with st.spinner("正在分享文档..."):
                        result = wps.share_document(
                            doc_id=doc_id,
                            users=users,
                            permission=permission
                        )
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        share_info = result['share']
                        
                        # 显示分享信息
                        st.markdown("#### 分享成功")
                        st.json(share_info)
                        
                        # 显示分享链接
                        if share_info.get('share_link'):
                            st.markdown(f"**分享链接:** {share_info['share_link']}")
                            st.code(share_info['share_link'], language=None)
                        
                        st.balloons()
                    else:
                        st.error(f"❌ {result['message']}")
    else:
        st.warning("暂无文档可分享，请先创建文档")
    
    st.markdown("---")
    
    # 显示已分享的文档
    st.markdown("#### 📋 分享历史")
    
    config = wps.config
    shares = config.get('shares', [])
    
    if shares:
        for i, share in enumerate(reversed(shares[-10:])):  # 显示最近10条
            with st.expander(
                f"分享 #{len(shares) - i} - {share.get('shared_at', 'N/A')[:19]}",
                expanded=False
            ):
                st.markdown(f"**文档ID:** `{share.get('doc_id', 'N/A')}`")
                st.markdown(f"**权限:** {share.get('permission', 'N/A')}")
                st.markdown(f"**分享给:** {', '.join(share.get('users', []))}")
                if share.get('share_link'):
                    st.markdown(f"**分享链接:** [{share['share_link']}]({share['share_link']})")
    else:
        st.info("暂无分享记录")
