"""
Authoritative Data Research Center - Enhanced UI with real data and visualizations
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
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
    tab1, tab2, tab3 = st.tabs(["📈 数据可视化", "📋 详细数据", "🔍 数据源管理"])
    
    with tab1:
        render_visualizations(trends, sources)
    
    with tab2:
        render_detailed_data(trends)
    
    with tab3:
        render_source_management(sources)


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
    st.info("已集成的权威数据源列表")
    
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
