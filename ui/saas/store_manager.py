
import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import random

def render_store_manager():
    """渲染店铺管理界面"""
    st.title("🏪 店铺管理")
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["📋 店铺列表", "➕ 添加店铺", "⚙️ 店铺设置"])
    
    # 店铺列表选项卡
    with tab1:
        st.header("店铺列表")
        
        # 示例店铺数据
        stores_data = [
            {
                "店铺ID": "STORE_001",
                "店铺名称": "示例店铺 1",
                "平台": "Amazon",
                "状态": "运营中",
                "创建时间": "2024-01-15 10:30:00",
                "月销售额": "¥125,000"
            },
            {
                "店铺ID": "STORE_002",
                "店铺名称": "示例店铺 2",
                "平台": "Shopify",
                "状态": "运营中",
                "创建时间": "2024-02-20 14:15:00",
                "月销售额": "¥98,500"
            },
            {
                "店铺ID": "STORE_003",
                "店铺名称": "示例店铺 3",
                "平台": "eBay",
                "状态": "暂停中",
                "创建时间": "2024-03-10 09:00:00",
                "月销售额": "¥45,200"
            }
        ]
        
        # 显示店铺表格
        st.dataframe(pd.DataFrame(stores_data), use_container_width=True, hide_index=True)
        
        # 统计信息
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总店铺数", len(stores_data))
        with col2:
            active_stores = len([s for s in stores_data if s["状态"] == "运营中"])
            st.metric("运营中", active_stores)
        with col3:
            total_sales = sum([float(s["月销售额"].replace("¥", "").replace(",", "")) for s in stores_data])
            st.metric("总月销售额", f"¥{total_sales:,.0f}")
    
    # 添加店铺选项卡
    with tab2:
        st.header("添加新店铺")
        
        # 表单
        with st.form("add_store_form"):
            name = st.text_input("店铺名称", max_chars=100)
            platform = st.selectbox("电商平台", ["Amazon", "Shopify", "Etsy", "eBay", "Walmart", "其他"])
            
            col1, col2 = st.columns(2)
            with col1:
                api_key = st.text_input("API Key", type="password")
            with col2:
                api_secret = st.text_input("API Secret", type="password")
            
            status = st.selectbox("状态", ["运营中", "暂停中", "待审核"])
            
            submitted = st.form_submit_button("添加店铺")
            if submitted:
                if name and platform:
                    st.success(f"店铺 '{name}' 添加成功！")
                    st.info("店铺信息已保存，请刷新页面查看。")
                else:
                    st.warning("请填写店铺名称和平台。")
    
    # 店铺设置选项卡
    with tab3:
        st.header("店铺设置")
        
        # 选择店铺
        selected_store = st.selectbox(
            "选择要设置的店铺",
            options=["STORE_001", "STORE_002", "STORE_003"],
            format_func=lambda x: f"{x} - 示例店铺 {x.split('_')[1]}"
        )
        
        st.divider()
        
        # 设置表单
        st.subheader("基本设置")
        
        with st.form("store_settings_form"):
            store_name = st.text_input("店铺名称", value=f"示例店铺 {selected_store.split('_')[1]}")
            
            col1, col2 = st.columns(2)
            with col1:
                auto_sync = st.checkbox("启用自动同步", value=True)
                sync_interval = st.number_input("同步间隔（分钟）", min_value=5, max_value=1440, value=60)
            with col2:
                notification = st.checkbox("启用通知", value=True)
                low_stock_alert = st.checkbox("低库存提醒", value=True)
            
            submitted = st.form_submit_button("保存设置")
            if submitted:
                st.success("设置已保存！")
