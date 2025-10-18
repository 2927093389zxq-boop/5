
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

def render_product_management():
    """渲染 ERP 产品管理页面"""
    st.title("🏷️ 产品管理")
    
    # 基本统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("产品总数", "325", delta="12")
    with col2:
        st.metric("在售产品", "298", delta="8")
    with col3:
        st.metric("新品(30天)", "15", delta="5")
    with col4:
        st.metric("平均价格", "¥256", delta="¥18")
    
    st.divider()
    
    # 产品操作
    st.subheader("⚙️ 产品操作")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_term = st.text_input("搜索产品", placeholder="输入产品名称、SKU或分类...")
    with col2:
        st.write("")
        st.write("")
        if st.button("➕ 添加产品", use_container_width=True):
            st.session_state['show_add_product_modal'] = True
    with col3:
        st.write("")
        st.write("")
        if st.button("📊 导出数据", use_container_width=True):
            st.session_state['show_export_modal'] = True
    
    # 添加产品对话框
    if st.session_state.get('show_add_product_modal', False):
        with st.expander("➕ 添加新产品", expanded=True):
            st.subheader("产品信息录入")
            
            col1, col2 = st.columns(2)
            with col1:
                new_product_name = st.text_input("产品名称*", key="new_prod_name")
                new_product_sku = st.text_input("SKU*", key="new_prod_sku")
                new_product_category = st.selectbox("分类*", 
                    ["电子产品", "服装", "食品", "日用品", "图书", "运动用品", "家居用品"], 
                    key="new_prod_cat")
                new_product_price = st.number_input("售价(¥)*", min_value=0.0, value=0.0, step=0.01, key="new_prod_price")
            with col2:
                new_product_cost = st.number_input("成本(¥)*", min_value=0.0, value=0.0, step=0.01, key="new_prod_cost")
                new_product_stock = st.number_input("初始库存", min_value=0, value=0, step=1, key="new_prod_stock")
                new_product_status = st.selectbox("状态", ["在售", "下架", "预售"], key="new_prod_status")
                new_product_desc = st.text_area("产品描述", key="new_prod_desc", height=80)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
            with col_btn1:
                if st.button("✅ 确认添加", type="primary", use_container_width=True):
                    if new_product_name and new_product_sku and new_product_price > 0:
                        st.success(f"✅ 产品添加成功！{new_product_name} (SKU: {new_product_sku})")
                        st.session_state['show_add_product_modal'] = False
                        st.rerun()
                    else:
                        st.error("请填写所有必填项（产品名称、SKU、售价）")
            with col_btn2:
                if st.button("❌ 取消", use_container_width=True):
                    st.session_state['show_add_product_modal'] = False
                    st.rerun()
    
    # 导出数据对话框
    if st.session_state.get('show_export_modal', False):
        with st.expander("📊 导出产品数据", expanded=True):
            st.subheader("选择导出格式和范围")
            
            col1, col2 = st.columns(2)
            with col1:
                export_format = st.selectbox("导出格式", ["Excel (xlsx)", "CSV", "JSON"], key="export_format")
                export_range = st.selectbox("导出范围", ["当前筛选结果", "全部产品"], key="export_range")
            with col2:
                include_fields = st.multiselect("包含字段", 
                    ["产品ID", "产品名称", "SKU", "分类", "价格", "成本", "利润率", "状态", "库存", "创建日期"],
                    default=["产品名称", "SKU", "分类", "价格", "库存", "状态"],
                    key="export_fields")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
            with col_btn1:
                if st.button("📥 下载", type="primary", use_container_width=True):
                    st.success(f"✅ 导出成功！格式: {export_format}, 范围: {export_range}")
                    st.info(f"导出字段: {', '.join(include_fields)}")
                    st.session_state['show_export_modal'] = False
                    st.rerun()
            with col_btn2:
                if st.button("❌ 取消", use_container_width=True):
                    st.session_state['show_export_modal'] = False
                    st.rerun()
    
    st.divider()
    
    # 产品列表
    st.subheader("📋 产品列表")
    
    # 创建示例产品数据
    products_data = []
    categories = ["电子产品", "服装", "食品", "日用品", "图书", "运动用品", "家居用品"]
    statuses = ["在售", "在售", "在售", "下架", "预售"]
    
    for i in range(25):
        price = random.randint(10, 1000)
        cost = int(price * random.uniform(0.5, 0.7))
        profit_margin = ((price - cost) / price * 100)
        
        products_data.append({
            "产品ID": f"PROD_{1000+i}",
            "产品名称": f"测试产品 {i+1}",
            "SKU": f"SKU-{100+i}",
            "分类": random.choice(categories),
            "价格": f"¥{price}",
            "成本": f"¥{cost}",
            "利润率": f"{profit_margin:.1f}%",
            "状态": random.choice(statuses),
            "库存": random.randint(0, 500),
            "创建日期": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "最后更新": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        })
    
    df = pd.DataFrame(products_data)
    
    # 添加过滤器
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "筛选状态",
            options=["在售", "下架", "预售"],
            default=["在售", "预售"]
        )
    with col2:
        category_filter = st.multiselect(
            "筛选分类",
            options=categories,
            default=categories
        )
    with col3:
        sort_by = st.selectbox(
            "排序方式",
            options=["产品ID", "产品名称", "价格", "库存", "创建日期"]
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
    
    st.info(f"共找到 {len(df)} 个产品")
    
    st.divider()
    
    # 产品分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 产品状态分布")
        status_count = df["状态"].value_counts()
        st.bar_chart(status_count)
    
    with col2:
        st.subheader("🏷️ 产品分类分布")
        category_count = df["分类"].value_counts()
        st.bar_chart(category_count)
    
    st.divider()
    
    # 热销产品
    st.subheader("🔥 热销产品 TOP 10")
    
    # 创建示例销售数据
    top_products_data = []
    for i in range(10):
        top_products_data.append({
            "排名": i + 1,
            "产品名称": f"热销产品 {i+1}",
            "SKU": f"SKU-{200+i}",
            "分类": random.choice(categories),
            "销量": random.randint(100, 1000),
            "销售额": f"¥{random.randint(10000, 100000):,}",
            "评分": f"{random.uniform(4.0, 5.0):.1f}⭐"
        })
    
    top_df = pd.DataFrame(top_products_data)
    st.dataframe(
        top_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # 产品生命周期
    st.subheader("📈 产品新增趋势")
    
    # 生成过去12个月的新增产品数据
    months = [(datetime.now() - timedelta(days=i*30)).strftime("%Y-%m") for i in range(11, -1, -1)]
    new_products = [random.randint(5, 25) for _ in range(12)]
    
    trend_df = pd.DataFrame({
        "月份": months,
        "新增产品": new_products
    })
    
    st.line_chart(trend_df.set_index("月份"))
