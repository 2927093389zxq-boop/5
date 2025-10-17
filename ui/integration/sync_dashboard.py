
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

def render_sync_dashboard():
    """渲染同步仪表板"""
    st.title("🔄 SaaS-ERP 同步中心")
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["📊 同步概览", "🔄 执行同步", "📜 同步日志"])
    
    # 同步概览选项卡
    with tab1:
        st.header("同步状态概览")
        
        # 显示统计数据
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总同步次数", "127")
        with col2:
            st.metric("成功", "115")
        with col3:
            st.metric("部分成功", "8")
        with col4:
            st.metric("失败", "4")
        
        # 同步类型分布
        st.subheader("同步类型分布")
        
        # 创建模拟数据
        sync_types = pd.DataFrame({
            "类型": ["产品同步到店铺", "库存更新", "订单同步到ERP"],
            "数量": [45, 67, 15]
        })
        
        st.bar_chart(sync_types.set_index("类型"))
        
        # 最近同步活动
        st.subheader("最近同步活动")
        
        # 创建模拟数据
        recent_data = []
        for i in range(5):
            days_ago = random.randint(0, 7)
            status = random.choice(["✅ success", "⚠️ partial", "❌ error"])
            sync_type = random.choice(["产品同步到店铺", "库存更新", "订单同步到ERP"])
            
            recent_data.append({
                "时间": (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M"),
                "类型": sync_type,
                "状态": status,
                "消息": f"{'成功' if '✅' in status else '部分成功' if '⚠️' in status else '失败'}同步{random.randint(1, 10)}个项目"
            })
        
        st.dataframe(pd.DataFrame(recent_data))
    
    # 执行同步选项卡
    with tab2:
        st.header("执行同步操作")
        
        sync_operation = st.selectbox(
            "选择同步操作",
            ["产品同步到店铺", "更新店铺库存", "订单同步到ERP"]
        )
        
        if sync_operation == "产品同步到店铺":
            st.write("选择要同步的产品和目标店铺")
            
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("选择产品", ["测试产品 1 (SKU: SKU-101)", "测试产品 2 (SKU: SKU-102)"])
            with col2:
                st.selectbox("选择目标店铺", ["示例店铺 (Shopify)"])
            
            if st.button("执行同步"):
                with st.spinner("正在同步产品到店铺..."):
                    # 模拟处理
                    import time
                    time.sleep(1)
                    st.success("✅ 产品已成功同步到店铺！")
        
        elif sync_operation == "更新店铺库存":
            st.selectbox("选择要更新库存的产品", 
                ["测试产品 1 (SKU: SKU-101, 库存: 45)", "测试产品 2 (SKU: SKU-102, 库存: 18)"])
            
            if st.button("更新所有店铺库存"):
                with st.spinner("正在更新店铺产品库存..."):
                    # 模拟处理
                    import time
                    time.sleep(1)
                    st.success("✅ 库存已成功同步到所有店铺！")
