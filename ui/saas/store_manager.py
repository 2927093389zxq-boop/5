
import streamlit as st
import pandas as pd
from core.saas.models.store import Store
from core.saas.services.store_service import StoreService
from datetime import datetime

def render_store_manager():
    """渲染店铺管理界面"""
    st.title("🏪 店铺管理")
    
    # 初始化服务
    store_service = StoreService()
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["📋 店铺列表", "➕ 添加店铺", "⚙️ 店铺设置"])
    
    # 店铺列表选项卡
    with tab1:
        st.header("店铺列表")
        
        # 获取所有店铺
        stores = store_service.list_stores()
        
        if not stores:
            st.info("暂无店铺信息，请添加店铺。")
        else:
            # 将店铺转换为表格格式
            stores_data = []
            for store in stores:
                stores_data.append({
                    "店铺ID": store.store_id,
                    "店铺名称": store.name,
                    "平台": store.platform,
                    "状态": store.status,
                    "创建时间": store.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })
            
            # 显示店铺表格
            st.dataframe(pd.DataFrame(stores_data))
    
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
            
            status = st.selectbox("状态", ["active", "inactive", "pending"])
            
            submitted = st.form_submit_button("添加店铺")
            if submitted:
                if name and platform:
                    # 创建新店铺对象
                    store = Store(
                        name=name,
                        platform=platform,
                        api_key=api_key,
                        api_secret=api_secret,
                        status=status
                    )
                    
                    # 保存店铺
                    if store_service.save_store(store):
                        st.success(f"店铺 '{name}' 添加成功！")
                    else:
                        st.error("店铺添加失败！")
                else:
                    st.warning("请填写店铺名称和平台。")
    
    # 店铺设置选项卡
    with tab3:
        st.header("店铺设置")
        st.info("请在店铺列表中选择要设置的店铺")
