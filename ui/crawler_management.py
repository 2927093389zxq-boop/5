"""
爬虫管理界面 - 集中管理所有爬虫代码的UI
Crawler Management UI - Centralized UI for managing all crawler code
"""

import streamlit as st
from core.crawler_manager import CrawlerManager
from datetime import datetime
import json


def render_crawler_management():
    """渲染爬虫管理界面"""
    st.header("🕷️ 爬虫代码管理中心")
    st.markdown("集中管理所有爬虫代码，支持便捷添加、编辑和切换爬虫")
    
    # 初始化爬虫管理器
    if 'crawler_manager' not in st.session_state:
        st.session_state.crawler_manager = CrawlerManager()
    
    manager = st.session_state.crawler_manager
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["📋 爬虫列表", "➕ 添加爬虫", "🔧 编辑爬虫", "▶️ 执行爬虫"])
    
    with tab1:
        render_crawler_list(manager)
    
    with tab2:
        render_add_crawler(manager)
    
    with tab3:
        render_edit_crawler(manager)
    
    with tab4:
        render_execute_crawler(manager)


def render_crawler_list(manager: CrawlerManager):
    """渲染爬虫列表"""
    st.markdown("### 📋 已保存的爬虫")
    
    # 过滤选项
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("🔍 搜索爬虫", placeholder="输入名称或平台...")
    
    with col2:
        platform_filter = st.selectbox(
            "平台筛选",
            ["全部"] + list(set([c.get('platform', 'custom') for c in manager.list_crawlers()]))
        )
    
    with col3:
        status_filter = st.selectbox("状态筛选", ["全部", "已启用", "已禁用"])
    
    # 获取爬虫列表
    crawlers = manager.list_crawlers()
    
    # 应用过滤
    if platform_filter != "全部":
        crawlers = [c for c in crawlers if c.get('platform') == platform_filter]
    
    if status_filter == "已启用":
        crawlers = [c for c in crawlers if c.get('enabled', True)]
    elif status_filter == "已禁用":
        crawlers = [c for c in crawlers if not c.get('enabled', True)]
    
    if search:
        crawlers = [
            c for c in crawlers
            if search.lower() in c.get('name', '').lower()
            or search.lower() in c.get('platform', '').lower()
        ]
    
    st.markdown("---")
    
    if not crawlers:
        st.info("暂无爬虫，请在'添加爬虫'标签页中添加")
    else:
        # 显示统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总数", len(manager.list_crawlers()))
        with col2:
            enabled_count = len([c for c in manager.list_crawlers() if c.get('enabled', True)])
            st.metric("已启用", enabled_count)
        with col3:
            platforms_count = len(set([c.get('platform', 'custom') for c in manager.list_crawlers()]))
            st.metric("平台数", platforms_count)
        
        st.markdown("---")
        
        # 显示爬虫列表
        for crawler in crawlers:
            with st.expander(
                f"🕷️ {crawler.get('name', 'N/A')} - {crawler.get('platform', 'custom')}", 
                expanded=False
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**名称:** {crawler.get('name', 'N/A')}")
                    st.markdown(f"**平台:** {crawler.get('platform', 'custom')}")
                    st.markdown(f"**描述:** {crawler.get('description', '无描述')}")
                    
                    status = "✅ 已启用" if crawler.get('enabled', True) else "❌ 已禁用"
                    st.markdown(f"**状态:** {status}")
                    
                    created = crawler.get('created_at', 'N/A')[:19]
                    updated = crawler.get('updated_at', 'N/A')[:19]
                    st.caption(f"创建时间: {created}")
                    st.caption(f"更新时间: {updated}")
                
                with col2:
                    # 操作按钮
                    if st.button("👁️ 查看代码", key=f"view_{crawler['name']}", use_container_width=True):
                        st.session_state[f'viewing_code_{crawler["name"]}'] = True
                    
                    if crawler.get('enabled', True):
                        if st.button("🚫 禁用", key=f"disable_{crawler['name']}", use_container_width=True):
                            result = manager.update_crawler(crawler['name'], enabled=False)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                    else:
                        if st.button("✅ 启用", key=f"enable_{crawler['name']}", use_container_width=True):
                            result = manager.update_crawler(crawler['name'], enabled=True)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                    
                    if st.button("🗑️ 删除", key=f"delete_{crawler['name']}", use_container_width=True):
                        result = manager.delete_crawler(crawler['name'])
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
                
                # 显示代码（如果用户点击了查看按钮）
                if st.session_state.get(f'viewing_code_{crawler["name"]}', False):
                    code = manager.get_crawler_code(crawler['name'])
                    if code:
                        st.code(code, language='python')
                        if st.button("关闭代码", key=f"close_code_{crawler['name']}"):
                            st.session_state[f'viewing_code_{crawler["name"]}'] = False
                            st.rerun()


def render_add_crawler(manager: CrawlerManager):
    """渲染添加爬虫界面"""
    st.markdown("### ➕ 添加新爬虫")
    st.info("💡 提示: 粘贴您的爬虫代码，系统会自动验证并保存。代码中需要包含 `scrape()`, `run()` 或 `main()` 函数。")
    
    with st.form("add_crawler_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "爬虫名称 *", 
                placeholder="例如: my_amazon_crawler",
                help="使用英文和下划线，不要包含空格或特殊字符"
            )
        
        with col2:
            platform = st.selectbox(
                "平台类型",
                ["custom", "amazon", "ebay", "shopee", "aliexpress", 
                 "tiktok", "youtube", "other"]
            )
        
        description = st.text_area(
            "爬虫描述",
            placeholder="简要描述这个爬虫的功能...",
            height=80
        )
        
        st.markdown("#### 爬虫代码")
        st.caption("请粘贴完整的Python代码。确保代码中包含 `scrape()`, `run()` 或 `main()` 函数作为入口点。")
        
        code = st.text_area(
            "Python代码 *",
            placeholder="""# 示例爬虫代码
import requests
from bs4 import BeautifulSoup

def scrape(url, **kwargs):
    '''主要爬取函数'''
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 你的爬取逻辑
    data = []
    
    return {
        'success': True,
        'data': data,
        'count': len(data)
    }
""",
            height=400,
            help="代码必须是有效的Python代码"
        )
        
        # 提供示例代码
        with st.expander("📖 查看示例代码模板"):
            st.code("""# 基础爬虫模板
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape(url, max_items=10, **kwargs):
    '''
    主要爬取函数
    
    参数:
        url: 要爬取的URL
        max_items: 最大项目数
        **kwargs: 其他参数
        
    返回:
        包含爬取结果的字典
    '''
    try:
        # 发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 提取数据 (根据实际网站结构修改)
        items = []
        for item in soup.select('.item-selector')[:max_items]:
            title = item.select_one('.title')
            price = item.select_one('.price')
            
            items.append({
                'title': title.text.strip() if title else '',
                'price': price.text.strip() if price else '',
                'scraped_at': datetime.now().isoformat()
            })
        
        return {
            'success': True,
            'data': items,
            'count': len(items),
            'url': url
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': []
        }
""", language='python')
        
        submitted = st.form_submit_button("💾 保存爬虫", use_container_width=True)
        
        if submitted:
            if not name or not code:
                st.error("❌ 请填写爬虫名称和代码")
            elif ' ' in name or not name.replace('_', '').isalnum():
                st.error("❌ 爬虫名称只能包含字母、数字和下划线")
            else:
                # 检查名称是否已存在
                if manager.get_crawler(name):
                    st.error(f"❌ 爬虫名称 '{name}' 已存在，请使用其他名称")
                else:
                    result = manager.add_crawler(
                        name=name,
                        code=code,
                        description=description,
                        platform=platform
                    )
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.balloons()
                        # 清空表单（通过重新加载）
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                        if 'error' in result:
                            st.code(result['error'])


def render_edit_crawler(manager: CrawlerManager):
    """渲染编辑爬虫界面"""
    st.markdown("### 🔧 编辑爬虫")
    
    crawlers = manager.list_crawlers()
    
    if not crawlers:
        st.info("暂无爬虫可编辑，请先添加爬虫")
        return
    
    # 选择要编辑的爬虫
    crawler_names = [c['name'] for c in crawlers]
    selected_name = st.selectbox("选择要编辑的爬虫", crawler_names)
    
    if selected_name:
        crawler = manager.get_crawler(selected_name)
        current_code = manager.get_crawler_code(selected_name)
        
        if crawler and current_code:
            with st.form("edit_crawler_form"):
                st.markdown(f"#### 编辑爬虫: {selected_name}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    platform = st.selectbox(
                        "平台类型",
                        ["custom", "amazon", "ebay", "shopee", "aliexpress", 
                         "tiktok", "youtube", "other"],
                        index=["custom", "amazon", "ebay", "shopee", "aliexpress", 
                               "tiktok", "youtube", "other"].index(crawler.get('platform', 'custom'))
                    )
                
                with col2:
                    enabled = st.checkbox("启用爬虫", value=crawler.get('enabled', True))
                
                description = st.text_area(
                    "爬虫描述",
                    value=crawler.get('description', ''),
                    height=80
                )
                
                st.markdown("#### 爬虫代码")
                code = st.text_area(
                    "Python代码",
                    value=current_code,
                    height=400
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    submitted = st.form_submit_button("💾 保存更新", use_container_width=True)
                
                with col2:
                    if st.form_submit_button("🔄 重置", use_container_width=True):
                        st.rerun()
                
                if submitted:
                    result = manager.update_crawler(
                        name=selected_name,
                        code=code,
                        description=description,
                        enabled=enabled
                    )
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                        if 'error' in result:
                            st.code(result['error'])


def render_execute_crawler(manager: CrawlerManager):
    """渲染执行爬虫界面"""
    st.markdown("### ▶️ 执行爬虫")
    st.info("选择一个爬虫并配置参数来运行")
    
    crawlers = manager.list_crawlers(enabled_only=True)
    
    if not crawlers:
        st.warning("暂无已启用的爬虫，请先添加并启用爬虫")
        return
    
    # 选择爬虫
    crawler_names = [c['name'] for c in crawlers]
    selected_name = st.selectbox("选择要执行的爬虫", crawler_names)
    
    if selected_name:
        crawler = manager.get_crawler(selected_name)
        
        st.markdown(f"#### 执行爬虫: {selected_name}")
        st.caption(f"平台: {crawler.get('platform', 'custom')} | 描述: {crawler.get('description', '无')}")
        
        with st.form("execute_crawler_form"):
            st.markdown("##### 配置参数")
            
            url = st.text_input(
                "目标URL",
                placeholder="https://example.com",
                help="要爬取的网页地址"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                max_items = st.number_input("最大项目数", min_value=1, max_value=1000, value=10)
            
            with col2:
                timeout = st.number_input("超时时间(秒)", min_value=5, max_value=300, value=30)
            
            # 额外参数
            with st.expander("高级参数 (JSON格式)"):
                extra_params = st.text_area(
                    "额外参数",
                    value='{}',
                    help="以JSON格式提供额外参数，例如: {\"headers\": {\"Authorization\": \"Bearer token\"}}"
                )
            
            submitted = st.form_submit_button("🚀 开始执行", use_container_width=True)
            
            if submitted:
                if not url:
                    st.error("❌ 请输入目标URL")
                else:
                    # 解析额外参数
                    try:
                        extra = json.loads(extra_params)
                    except:
                        extra = {}
                    
                    # 执行爬虫
                    with st.spinner(f"正在执行爬虫 {selected_name}..."):
                        result = manager.execute_crawler(
                            selected_name,
                            url=url,
                            max_items=max_items,
                            timeout=timeout,
                            **extra
                        )
                    
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                        
                        # 显示结果
                        if 'result' in result:
                            st.markdown("#### 执行结果")
                            
                            # 尝试以友好的方式显示结果
                            crawler_result = result['result']
                            
                            if isinstance(crawler_result, dict):
                                # 显示统计信息
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if 'count' in crawler_result:
                                        st.metric("获取项目数", crawler_result['count'])
                                
                                with col2:
                                    if 'success' in crawler_result:
                                        status = "✅ 成功" if crawler_result['success'] else "❌ 失败"
                                        st.metric("状态", status)
                                
                                with col3:
                                    if 'data' in crawler_result and isinstance(crawler_result['data'], list):
                                        st.metric("数据行数", len(crawler_result['data']))
                                
                                # 显示详细数据
                                with st.expander("查看详细数据", expanded=True):
                                    st.json(crawler_result)
                                
                                # 提供下载选项
                                if 'data' in crawler_result:
                                    json_str = json.dumps(crawler_result['data'], 
                                                        ensure_ascii=False, indent=2)
                                    st.download_button(
                                        label="📥 下载结果(JSON)",
                                        data=json_str,
                                        file_name=f"{selected_name}_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                            else:
                                # 直接显示结果
                                st.json(crawler_result)
                    else:
                        st.error(f"❌ {result['message']}")
                        if 'error' in result:
                            st.code(result['error'])
