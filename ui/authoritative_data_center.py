"""
Authoritative Data Research Center - Enhanced UI with real data and visualizations
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
from datetime import datetime
from core.collectors.market_collector import fetch_all_trends, get_all_sources, DATA_SOURCES


def render_authoritative_data_center():
    """
    Render the authoritative data research center with real data,
    visualizations, and hover-enabled source links.
    """
    st.header("📊 权威数据调研中心")
    st.markdown("集成多个国际权威数据源，提供实时市场洞察与趋势分析")
    
    # Fetch data
    with st.spinner("正在获取最新数据..."):
        trends = fetch_all_trends()
        sources = get_all_sources()
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 数据可视化", "📋 详细数据", "🔍 数据源管理", "📥 数据采集"])
    
    with tab1:
        render_visualizations(trends, sources)
    
    with tab2:
        render_detailed_data(trends)
    
    with tab3:
        render_source_management(sources)
    
    with tab4:
        render_data_collection()


def render_visualizations(trends, sources):
    """Render data visualizations with interactive charts."""
    st.subheader("全球电商与贸易趋势可视化")
    
    # Extract numeric values for visualization
    viz_data = []
    for trend in trends:
        data = trend.get('data', {})
        if 'value' in data:
            viz_data.append({
                'source': trend['source'].split('(')[0].strip(),
                'value': data['value'],
                'unit': data.get('unit', ''),
                'credibility': trend['credibility'],
                'url': trend['url'],
                'description': trend['description']
            })
    
    if viz_data:
        # Create interactive bar chart
        df_viz = pd.DataFrame(viz_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 数值指标对比")
            fig1 = go.Figure()
            
            # Add bars with hover information
            fig1.add_trace(go.Bar(
                x=df_viz['source'],
                y=df_viz['value'],
                text=[f"{v}{u}" for v, u in zip(df_viz['value'], df_viz['unit'])],
                textposition='auto',
                marker=dict(
                    color=df_viz['credibility'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="可信度")
                ),
                hovertemplate='<b>%{x}</b><br>' +
                             '数值: %{y}<br>' +
                             '可信度: %{marker.color:.0%}<br>' +
                             '<extra></extra>'
            ))
            
            fig1.update_layout(
                xaxis_title="数据源",
                yaxis_title="数值",
                height=400,
                hovermode='closest'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Add clickable links below
            st.markdown("**数据来源链接:**")
            for item in viz_data:
                st.markdown(f"- [{item['source']}]({item['url']}) - {item['description']}")
        
        with col2:
            st.markdown("##### 数据源可信度分析")
            fig2 = px.pie(
                df_viz,
                names='source',
                values='credibility',
                title='各数据源可信度权重',
                hover_data=['url'],
            )
            fig2.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>' +
                             '可信度: %{value:.0%}<br>' +
                             '<extra></extra>'
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Overall metrics
            st.metric("综合可信度", f"{df_viz['credibility'].mean():.0%}")
            st.metric("数据源数量", len(df_viz))
    
    # Growth rate visualization
    st.markdown("##### 增长趋势分析")
    growth_data = []
    for trend in trends:
        data = trend.get('data', {})
        if 'growth_rate' in data or 'cagr' in data:
            growth_data.append({
                'source': trend['source'].split('(')[0].strip(),
                'rate': data.get('growth_rate', data.get('cagr', 0)),
                'period': data.get('year', data.get('period', 'N/A')),
                'url': trend['url']
            })
    
    if growth_data:
        df_growth = pd.DataFrame(growth_data)
        fig3 = go.Figure()
        
        colors = ['#2ecc71' if r > 10 else '#f39c12' if r > 5 else '#e74c3c' 
                  for r in df_growth['rate']]
        
        fig3.add_trace(go.Bar(
            x=df_growth['source'],
            y=df_growth['rate'],
            marker_color=colors,
            text=[f"{r:.1f}%" for r in df_growth['rate']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                         '增长率: %{y:.1f}%<br>' +
                         '<extra></extra>'
        ))
        
        fig3.update_layout(
            title='市场增长率对比',
            xaxis_title='数据源',
            yaxis_title='增长率 (%)',
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)


def render_detailed_data(trends):
    """Render detailed data table with hover information."""
    st.subheader("详细数据列表")
    
    for i, trend in enumerate(trends, 1):
        with st.expander(f"📊 {i}. {trend['source']} (可信度: {trend['credibility']:.0%})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**指标:** {trend['metric']}")
                st.markdown(f"**描述:** {trend['description']}")
                st.markdown(f"**数据来源:** [{trend['url']}]({trend['url']})")
                st.markdown(f"**采集时间:** {trend['fetched_at']}")
                
                # Display detailed data
                if 'data' in trend:
                    st.json(trend['data'])
            
            with col2:
                # Progress bar for credibility
                st.markdown("**可信度评分**")
                st.progress(trend['credibility'])
                st.caption(f"{trend['credibility']:.0%}")
                
                # Quick stats
                data = trend.get('data', {})
                if 'value' in data:
                    st.metric("数值", f"{data['value']}{data.get('unit', '')}")
                if 'growth_rate' in data:
                    st.metric("增长率", f"{data['growth_rate']}%")
                elif 'cagr' in data:
                    st.metric("复合增长率", f"{data['cagr']}%")


def render_source_management(sources):
    """Render data source management interface."""
    st.subheader("数据源管理")
    
    # 添加URL管理接口
    st.markdown("##### 🔗 添加自定义数据源")
    st.info("在此添加您自己的权威数据源URL，这些数据将提供给爬虫爬取并供智能分析参考")
    
    with st.expander("➕ 添加新数据源", expanded=False):
        with st.form("add_data_source"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("数据源名称", placeholder="例如: Statista Electronics Market")
                new_url = st.text_input("数据源URL", placeholder="https://example.com/data")
            with col2:
                new_description = st.text_area("描述", placeholder="简要描述此数据源提供的信息")
                new_credibility = st.slider("可信度评分", 0.0, 1.0, 0.95, 0.05)
            
            submit_button = st.form_submit_button("添加数据源")
            
            if submit_button:
                if new_name and new_url:
                    # 保存到配置文件
                    config_file = "config/custom_data_sources.json"
                    os.makedirs("config", exist_ok=True)
                    
                    # 加载现有配置
                    custom_sources = []
                    if os.path.exists(config_file):
                        try:
                            with open(config_file, 'r', encoding='utf-8') as f:
                                custom_sources = json.load(f)
                        except:
                            custom_sources = []
                    
                    # 添加新数据源
                    custom_sources.append({
                        "name": new_name,
                        "url": new_url,
                        "description": new_description,
                        "credibility": new_credibility,
                        "added_at": pd.Timestamp.now().isoformat()
                    })
                    
                    # 保存
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(custom_sources, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"✅ 已添加数据源: {new_name}")
                    st.info("💡 此数据源将在下次数据采集时被爬虫使用")
                    st.rerun()
                else:
                    st.error("请填写名称和URL")
    
    # 显示自定义数据源
    st.markdown("##### 📋 自定义数据源列表")
    config_file = "config/custom_data_sources.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                custom_sources = json.load(f)
            
            if custom_sources:
                for idx, source in enumerate(custom_sources):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{source['name']}**")
                        st.caption(source.get('description', ''))
                    
                    with col2:
                        st.markdown(f"[访问URL]({source['url']})")
                        st.caption(f"添加时间: {source.get('added_at', 'N/A')[:10]}")
                    
                    with col3:
                        st.metric("可信度", f"{source['credibility']:.0%}")
                    
                    st.markdown("---")
            else:
                st.info("暂无自定义数据源，点击上方'添加新数据源'开始添加")
        except Exception as e:
            st.error(f"加载自定义数据源失败: {e}")
    else:
        st.info("暂无自定义数据源，点击上方'添加新数据源'开始添加")
    
    st.markdown("---")
    st.markdown("##### 🌐 已集成的权威数据源")
    st.caption("系统内置的权威数据源")
    
    # Create a dataframe for better display
    df_sources = pd.DataFrame(sources)
    
    # Display as interactive table
    st.markdown("##### 集成数据源概览")
    
    for idx, source in enumerate(sources, 1):
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"**{idx}. {source['name']}**")
            st.caption(source['description'])
        
        with col2:
            st.markdown(f"[访问数据源]({source['url']})")
        
        with col3:
            # Credibility indicator
            cred = source['credibility']
            if cred >= 0.95:
                st.success(f"✓ {cred:.0%}")
            elif cred >= 0.90:
                st.info(f"○ {cred:.0%}")
            else:
                st.warning(f"△ {cred:.0%}")
        
        st.markdown("---")
    
    # Summary statistics
    st.markdown("##### 统计摘要")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总数据源", len(sources))
    
    with col2:
        high_cred = sum(1 for s in sources if s['credibility'] >= 0.95)
        st.metric("高可信度源", high_cred)
    
    with col3:
        avg_cred = sum(s['credibility'] for s in sources) / len(sources)
        st.metric("平均可信度", f"{avg_cred:.0%}")
    
    with col4:
        st.metric("覆盖领域", "电商+贸易")
    
    # Visualization of source credibility distribution
    st.markdown("##### 可信度分布")
    fig = px.bar(
        df_sources,
        x='name',
        y='credibility',
        color='credibility',
        color_continuous_scale='RdYlGn',
        labels={'name': '数据源', 'credibility': '可信度'},
        hover_data=['description', 'url']
    )
    fig.update_layout(height=300, showlegend=False)
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>' +
                     '可信度: %{y:.0%}<br>' +
                     '<extra></extra>'
    )
    st.plotly_chart(fig, use_container_width=True)


def render_data_collection():
    """Render data collection tab with hourly scraping and manual upload."""
    st.subheader("📥 数据采集与存储")
    st.info("支持自动爬取权威数据源或手动上传数据文件")
    
    # Create two columns for different collection methods
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("##### 🤖 自动爬取配置")
        
        # Scraping configuration
        enable_auto_scrape = st.checkbox(
            "启用自动爬取",
            value=False,
            help="启用后，系统将每小时自动爬取权威数据源"
        )
        
        if enable_auto_scrape:
            scrape_interval = st.selectbox(
                "爬取间隔",
                ["每小时", "每2小时", "每6小时", "每12小时", "每24小时"],
                index=0
            )
            
            # Source selection
            sources = get_all_sources()
            source_names = [s['name'] for s in sources]
            
            selected_sources = st.multiselect(
                "选择要爬取的数据源",
                source_names,
                default=source_names[:3],
                help="选择要定时爬取的权威数据源"
            )
            
            st.markdown("**去重设置:**")
            dedupe_method = st.radio(
                "去重方式",
                ["基于URL", "基于内容哈希", "基于标题+时间"],
                horizontal=True,
                help="防止采集重复信息"
            )
            
            # Storage location
            storage_path = st.text_input(
                "存储路径",
                value="data/authoritative_sources",
                help="采集数据的保存路径"
            )
            
            if st.button("💾 保存爬取配置", type="primary"):
                config = {
                    "enabled": enable_auto_scrape,
                    "interval": scrape_interval,
                    "sources": selected_sources,
                    "dedupe_method": dedupe_method,
                    "storage_path": storage_path,
                    "last_updated": datetime.now().isoformat()
                }
                
                # Save configuration
                os.makedirs("config", exist_ok=True)
                with open("config/scraping_config.json", 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                st.success("✅ 爬取配置已保存！")
                st.info(f"系统将{scrape_interval}爬取选定的数据源")
        else:
            st.info("自动爬取未启用")
            st.caption("启用后可配置定时爬取任务")
    
    with col2:
        st.markdown("##### 📤 手动上传数据")
        
        st.info("如果爬虫无法访问，可以手动上传PDF、TXT或图片文件")
        
        # File uploader
        upload_type = st.radio(
            "上传类型",
            ["PDF文档", "文本文件", "图片"],
            horizontal=True
        )
        
        if upload_type == "PDF文档":
            uploaded_file = st.file_uploader(
                "选择PDF文件",
                type=['pdf'],
                help="上传包含市场数据的PDF文档"
            )
            
            if uploaded_file:
                st.success(f"已选择: {uploaded_file.name}")
                
                # Metadata
                with st.form("pdf_metadata"):
                    title = st.text_input("文档标题", placeholder="例如：2024年电商市场报告")
                    source = st.text_input("来源", placeholder="例如：McKinsey, Statista")
                    date = st.date_input("发布日期")
                    tags = st.text_input("标签", placeholder="用逗号分隔，例如：电商,市场,趋势")
                    
                    submitted = st.form_submit_button("📥 保存PDF")
                    
                    if submitted:
                        if not title:
                            st.error("请填写文档标题")
                        else:
                            # Save PDF
                            save_dir = "data/authoritative_sources/pdf"
                            os.makedirs(save_dir, exist_ok=True)
                            
                            # Create safe filename
                            import re
                            safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:50]
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{safe_title}_{timestamp}.pdf"
                            filepath = os.path.join(save_dir, filename)
                            
                            # Save file
                            with open(filepath, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Save metadata
                            metadata = {
                                "title": title,
                                "source": source,
                                "date": str(date),
                                "tags": [t.strip() for t in tags.split(',') if t.strip()],
                                "filename": filename,
                                "filepath": filepath,
                                "uploaded_at": datetime.now().isoformat()
                            }
                            
                            metadata_file = filepath.replace('.pdf', '_metadata.json')
                            with open(metadata_file, 'w', encoding='utf-8') as f:
                                json.dump(metadata, f, ensure_ascii=False, indent=2)
                            
                            st.success(f"✅ PDF已保存: {filepath}")
                            st.balloons()
        
        elif upload_type == "文本文件":
            uploaded_file = st.file_uploader(
                "选择TXT文件",
                type=['txt'],
                help="上传包含市场数据的文本文件"
            )
            
            if uploaded_file:
                st.success(f"已选择: {uploaded_file.name}")
                
                # Preview content
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                st.text_area("内容预览", content[:500] + "...", height=200)
                
                with st.form("txt_metadata"):
                    title = st.text_input("文件标题")
                    source = st.text_input("来源")
                    tags = st.text_input("标签", placeholder="用逗号分隔")
                    
                    submitted = st.form_submit_button("📥 保存文本")
                    
                    if submitted and title:
                        save_dir = "data/authoritative_sources/txt"
                        os.makedirs(save_dir, exist_ok=True)
                        
                        import re
                        safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:50]
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{safe_title}_{timestamp}.txt"
                        filepath = os.path.join(save_dir, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        st.success(f"✅ 文本已保存: {filepath}")
        
        else:  # 图片
            uploaded_file = st.file_uploader(
                "选择图片文件",
                type=['png', 'jpg', 'jpeg'],
                help="上传包含数据的图片（如图表、截图）"
            )
            
            if uploaded_file:
                st.image(uploaded_file, caption="上传的图片", use_container_width=True)
                
                with st.form("image_metadata"):
                    title = st.text_input("图片标题")
                    description = st.text_area("描述")
                    source = st.text_input("来源")
                    
                    submitted = st.form_submit_button("📥 保存图片")
                    
                    if submitted and title:
                        save_dir = "data/authoritative_sources/images"
                        os.makedirs(save_dir, exist_ok=True)
                        
                        import re
                        safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:50]
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        ext = uploaded_file.name.split('.')[-1]
                        filename = f"{safe_title}_{timestamp}.{ext}"
                        filepath = os.path.join(save_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        
                        st.success(f"✅ 图片已保存: {filepath}")
    
    # Saved files section
    st.markdown("---")
    st.markdown("### 📁 已保存的数据文件")
    
    base_dir = "data/authoritative_sources"
    if os.path.exists(base_dir):
        # Count files
        pdf_count = len([f for f in os.listdir(os.path.join(base_dir, 'pdf')) if f.endswith('.pdf')]) if os.path.exists(os.path.join(base_dir, 'pdf')) else 0
        txt_count = len([f for f in os.listdir(os.path.join(base_dir, 'txt')) if f.endswith('.txt')]) if os.path.exists(os.path.join(base_dir, 'txt')) else 0
        img_count = len([f for f in os.listdir(os.path.join(base_dir, 'images')) if f.endswith(('.png', '.jpg', '.jpeg'))]) if os.path.exists(os.path.join(base_dir, 'images')) else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("PDF文档", pdf_count)
        with col2:
            st.metric("文本文件", txt_count)
        with col3:
            st.metric("图片文件", img_count)
    else:
        st.info("暂无保存的数据文件")
    
    # Search interface
    st.markdown("---")
    st.markdown("### 🔍 搜索已保存数据")
    
    search_query = st.text_input(
        "输入关键词搜索",
        placeholder="搜索标题、标签、内容...",
        help="使用AI搜索已保存的所有数据文件"
    )
    
    if st.button("🔍 开始搜索") and search_query:
        with st.spinner("AI正在搜索相关数据..."):
            # This would integrate with AI to search through saved files
            st.info(f"搜索功能开发中...关键词: {search_query}")
            st.caption("将使用AI分析PDF内容、文本和图片OCR结果进行智能搜索")
