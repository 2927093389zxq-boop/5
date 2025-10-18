import streamlit as st
import pandas as pd
from datetime import datetime

# 导入我们新创建的核心数据获取函数和平台列表
from core.data_fetcher import get_platform_data, PLATFORM_LIST

def render_dashboard():
    """
    渲染全新的、可交互的主仪表盘页面。
    """
    st.header("📊 动态数据总览")

    # 1. 保留顶部的实时信息
    col1, col2, col3 = st.columns(3)
    col1.metric("当前时间", datetime.now().strftime("%H:%M:%S"))
    col2.metric("联网状态", "在线 ✅")
    col3.metric("数据源数量", f"{len(PLATFORM_LIST)} 个")

    st.markdown("---") # 添加一条分割线

    # 2. 创建交互式数据看板
    st.markdown("### 🔥 跨平台热门产品看板")
    st.caption("选择一个平台，然后点击按钮来获取最新的公开热门商品数据。")

    # 创建一个两列的布局
    col_select, col_button = st.columns([3, 1])

    with col_select:
        # 创建平台选择下拉菜单
        selected_platform = st.selectbox(
            "请选择数据平台:",
            options=PLATFORM_LIST,
            index=0  # 默认选中第一个平台 'Amazon'
        )

    with col_button:
        # 创建一个垂直对齐的按钮
        st.write("") # 占位符让按钮垂直居中
        st.write("")
        fetch_button = st.button("🚀 获取数据", use_container_width=True)

    # 3. 获取并显示数据
    if fetch_button:
        # 当用户点击按钮时，执行以下操作
        with st.spinner(f"正在从 {selected_platform} 获取数据，请稍候..."):
            # 调用我们的核心函数
            data = get_platform_data(selected_platform)

            if data:
                # 如果成功获取到数据，将其转换为Pandas DataFrame并显示
                # 使用st.dataframe可以让表格滚动，比st.table更适合大量数据
                df = pd.DataFrame(data)
                st.success(f"✅ 成功获取 {len(data)} 条数据")
                st.dataframe(df, use_container_width=True)
            else:
                # 如果爬虫失败，显示API接口弹窗
                st.error("⚠️ 爬虫无法获取数据")
                
                # 显示API接口选项（弹窗效果）
                with st.expander("🔌 使用API接口获取数据", expanded=True):
                    st.info(f"爬虫暂时无法访问{selected_platform}，您可以使用API接口代替")
                    
                    # API配置输入
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        api_endpoint = st.text_input(
                            "API端点",
                            placeholder=f"https://api.example.com/{selected_platform.lower()}",
                            help="输入第三方API的完整URL"
                        )
                        api_key = st.text_input(
                            "API密钥",
                            type="password",
                            placeholder="输入您的API密钥",
                            help="从API提供商获取的密钥"
                        )
                    
                    with col2:
                        st.markdown("**推荐的API服务商:**")
                        
                        if selected_platform == "Amazon":
                            st.markdown("- [Rainforest API](https://www.rainforestapi.com/)")
                            st.markdown("- [ScraperAPI](https://www.scraperapi.com/)")
                            st.markdown("- [RapidAPI Amazon](https://rapidapi.com/)")
                        elif selected_platform == "TikTok":
                            st.markdown("- [TikTok Research API](https://developers.tiktok.com/)")
                            st.markdown("- [RapidAPI TikTok](https://rapidapi.com/)")
                        elif selected_platform == "YouTube":
                            st.markdown("- [YouTube Data API](https://developers.google.com/youtube/v3)")
                        else:
                            st.markdown("- [ScraperAPI](https://www.scraperapi.com/)")
                            st.markdown("- [Bright Data](https://brightdata.com/)")
                    
                    # 保存API配置选项
                    save_api = st.checkbox("保存此API配置以便下次使用")
                    
                    if st.button("📡 使用API获取数据", type="primary"):
                        if not api_endpoint or not api_key:
                            st.error("请输入API端点和密钥")
                        else:
                            with st.spinner("正在通过API获取数据..."):
                                # 这里应该调用实际的API
                                st.warning("API功能正在开发中...")
                                st.info(f"将使用 {api_endpoint} 获取 {selected_platform} 数据")
                                
                                # 如果选择保存，保存API配置
                                if save_api:
                                    import json
                                    import os
                                    
                                    config_file = "config/api_keys.json"
                                    apis = []
                                    
                                    if os.path.exists(config_file):
                                        try:
                                            with open(config_file, 'r', encoding='utf-8') as f:
                                                apis = json.load(f)
                                        except:
                                            pass
                                    
                                    new_api = {
                                        "platform": selected_platform,
                                        "name": f"{selected_platform} Data API",
                                        "url": api_endpoint,
                                        "api_key": api_key,
                                        "status": "active",
                                        "created_at": datetime.now().isoformat()
                                    }
                                    
                                    # 检查是否已存在
                                    existing = next((i for i, a in enumerate(apis) if a.get('platform') == selected_platform), None)
                                    
                                    if existing is not None:
                                        apis[existing] = new_api
                                    else:
                                        apis.append(new_api)
                                    
                                    os.makedirs(os.path.dirname(config_file), exist_ok=True)
                                    with open(config_file, 'w', encoding='utf-8') as f:
                                        json.dump(apis, f, ensure_ascii=False, indent=2)
                                    
                                    st.success("✅ API配置已保存到API管理模块")
                
                # 提供替代方案
                st.markdown("---")
                st.markdown("### 💡 其他解决方案")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔧 优化爬虫", use_container_width=True):
                        st.info("前往'爬虫自我迭代控制台'优化爬虫性能")
                
                with col2:
                    if st.button("🔗 API管理", use_container_width=True):
                        st.info("前往'API管理'模块查看已保存的API")
                
                with col3:
                    if st.button("📖 查看日志", use_container_width=True):
                        st.info("前往'日志与设置'查看详细错误信息")
