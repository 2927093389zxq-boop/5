
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

def render_inventory_management():
    """渲染 ERP 库存管理页面"""
    st.title("📦 库存管理")
    
    # 基本统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("库存产品数", "325", delta="12")
    with col2:
        st.metric("库存总值", "¥1,245,750", delta="¥45,230")
    with col3:
        st.metric("低库存产品", "23", delta="-5")
    with col4:
        st.metric("库存周转率", "5.67", delta="0.21")
    
    st.divider()
    
    # 库存操作
    st.subheader("⚙️ 库存操作")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_term = st.text_input("搜索产品", placeholder="输入产品名称、SKU或编号...")
    with col2:
        st.write("")
        st.write("")
        if st.button("📥 入库", use_container_width=True):
            st.info("入库功能开发中...")
    with col3:
        st.write("")
        st.write("")
        if st.button("📤 出库", use_container_width=True):
            st.info("出库功能开发中...")
    
    st.divider()
    
    # 库存列表
    st.subheader("📋 库存清单")
    
    # 创建示例库存数据
    inventory_data = []
    categories = ["电子产品", "服装", "食品", "日用品", "图书"]
    statuses = ["正常", "正常", "正常", "低库存", "缺货"]
    
    for i in range(20):
        quantity = random.randint(0, 500)
        reorder_point = 50
        
        if quantity == 0:
            status = "缺货"
        elif quantity < reorder_point:
            status = "低库存"
        else:
            status = "正常"
        
        inventory_data.append({
            "产品编号": f"PROD_{1000+i}",
            "产品名称": f"测试产品 {i+1}",
            "SKU": f"SKU-{100+i}",
            "分类": random.choice(categories),
            "当前库存": quantity,
            "单位": "件",
            "再订购点": reorder_point,
            "单价": f"¥{random.randint(10, 500)}",
            "库存价值": f"¥{quantity * random.randint(10, 500):,}",
            "状态": status,
            "最后更新": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d %H:%M")
        })
    
    df = pd.DataFrame(inventory_data)
    
    # 添加过滤器
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "筛选状态",
            options=["正常", "低库存", "缺货"],
            default=["正常", "低库存", "缺货"]
        )
    with col2:
        category_filter = st.multiselect(
            "筛选分类",
            options=categories,
            default=categories
        )
    
    # 应用过滤
    if status_filter:
        df = df[df["状态"].isin(status_filter)]
    if category_filter:
        df = df[df["分类"].isin(category_filter)]
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)]
    
    # 显示表格
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # 库存分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 库存状态分布")
        status_count = df["状态"].value_counts()
        st.bar_chart(status_count)
    
    with col2:
        st.subheader("🏷️ 分类库存分布")
        category_count = df["分类"].value_counts()
        st.bar_chart(category_count)
    
    st.divider()
    
    # 库存变动趋势
    st.subheader("📈 库存变动趋势")
    
    # 生成过去30天的库存变动数据
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(29, -1, -1)]
    in_stock = [random.randint(50, 150) for _ in range(30)]
    out_stock = [random.randint(40, 140) for _ in range(30)]
    
    trend_df = pd.DataFrame({
        "日期": dates,
        "入库数量": in_stock,
        "出库数量": out_stock
    })
    
    st.line_chart(trend_df.set_index("日期"))
    
    # 需要补货的产品
    st.subheader("⚠️ 需要补货的产品")
    
    low_stock_df = df[df["状态"].isin(["低库存", "缺货"])].copy()
    
    if len(low_stock_df) > 0:
        st.warning(f"发现 {len(low_stock_df)} 个产品需要补货！")
        st.dataframe(
            low_stock_df[["产品编号", "产品名称", "SKU", "当前库存", "再订购点", "状态"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("所有产品库存正常！")
