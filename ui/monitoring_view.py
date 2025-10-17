"""
Monitoring Dashboard UI Page
监控仪表板 UI 页面

Real-time monitoring interface using Streamlit
使用 Streamlit 的实时监控界面
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from core.monitoring import get_monitoring_dashboard
from core.i18n import t


def render_monitoring_page():
    """Render monitoring dashboard page / 渲染监控仪表板页面"""
    
    st.title("📊 " + t("monitoring_dashboard_title", default="实时监控仪表板 / Real-time Monitoring Dashboard"))
    
    # Get dashboard instance
    dashboard = get_monitoring_dashboard()
    
    # Add refresh button and auto-refresh
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        auto_refresh = st.checkbox("🔄 自动刷新 / Auto Refresh", value=False)
    
    with col2:
        if st.button("🔄 立即刷新 / Refresh Now"):
            st.rerun()
    
    with col3:
        if st.button("🗑️ 重置数据 / Reset Data"):
            dashboard.reset()
            st.success("数据已重置 / Data reset")
            time.sleep(1)
            st.rerun()
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Get dashboard data
    try:
        data = dashboard.get_dashboard_data()
        current_stats = data["current_stats"]
        platform_stats = data["platform_stats"]
        recent_requests = data["recent_requests"]
        recent_errors = data["recent_errors"]
        alerts = data["alerts"]
    except Exception as e:
        st.error(f"获取数据失败 / Failed to get data: {e}")
        return
    
    st.divider()
    
    # === Overview Metrics / 概览指标 ===
    st.subheader("📈 概览 / Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="总请求 / Total Requests",
            value=current_stats["total_requests"],
            delta=None
        )
    
    with col2:
        success_rate = current_stats["success_rate"]
        st.metric(
            label="成功率 / Success Rate",
            value=f"{success_rate:.1f}%",
            delta=None,
            delta_color="normal" if success_rate > 90 else "inverse"
        )
    
    with col3:
        st.metric(
            label="抓取项目 / Items Scraped",
            value=current_stats["total_items_scraped"],
            delta=None
        )
    
    with col4:
        st.metric(
            label="错误数 / Errors",
            value=current_stats["total_errors"],
            delta=None,
            delta_color="inverse"
        )
    
    # === Performance Metrics / 性能指标 ===
    st.divider()
    st.subheader("⚡ 性能 / Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="平均响应时间 / Avg Response Time",
            value=f"{current_stats['avg_response_time']:.2f}s"
        )
    
    with col2:
        st.metric(
            label="最小响应时间 / Min Response Time",
            value=f"{current_stats['min_response_time']:.2f}s"
        )
    
    with col3:
        st.metric(
            label="最大响应时间 / Max Response Time",
            value=f"{current_stats['max_response_time']:.2f}s"
        )
    
    with col4:
        st.metric(
            label="请求/分钟 / Requests/min",
            value=f"{current_stats['requests_per_minute']:.1f}"
        )
    
    # === Platform Statistics / 平台统计 ===
    if platform_stats:
        st.divider()
        st.subheader("🌐 平台统计 / Platform Statistics")
        
        platform_df = pd.DataFrame([
            {
                "平台 / Platform": platform,
                "请求 / Requests": stats["requests"],
                "成功 / Success": stats["successful"],
                "失败 / Failed": stats["failed"],
                "项目 / Items": stats["items"],
                "成功率 / Success Rate": f"{stats['successful'] / stats['requests'] * 100:.1f}%" if stats["requests"] > 0 else "0%"
            }
            for platform, stats in platform_stats.items()
        ])
        
        st.dataframe(platform_df, use_container_width=True, hide_index=True)
    
    # === Alerts / 警报 ===
    if alerts:
        st.divider()
        st.subheader("🚨 警报 / Alerts")
        
        for alert in reversed(alerts):  # Show most recent first
            severity = alert["severity"]
            
            if severity == "error":
                st.error(f"🔴 [{alert['timestamp']}] {alert['message']}")
            elif severity == "warning":
                st.warning(f"🟡 [{alert['timestamp']}] {alert['message']}")
            else:
                st.info(f"🔵 [{alert['timestamp']}] {alert['message']}")
    
    # === Recent Requests / 最近请求 ===
    if recent_requests:
        st.divider()
        st.subheader("📋 最近请求 / Recent Requests")
        
        # Limit to last 20 for display
        display_requests = recent_requests[-20:]
        
        requests_df = pd.DataFrame([
            {
                "时间 / Time": req["timestamp"].split("T")[1][:8],  # Show only time part
                "平台 / Platform": req["platform"],
                "状态 / Status": "✅ 成功" if req["success"] else "❌ 失败",
                "响应时间 / Response Time (s)": f"{req['response_time']:.2f}",
                "项目数 / Items": req["items_count"]
            }
            for req in display_requests
        ])
        
        st.dataframe(requests_df, use_container_width=True, hide_index=True)
    
    # === Recent Errors / 最近错误 ===
    if recent_errors:
        st.divider()
        st.subheader("❌ 最近错误 / Recent Errors")
        
        # Limit to last 10 for display
        display_errors = recent_errors[-10:]
        
        errors_df = pd.DataFrame([
            {
                "时间 / Time": err["timestamp"].split("T")[1][:8],
                "平台 / Platform": err["platform"],
                "错误类型 / Error Type": err.get("error_type", "未知 / Unknown")
            }
            for err in display_errors
        ])
        
        st.dataframe(errors_df, use_container_width=True, hide_index=True)
    
    # === System Info / 系统信息 ===
    st.divider()
    st.subheader("ℹ️ 系统信息 / System Info")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**运行时间 / Uptime**: {current_stats['uptime_seconds'] / 60:.1f} 分钟 / minutes")
    
    with col2:
        st.info(f"**最后更新 / Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Add some helpful information
    st.divider()
    st.markdown("""
    ### 使用说明 / Instructions
    
    - **自动刷新**: 勾选后每 5 秒自动刷新数据 / Auto refresh data every 5 seconds when enabled
    - **立即刷新**: 手动刷新当前数据 / Manually refresh current data
    - **重置数据**: 清除所有统计数据，从头开始 / Clear all statistics and start fresh
    - **警报阈值**: 
        - 错误率 > 10% 触发警告 / Error rate > 10% triggers warning
        - 验证码率 > 5% 触发警告 / Captcha rate > 5% triggers warning
        - 平均响应时间 > 10秒 触发提示 / Avg response time > 10s triggers info
    """)


if __name__ == "__main__":
    render_monitoring_page()
