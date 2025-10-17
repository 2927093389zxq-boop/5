
import streamlit as st
import pandas as pd
import random
from datetime import datetime

def render_inventory_view():
    """渲染库存管理视图"""
    st.title("📦 库存管理")
    
    # 创建选项卡
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 库存列表", 
        "➕ 新增产品", 
        "🔄 库存调整", 
        "📊 库存报告"
    ])
    
    # 库存列表选项卡
    with tab1:
        st.header("库存列表")
        
        # 创建模拟数据
        inventory_data = []
        for i in range(10):
            inventory_data.append({
                "产品ID": f"prod_{1000+i}",
                "产品名称": f"测试产品 {i+1}",
                "SKU": f"SKU-{100+i}",
                "类别": random.choice(["电子产品", "家居用品", "办公用品", "厨房用品", "运动器材"]),
                "当前库存": random.randint(0, 100),
                "再订购点": 15,
                "成本价": f"¥{random.randint(50, 500):.2f}",
                "零售价": f"¥{random.randint(100, 1000):.2f}",
                "状态": random.choice(["正常", "低库存", "缺货"])
            })
        
        st.dataframe(pd.DataFrame(inventory_data))
    
    # 新增产品选项卡
    with tab2:
        st.header("添加新产品")
        
        with st.form("add_product_form"):
            name = st.text_input("产品名称", max_chars=100)
            
            col1, col2 = st.columns(2)
            with col1:
                sku = st.text_input("SKU")
                category = st.text_input("类别")
                cost_price = st.number_input("成本价", min_value=0.0, format="%.2f")
            
            with col2:
                barcode = st.text_input("条形码")
                stock_quantity = st.number_input("初始库存数量", min_value=0, value=0)
                retail_price = st.number_input("零售价", min_value=0.0, format="%.2f")
            
            submitted = st.form_submit_button("添加产品")
            if submitted:
                st.success("产品添加成功！")
