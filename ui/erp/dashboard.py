
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

def render_erp_dashboard():
    """渲染 ERP 仪表板"""
    st.title("📊 ERP 系统仪表盘")
    
    # 基本指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("库存产品数", "125")
    with col2:
        st.metric("库存总值", "¥245,750.00")
    with col3:
        st.metric("低库存产品", "12", delta="-3")
    with col4:
        st.metric("库存周转率", "5.67", delta="0.21")
    
    # 库存状态概览
    st.subheader("📦 库存状态概览")
    
    # 创建模拟数据
    status_data = pd.DataFrame({
        "状态": ["正常库存", "低库存", "缺货"],
        "数量": [89, 27, 9]
    })
    
    # 使用streamlit的图表
    st.bar_chart(status_data.set_index("状态"))
    
    # 低库存产品表格
    st.subheader("⚠️ 需要补货的产品")
    
    # 创建模拟数据
    low_stock_data = []
    for i in range(5):
        low_stock_data.append({
            "产品ID": f"prod_{1000+i}",
            "产品名称": f"测试产品 {i+1}",
            "SKU": f"SKU-{100+i}",
            "当前库存": random.randint(1, 10),
            "再订购点": 15,
            "状态": "低库存" if i > 0 else "缺货"
        })
    
    st.dataframe(pd.DataFrame(low_stock_data))
