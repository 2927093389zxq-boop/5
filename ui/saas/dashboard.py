
import streamlit as st
import pandas as pd
from core.saas.services.store_service import StoreService
from datetime import datetime, timedelta
import random

def render_saas_dashboard():
    """渲染 SaaS 仪表板"""
    st.title("🛍️ 电商 SaaS 仪表盘")
    
    # 初始化服务
    store_service = StoreService()
    
    # 获取所有店铺
    stores = store_service.list_stores()
    
    if not stores:
        st.info("暂无店铺信息，请先添加店铺。")
        if st.button("添加示例店铺"):
            # 添加示例店铺
            from core.saas.models.store import Store
            store = Store(
                name="示例店铺",
                platform="Shopify",
                status="active"
            )
            store_service.save_store(store)
            st.success("已添加示例店铺")
            st.rerun()
        return
    
    # 店铺选择器
    selected_store = st.selectbox(
        "选择店铺",
        options=[store.store_id for store in stores],
        format_func=lambda x: next((s.name for s in stores if s.store_id == x), x)
    )
    
    # 获取选中的店铺
    store = next((s for s in stores if s.store_id == selected_store), None)
    
    if not store:
        st.warning("未找到选中的店铺")
        return
    
    # 基础信息卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("平台", store.platform)
    with col2:
        st.metric("状态", store.status)
    with col3:
        st.metric("创建日期", store.created_at.strftime("%Y-%m-%d"))
    
    # 模拟数据
    st.subheader("📊 销售概览")
    
    # 生成过去30天的日期
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)]
    
    # 模拟销售数据
    random.seed(hash(store.store_id))
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
