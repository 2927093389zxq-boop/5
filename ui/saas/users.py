
import streamlit as st
import pandas as pd
from datetime import datetime
import random

def render_users_management():
    """渲染 SaaS 用户管理页面"""
    st.title("👥 用户管理")
    
    # 基本统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总用户数", "156", delta="12")
    with col2:
        st.metric("活跃用户", "142", delta="8")
    with col3:
        st.metric("付费用户", "89", delta="5")
    with col4:
        st.metric("月增长率", "8.5%", delta="1.2%")
    
    st.divider()
    
    # 用户操作区
    st.subheader("⚙️ 用户操作")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("搜索用户", placeholder="输入用户名或邮箱...")
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("➕ 添加新用户", use_container_width=True):
            st.info("添加用户功能开发中...")
    
    # 示例用户列表
    st.subheader("📋 用户列表")
    
    # 创建示例数据
    users_data = []
    for i in range(10):
        users_data.append({
            "用户ID": f"USER_{1000+i}",
            "用户名": f"user{i+1}",
            "邮箱": f"user{i+1}@example.com",
            "状态": random.choice(["活跃", "活跃", "活跃", "禁用"]),
            "角色": random.choice(["管理员", "普通用户", "普通用户", "VIP用户"]),
            "注册日期": (datetime.now() - pd.Timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "最后登录": (datetime.now() - pd.Timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        })
    
    df = pd.DataFrame(users_data)
    
    # 过滤
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)]
    
    # 显示表格
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # 用户活跃度分析
    st.subheader("📊 用户活跃度分析")
    
    # 生成过去7天的活跃数据
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)]
    active_users = [random.randint(80, 120) for _ in range(7)]
    
    activity_df = pd.DataFrame({
        "日期": dates,
        "活跃用户数": active_users
    })
    
    st.line_chart(activity_df.set_index("日期"))
    
    # 用户角色分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 用户角色分布")
        role_data = pd.DataFrame({
            "角色": ["普通用户", "VIP用户", "管理员"],
            "数量": [98, 45, 13]
        })
        st.bar_chart(role_data.set_index("角色"))
    
    with col2:
        st.subheader("✅ 用户状态分布")
        status_data = pd.DataFrame({
            "状态": ["活跃", "禁用", "待激活"],
            "数量": [142, 8, 6]
        })
        st.bar_chart(status_data.set_index("状态"))
