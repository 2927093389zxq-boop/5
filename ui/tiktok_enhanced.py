"""
TikTok数据采集与分析模块
TikTok Data Collection and Analysis Module
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def render_tiktok_module():
    """
    渲染TikTok模块界面
    Render TikTok Module UI
    """
    st.header("🎵 TikTok数据采集与分析")
    st.markdown("通过爬虫或API接口获取TikTok热门数据，并进行智能分析")
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📊 数据采集", "🔍 数据搜索", "📈 历史趋势"])
    
    with tab1:
        render_data_collection()
    
    with tab2:
        render_data_search()
    
    with tab3:
        render_historical_trends()


def render_data_collection():
    """数据采集界面"""
    st.markdown("### 📊 TikTok数据采集")
    
    # 模式选择
    mode = st.radio(
        "数据获取模式",
        ["爬虫模式", "API接口模式"],
        horizontal=True,
        help="如果爬虫无法访问，请使用API接口模式"
    )
    
    if mode == "爬虫模式":
        st.info("💡 使用网页爬虫获取TikTok公开数据")
        
        # 爬虫配置
        col1, col2 = st.columns(2)
        with col1:
            search_keyword = st.text_input(
                "搜索关键词",
                placeholder="例如: fashion, beauty, tech",
                help="输入要搜索的关键词"
            )
        with col2:
            max_results = st.number_input(
                "最大结果数",
                min_value=10,
                max_value=100,
                value=20,
                step=10
            )
        
        # 数据类型选择
        data_types = st.multiselect(
            "数据类型",
            ["热门视频", "热门话题", "热门音乐", "创作者数据"],
            default=["热门视频"]
        )
        
        if st.button("🚀 开始爬取", type="primary"):
            if not search_keyword:
                st.error("请输入搜索关键词")
            else:
                with st.spinner("正在爬取TikTok数据..."):
                    try:
                        # 调用爬虫功能
                        data = scrape_tiktok_data(search_keyword, max_results, data_types)
                        
                        if data:
                            st.success(f"✅ 成功采集 {len(data)} 条数据")
                            
                            # 保存数据
                            save_tiktok_data(data, search_keyword)
                            
                            # 显示数据预览
                            display_data_preview(data)
                            
                            # 发送到智能分析
                            if st.button("📊 发送到智能分析模块"):
                                st.info("数据已保存，可以在'智能分析'页面中查看")
                        else:
                            st.error("爬取失败，请尝试使用API接口模式")
                            
                    except Exception as e:
                        st.error(f"爬取失败: {e}")
                        st.warning("建议切换到'API接口模式'")
    
    else:  # API接口模式
        st.info("💡 使用第三方API接口获取TikTok数据")
        st.caption("支持的API: TikTok Research API, RapidAPI TikTok API等")
        
        # API配置
        api_key = st.text_input(
            "API密钥",
            type="password",
            placeholder="请输入TikTok API密钥",
            help="在第三方API平台申请密钥"
        )
        
        api_endpoint = st.text_input(
            "API端点 (可选)",
            placeholder="https://api.tiktok.com/v1/...",
            help="自定义API端点URL"
        )
        
        # 保存API配置
        if st.checkbox("保存API配置"):
            if api_key:
                save_api_config("tiktok", api_key, api_endpoint)
                st.success("✅ API配置已保存")
        
        # 查询参数
        col1, col2 = st.columns(2)
        with col1:
            search_keyword = st.text_input(
                "搜索关键词",
                placeholder="例如: #fashion",
                key="api_keyword"
            )
        with col2:
            max_results = st.number_input(
                "最大结果数",
                min_value=10,
                max_value=100,
                value=20,
                step=10,
                key="api_max_results"
            )
        
        if st.button("🚀 获取数据", type="primary", key="api_fetch"):
            if not api_key:
                st.error("请输入API密钥")
            elif not search_keyword:
                st.error("请输入搜索关键词")
            else:
                with st.spinner("正在从API获取数据..."):
                    try:
                        # 调用API
                        data = fetch_tiktok_api(api_key, api_endpoint, search_keyword, max_results)
                        
                        if data:
                            st.success(f"✅ 成功获取 {len(data)} 条数据")
                            
                            # 保存数据
                            save_tiktok_data(data, search_keyword)
                            
                            # 显示数据预览
                            display_data_preview(data)
                            
                            # 发送到智能分析
                            if st.button("📊 发送到智能分析模块", key="send_to_analysis"):
                                st.info("数据已保存到 data/tiktok/ 目录，可在'智能分析'模块中使用")
                        else:
                            st.error("未能获取数据，请检查API密钥和端点")
                            
                    except Exception as e:
                        st.error(f"API调用失败: {e}")


def render_data_search():
    """数据搜索界面"""
    st.markdown("### 🔍 数据搜索")
    st.info("搜索已采集的TikTok数据")
    
    # 搜索框
    search_query = st.text_input(
        "输入关键词搜索",
        placeholder="搜索标题、话题、创作者等...",
        help="搜索本地已保存的TikTok数据"
    )
    
    if st.button("🔍 搜索", type="primary") or search_query:
        if search_query:
            with st.spinner("搜索中..."):
                results = search_tiktok_data(search_query)
                
                if results:
                    st.success(f"找到 {len(results)} 条相关数据")
                    display_data_preview(results)
                else:
                    st.warning("未找到相关数据")
        else:
            st.info("请输入搜索关键词")
    
    # 显示所有保存的数据文件
    st.markdown("---")
    st.markdown("#### 📁 已保存的数据文件")
    
    data_dir = "data/tiktok"
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        if files:
            for file in sorted(files, reverse=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.text(f"📄 {file}")
                
                with col2:
                    file_path = os.path.join(data_dir, file)
                    file_size = os.path.getsize(file_path)
                    st.caption(f"{file_size / 1024:.1f} KB")
                
                with col3:
                    if st.button("查看", key=f"view_{file}"):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            st.json(data)
                        except Exception as e:
                            st.error(f"读取失败: {e}")
        else:
            st.info("暂无数据文件")
    else:
        st.info("数据目录不存在，请先采集数据")


def render_historical_trends():
    """历史趋势分析"""
    st.markdown("### 📈 历史数据趋势")
    st.info("查看TikTok数据的历史趋势变化")
    
    # 加载历史数据
    data_dir = "data/tiktok"
    
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        if files:
            # 时间范围选择
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("开始日期")
            with col2:
                end_date = st.date_input("结束日期")
            
            # 分析维度
            analysis_type = st.selectbox(
                "分析维度",
                ["播放量趋势", "点赞量趋势", "评论量趋势", "话题热度", "创作者排行"]
            )
            
            if st.button("📊 生成趋势分析", type="primary"):
                with st.spinner("生成趋势分析中..."):
                    try:
                        # 分析历史数据
                        trends = analyze_historical_trends(files, start_date, end_date, analysis_type)
                        
                        if trends:
                            st.success("✅ 趋势分析完成")
                            
                            # 这里可以添加图表展示
                            st.line_chart(trends.get('chart_data', {}))
                            
                            # 显示统计信息
                            st.markdown("#### 统计摘要")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("总数据点", trends.get('total_points', 0))
                            with col2:
                                st.metric("平均值", f"{trends.get('average', 0):.2f}")
                            with col3:
                                st.metric("增长率", f"{trends.get('growth_rate', 0):.1f}%")
                        else:
                            st.warning("未找到符合条件的数据")
                            
                    except Exception as e:
                        st.error(f"分析失败: {e}")
        else:
            st.info("暂无历史数据，请先采集数据")
    else:
        st.info("数据目录不存在，请先采集数据")


# Helper functions

def scrape_tiktok_data(keyword: str, max_results: int, data_types: List[str]) -> List[Dict]:
    """
    使用爬虫获取TikTok数据
    Use web scraping to get TikTok data
    """
    # 这里应该实现实际的爬虫逻辑
    # For now, return mock data
    logger.info(f"Scraping TikTok data for keyword: {keyword}")
    
    # Mock data
    return [
        {
            "id": f"video_{i}",
            "title": f"TikTok Video {i} - {keyword}",
            "author": f"creator_{i}",
            "views": 100000 + i * 10000,
            "likes": 5000 + i * 500,
            "comments": 200 + i * 20,
            "shares": 100 + i * 10,
            "timestamp": datetime.now().isoformat()
        }
        for i in range(min(max_results, 5))
    ]


def fetch_tiktok_api(api_key: str, endpoint: str, keyword: str, max_results: int) -> List[Dict]:
    """
    通过API获取TikTok数据
    Fetch TikTok data through API
    """
    # 这里应该实现实际的API调用逻辑
    logger.info(f"Fetching TikTok data from API for keyword: {keyword}")
    
    # Mock data
    return [
        {
            "id": f"video_api_{i}",
            "title": f"TikTok API Video {i} - {keyword}",
            "author": f"api_creator_{i}",
            "views": 150000 + i * 15000,
            "likes": 7500 + i * 750,
            "comments": 300 + i * 30,
            "shares": 150 + i * 15,
            "timestamp": datetime.now().isoformat()
        }
        for i in range(min(max_results, 5))
    ]


def save_tiktok_data(data: List[Dict], keyword: str):
    """保存TikTok数据到本地"""
    data_dir = "data/tiktok"
    os.makedirs(data_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tiktok_{keyword}_{timestamp}.json"
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            "keyword": keyword,
            "timestamp": datetime.now().isoformat(),
            "count": len(data),
            "data": data
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"TikTok data saved to {filepath}")


def save_api_config(platform: str, api_key: str, endpoint: str = ""):
    """保存API配置"""
    config_file = "config/api_keys.json"
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    # 读取现有配置
    config = []
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = []
    
    # 更新或添加配置
    platform_config = {
        "platform": platform,
        "api_key": api_key,
        "endpoint": endpoint,
        "updated_at": datetime.now().isoformat()
    }
    
    # 检查是否已存在
    existing_index = next((i for i, c in enumerate(config) if c.get('platform') == platform), None)
    
    if existing_index is not None:
        config[existing_index] = platform_config
    else:
        config.append(platform_config)
    
    # 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def display_data_preview(data: List[Dict]):
    """显示数据预览"""
    st.markdown("#### 数据预览")
    
    for idx, item in enumerate(data[:5], 1):
        with st.expander(f"🎵 {idx}. {item.get('title', 'Unknown')[:80]}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**ID:**", item.get('id', 'N/A'))
                st.write("**作者:**", item.get('author', 'N/A'))
                st.write("**播放量:**", f"{item.get('views', 0):,}")
                st.write("**点赞量:**", f"{item.get('likes', 0):,}")
            
            with col2:
                st.write("**评论数:**", f"{item.get('comments', 0):,}")
                st.write("**分享数:**", f"{item.get('shares', 0):,}")
                st.write("**时间:**", item.get('timestamp', 'N/A')[:19])
    
    if len(data) > 5:
        st.info(f"显示前5条，共 {len(data)} 条数据")


def search_tiktok_data(query: str) -> List[Dict]:
    """搜索本地TikTok数据"""
    results = []
    data_dir = "data/tiktok"
    
    if not os.path.exists(data_dir):
        return results
    
    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    for file in files:
        try:
            with open(os.path.join(data_dir, file), 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                
                # 搜索数据
                if isinstance(file_data, dict) and 'data' in file_data:
                    items = file_data['data']
                else:
                    items = file_data
                
                for item in items:
                    # 简单的关键词匹配
                    if query.lower() in str(item).lower():
                        results.append(item)
        except Exception as e:
            logger.error(f"Error reading file {file}: {e}")
    
    return results


def analyze_historical_trends(files: List[str], start_date, end_date, analysis_type: str) -> Dict:
    """分析历史趋势"""
    # 这里应该实现实际的趋势分析逻辑
    # For now, return mock trends
    
    return {
        "total_points": len(files) * 10,
        "average": 50000,
        "growth_rate": 15.5,
        "chart_data": {
            "date": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "value": [10000, 15000, 20000]
        }
    }
