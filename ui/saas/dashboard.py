
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import json
import os

def render_saas_dashboard():
    """渲染 SaaS 仪表板"""
    st.title("🛍️ 电商 SaaS 仪表盘")
    
    # 示例店铺数据
    store_data = {
        "name": "示例店铺",
        "platform": "Shopify",
        "status": "运营中",
        "created_at": "2024-01-15"
    }
    
    # 基础信息卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("平台", store_data["platform"])
    with col2:
        st.metric("状态", store_data["status"])
    with col3:
        st.metric("创建日期", store_data["created_at"])
    
    # 模拟数据
    st.subheader("📊 销售概览")
    
    # 生成过去30天的日期
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)]
    
    # 模拟销售数据
    random.seed(hash(store_data["name"]))
    sales = [random.randint(1000, 5000) for _ in range(30)]
    orders = [random.randint(10, 50) for _ in range(30)]
    
    # 使用折线图代替matplotlib
    sales_df = pd.DataFrame({
        "日期": dates,
        "销售额": sales,
        "订单数": orders
    })
    
    st.line_chart(
        sales_df.set_index("日期")[["销售额", "订单数"]]
    )
    
    # 绩效指标
    st.subheader("🔍 关键绩效指标")
    
    # 计算平均订单价值
    aov = sum(sales) / sum(orders)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总销售额", f"¥{sum(sales):,}", f"+{random.randint(5, 15)}%")
    with col2:
        st.metric("总订单数", f"{sum(orders)}", f"+{random.randint(3, 10)}%")
    with col3:
        st.metric("平均订单价值", f"¥{aov:.2f}", f"{random.randint(-5, 5)}%")
    with col4:
        st.metric("转化率", f"{random.uniform(1.5, 3.5):.2f}%", f"{random.uniform(-0.5, 0.5):.2f}%")
