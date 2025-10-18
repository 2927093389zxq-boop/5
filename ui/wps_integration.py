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
    
    # 检查URL参数中是否有授权码
    query_params = st.query_params
    if 'code' in query_params:
        handle_oauth_callback(wps, query_params['code'][0])
    
    # 提供三种登录方式
    tab1, tab2, tab3 = st.tabs(["账号密码登录", "OAuth认证", "API密钥配置"])
    
    with tab1:
        st.info("""
        **使用WPS账号登录**
        
        输入您的WPS账号和密码即可连接到WPS云端，实现：
        - 📄 创建和编辑在线文档
        - 📤 上传本地文件到云端
        - 👥 与团队成员协作
        - 🔗 生成分享链接
        
        注意：这是演示登录方式，生产环境推荐使用OAuth认证。
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
                        result = wps.authenticate(username, password)
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        if 'warning' in result:
                            st.warning(result['warning'])
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
    
    with tab2:
        st.info("""
        **OAuth认证（推荐用于生产环境）**
        
        安全的OAuth2.0认证流程：
        1. 点击下方按钮跳转到WPS授权页面
        2. 在WPS页面登录并授权
        3. 授权成功后自动返回此应用
        4. 系统自动完成认证过程
        
        优势：
        - 🔒 更安全，无需在应用中存储密码
        - 📋 符合OAuth2.0标准
        - 🔄 支持令牌自动刷新
        """)
        
        # 获取当前配置的应用信息
        config = wps.config
        app_id = config.get('app_id', '')
        
        if not app_id:
            st.warning("⚠️ 请先在'API密钥配置'标签页中设置App ID和App Secret")
            if st.button("前往配置API密钥", use_container_width=True):
                # 这里无法直接切换标签，但可以给用户提示
                st.info("请点击上方的'API密钥配置'标签进行设置")
        else:
            # 生成OAuth认证URL
            # 使用当前Streamlit应用的URL作为回调地址
            redirect_uri = f"http://localhost:8505"
            auth_url = wps.get_auth_url(redirect_uri)
            
            if auth_url:
                st.markdown(f"### [🚀 开始OAuth认证]({auth_url})")
                st.markdown("---")
                st.info("点击上方按钮后，会跳转到WPS授权页面，请在那里完成登录和授权操作。")
            else:
                st.error("无法生成OAuth认证链接，请检查API配置")
    
    with tab3:
        st.info("""
        **使用WPS开放平台API**
        
        配置WPS开放平台的应用凭证：
        1. 访问 [WPS开放平台](https://open.wps.cn/)
        2. 注册并创建应用
        3. 设置回调地址为：`http://localhost:8505`
        4. 获取 AppID 和 AppSecret
        5. 在下方填入凭证信息
        """)
        
        with st.form("wps_api_config_form"):
            app_id = st.text_input(
                "WPS App ID",
                value=wps.config.get('app_id', ''),
                help="在WPS开放平台获取"
            )
            
            app_secret = st.text_input(
                "WPS App Secret",
                value=wps.config.get('app_secret', ''),
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
                    st.success("✅ API配置已保存")
                    st.info("请切换到'OAuth认证'标签页完成授权")
                else:
                    st.warning("请填写完整的API凭证")
                    

def handle_oauth_callback(wps: WPSIntegration, code: str):
    """
    处理OAuth认证回调
    
    Args:
        wps: WPSIntegration实例
        code: 授权码
    """
    st.markdown("---")
    st.subheader("🔄 正在处理OAuth认证...")
    
    with st.spinner("正在获取访问令牌..."):
        # 使用与请求授权时相同的回调地址
        redirect_uri = f"http://localhost:8505"
        result = wps.get_token(code, redirect_uri)
    
    if result['success']:
        st.success("✅ OAuth认证成功！")
        st.info(f"已获取访问令牌，有效期2小时")
        
        # 清除URL中的授权码，避免重复处理
        st.query_params.clear()
        
        # 延迟后刷新页面
        import time
        time.sleep(1)
        st.rerun()
    else:
        st.error(f"❌ OAuth认证失败: {result['message']}")
        st.info("请重新尝试OAuth认证流程")
        
        # 清除URL中的授权码
        st.query_params.clear()


def render_wps_workspace(wps: WPSIntegration, user_info: dict):
    """渲染WPS工作空间"""
    
    # 检查令牌有效性
    token_valid = wps.check_token_validity()
    if not token_valid:
        st.error("❌ 访问令牌已失效，请重新登录")
        if st.button("🔄 重新登录", use_container_width=True):
            result = wps.logout()
            st.rerun()
        return
    
    # 顶部用户信息和登出按钮
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user = user_info.get('user', {})
        st.success(f"✅ 已连接WPS账号: **{user.get('username', 'N/A')}**")
        
        # 显示令牌状态信息
        config = wps.config
        if 'token_expires_at' in config:
            expires_at = config['token_expires_at']
            now = datetime.now().timestamp()
            remaining_time = expires_at - now
            
            if remaining_time > 0:
                hours, remainder = divmod(remaining_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                st.info(f"🔐 访问令牌有效期还剩: {int(hours)}小时{int(minutes)}分钟")
            else:
                st.warning("⚠️ 访问令牌已过期，正在尝试刷新...")
                wps.check_token_validity()
    
    with col2:
        if st.button("🚪 登出", use_container_width=True):
            result = wps.logout()
            if result['success']:
                st.success(result['message'])
                st.rerun()
    
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
