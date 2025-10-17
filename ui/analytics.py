import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from core.processing.anomaly_detector import detect_anomalies
from core.collectors.market_collector import fetch_all_trends, get_all_sources

def render_analytics():
    """Renders the analytics page for anomaly detection and insights."""
    st.header("🧠 智能分析")

    # Create tabs for different views
    tab1, tab2 = st.tabs(["异常检测", "权威数据来源"])
    
    with tab1:
        st.markdown("#### 数据指标输入")
        st.write("示例输入：历史销量（用于检测异常）")

        data = [100, 103, 120, 115, 420, 130, 110]
        
        # Create interactive plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(data) + 1)),
            y=data,
            mode='lines+markers',
            name='销量',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))
        
        # Detect and mark anomalies
        anomaly_indices = detect_anomalies(data)
        if anomaly_indices:
            anomaly_x = [i + 1 for i in anomaly_indices]
            anomaly_y = [data[i] for i in anomaly_indices]
            fig.add_trace(go.Scatter(
                x=anomaly_x,
                y=anomaly_y,
                mode='markers',
                name='异常点',
                marker=dict(color='red', size=12, symbol='x')
            ))
        
        fig.update_layout(
            title="销量趋势分析",
            xaxis_title="时间周期",
            yaxis_title="销量",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 异常检测结果")
        if anomaly_indices:
            for idx in anomaly_indices:
                st.warning(f"在位置 {idx+1} 检测到异常点，值为 {data[idx]}。")
            
            # Calculate anomaly percentage
            if idx > 0:
                prev_val = data[idx-1]
                change_pct = ((data[idx] - prev_val) / prev_val) * 100
                st.markdown("#### AI 解释")
                st.info(f"系统检测到第 {idx+1} 个数据点出现异常增长（约 +{change_pct:.1f}%），可能与促销活动或投放策略调整有关。")
        else:
            st.success("未发现明显异常。")

    with tab2:
        st.markdown("#### 权威数据来源验证")
        sources = get_all_sources()
        
        # Display sources in a more structured way
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**已集成的权威数据源:**")
            for source in sources:
                with st.expander(f"📊 {source['name']} (可信度: {source['credibility']:.0%})"):
                    st.markdown(f"**描述:** {source['description']}")
                    st.markdown(f"**链接:** [{source['url']}]({source['url']})")
                    st.progress(source['credibility'])
        
        with col2:
            # Calculate average credibility
            avg_credibility = sum(s['credibility'] for s in sources) / len(sources)
            st.metric("平均可信度", f"{avg_credibility:.0%}")
            st.metric("数据源数量", len(sources))
            
            # Create credibility chart
            fig_cred = px.bar(
                x=[s['name'].split('(')[0].strip() for s in sources],
                y=[s['credibility'] for s in sources],
                labels={'x': '数据源', 'y': '可信度'},
                title='数据源可信度对比'
            )
            fig_cred.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_cred, use_container_width=True)
