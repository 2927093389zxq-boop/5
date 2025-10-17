import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from core.integration.sync_service import SyncService
from core.erp.inventory.inventory_manager import InventoryManager
from core.saas.services.store_service import StoreService

def render_sync_dashboard():
    """渲染同步仪表板"""
    st.title("🔄 SaaS-ERP 同步中心")
    
    # 初始化服务
    sync_service = SyncService()
    inventory_manager = InventoryManager()
    store_service = StoreService()
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["📊 同步概览", "🔄 执行同步", "📜 同步日志"])
    
    # 同步概览选项卡
    with tab1:
        st.header("同步状态概览")
        
        # 获取最近的同步日志
        recent_logs = sync_service.get_logs(limit=100)
        
        if not recent_logs:
            st.info("暂无同步记录。")
        else:
            # 统计各种同步类型和状态
            sync_types = {}
            status_counts = {"success": 0, "partial": 0, "error": 0, "warning": 0}
            
            for log in recent_logs:
                if log.sync_type in sync_types:
                    sync_types[log.sync_type] += 1
                else:
                    sync_types[log.sync_type] = 1
                
                if log.status in status_counts:
                    status_counts[log.status] += 1
            
            # 显示统计数据
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总同步次数", len(recent_logs))
            with col2:
                st.metric("成功", status_counts["success"])
            with col3:
                st.metric("部分成功", status_counts["partial"])
            with col4:
                st.metric("失败", status_counts["error"] + status_counts["warning"])
            
            # 绘制同步类型分布图
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # 同步类型分布
            type_labels = []
            type_values = []
            for sync_type, count in sync_types.items():
                if sync_type == "product_to_saas":
                    type_labels.append("产品同步到店铺")
                elif sync_type == "inventory_update":
                    type_labels.append("库存更新")
                elif sync_type == "order_to_erp":
                    type_labels.append("订单同步到ERP")
                else:
                    type_labels.append(sync_type)
                type_values.append(count)
            
            ax1.pie(type_values, labels=type_labels, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            ax1.set_title('同步类型分布')
            
            # 同步状态分布
            status_labels = ["成功", "部分成功", "错误", "警告"]
            status_values = [status_counts["success"], status_counts["partial"], 
                            status_counts["error"], status_counts["warning"]]
            status_colors = ['#66b3ff', '#99ff99', '#ff9999', '#ffcc99']
            
            ax2.pie(status_values, labels=status_labels, colors=status_colors, 
                   autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            ax2.set_title('同步状态分布')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # 最近同步活动
            st.subheader("最近同步活动")
            
            recent_data = []
            for log in recent_logs[:10]:
                status_icon = "✅" if log.status == "success" else "⚠️" if log.status == "partial" or log.status == "warning" else "❌"
                
                sync_type_display = ""
                if log.sync_type == "product_to_saas":
                    sync_type_display = "产品同步到店铺"
                elif log.sync_type == "inventory_update":
                    sync_type_display = "库存更新"
                elif log.sync_type == "order_to_erp":
                    sync_type_display = "订单同步到ERP"
                else:
                    sync_type_display = log.sync_type
                
                recent_data.append({
                    "时间": log.created_at.strftime("%Y-%m-%d %H:%M"),
                    "类型": sync_type_display,
                    "状态": f"{status_icon} {log.status}",
                    "消息": log.message
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
            # 获取产品和店铺
            erp_products = inventory_manager.list_products()
            stores = store_service.list_stores()
            
            if not erp_products:
                st.warning("ERP系统中没有产品。请先添加产品。")
            elif not stores:
                st.warning("没有配置的店铺。请先添加店铺。")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_product = st.selectbox(
                        "选择产品",
                        options=[p.product_id for p in erp_products],
                        format_func=lambda x: next((f"{p.name} (SKU: {p.sku})" for p in erp_products if p.product_id == x), x)
                    )
                
                with col2:
                    selected_store = st.selectbox(
                        "选择目标店铺",
                        options=[s.store_id for s in stores],
                        format_func=lambda x: next((f"{s.name} ({s.platform})" for s in stores if s.store_id == x), x)
                    )
                
                # 获取选中的产品
                product = next((p for p in erp_products if p.product_id == selected_product), None)
                
                if product:
                    st.write(f"**产品:** {product.name}")
                    st.write(f"**SKU:** {product.sku}")
                    st.write(f"**当前库存:** {product.stock_quantity}")
                    st.write(f"**零售价:** ¥{product.retail_price:.2f}")
                    
                    if product.stock_quantity <= 0:
                        st.warning("⚠️ 此产品库存不足，无法同步到店铺")
                    
                    if st.button("执行同步"):
                        with st.spinner("正在同步产品到店铺..."):
                            if sync_service.sync_product_to_saas(selected_product, selected_store):
                                st.success("✅ 产品已成功同步到店铺！")
                            else:
                                st.error("❌ 产品同步失败，请查看同步日志获取详细信息。")
        
        elif sync_operation == "更新店铺库存":
            # 获取产品
            erp_products = inventory_manager.list_products()
            
            if not erp_products:
                st.warning("ERP系统中没有产品。请先添加产品。")
            else:
                selected_product = st.selectbox(
                    "选择要更新库存的产品",
                    options=[p.product_id for p in erp_products],
                    format_func=lambda x: next((f"{p.name} (SKU: {p.sku}, 库存: {p.stock_quantity})" for p in erp_products if p.product_id == x), x)
                )
                
                # 获取选中的产品
                product = next((p for p in erp_products if p.product_id == selected_product), None)
                
                if product:
                    st.write(f"**产品:** {product.name}")
                    st.write(f"**SKU:** {product.sku}")
                    st.write(f"**当前库存:** {product.stock_quantity}")
                    
                    if st.button("更新所有店铺库存"):
                        with st.spinner("正在更新店铺产品库存..."):
                            if sync_service.sync_inventory_to_saas(selected_product):
                                st.success("✅ 库存已成功同步到所有店铺！")
                            else:
                                st.warning("⚠️ 库存同步完成，但可能有部分店铺未更新。请查看同步日志获取详细信息。")
        
        elif sync_operation == "订单同步到ERP":
            st.info("此处应显示待同步的订单列表，由于这是演示系统，请输入模拟订单ID。")
            
            order_id = st.text_input("输入订单ID", value="order_12345")
            
            if st.button("同步订单到ERP"):
                if order_id:
                    with st.spinner("正在同步订单到ERP系统..."):
                        if sync_service.sync_order_to_erp(order_id):
                            st.success("✅ 订单已成功同步到ERP系统！")
                        else:
                            st.error("❌ 订单同步失败，请查看同步日志获取详细信息。")
                else:
                    st.warning("请输入有效的订单ID")
    
    # 同步日志选项卡
    with tab3:
        st.header("同步日志")
        
        # 筛选选项
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sync_type_filter = st.selectbox(
                "同步类型",
                ["全部", "product_to_saas", "inventory_update", "order_to_erp"],
                format_func=lambda x: {
                    "全部": "全部", 
                    "product_to_saas": "产品同步到店铺",
                    "inventory_update": "库存更新",
                    "order_to_erp": "订单同步到ERP"
                }.get(x, x)
            )
        
        with col2:
            status_filter = st.selectbox(
                "状态",
                ["全部", "success", "partial", "error", "warning"],
                format_func=lambda x: {
                    "全部": "全部", 
                    "success": "成功",
                    "partial": "部分成功",
                    "error": "错误",
                    "warning": "警告"
                }.get(x, x)
            )
        
        with col3:
            limit = st.number_input("显示记录数", min_value=10, max_value=500, value=100, step=10)
        
        # 获取日志
        logs = sync_service.get_logs(
            sync_type=None if sync_type_filter == "全部" else sync_type_filter,
            status=None if status_filter == "全部" else status_filter,
            limit=limit
        )
        
        if not logs:
            st.info("没有符合筛选条件的同步记录。")
        else:
            # 转换为表格数据
            log_data = []
            for log in logs:
                status_icon = "✅" if log.status == "success" else "⚠️" if log.status == "partial" or log.status == "warning" else "❌"
                
                sync_type_display = ""
                if log.sync_type == "product_to_saas":
                    sync_type_display = "产品同步到店铺"
                elif log.sync_type == "inventory_update":
                    sync_type_display = "库存更新"
                elif log.sync_type == "order_to_erp":
                    sync_type_display = "订单同步到ERP"
                else:
                    sync_type_display = log.sync_type
                
                log_data.append({
                    "ID": log.log_id,
                    "时间": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "类型": sync_type_display,
                    "源ID": log.source_id,
                    "目标ID": log.target_id if log.target_id else "-",
                    "状态": f"{status_icon} {log.status}",
                    "消息": log.message
                })
            
            st.dataframe(pd.DataFrame(log_data))
            
            # 查看详细日志
            st.subheader("查看详细日志")
            selected_log_id = st.selectbox(
                "选择日志ID",
                options=[log.log_id for log in logs],
                format_func=lambda x: next((f"{l.log_id} ({l.created_at.strftime('%Y-%m-%d %H:%M')})" for l in logs if l.log_id == x), x)
            )
            
            # 获取选中的日志
            log = next((l for l in logs if l.log_id == selected_log_id), None)
            
            if log:
                st.json(log.to_dict())