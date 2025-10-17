import streamlit as st
import os
import json
from datetime import datetime
import platform

# SaaS 和 ERP 模块导入
from ui.saas.dashboard import render_saas_dashboard
from ui.saas.store_manager import render_store_manager
from ui.erp.dashboard import render_erp_dashboard
from ui.erp.inventory_view import render_inventory_view
from ui.integration.sync_dashboard import render_sync_dashboard

# 确保数据目录存在
def ensure_integration_dirs():
    """确保集成系统所需的目录存在"""
    dirs = [
        "data/saas/stores",
        "data/saas/products", 
        "data/saas/orders",
        "data/erp/inventory/products",
        "data/erp/inventory/movements",
        "data/erp/suppliers",
        "data/integration/sync_logs"
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # 创建或更新配置文件
    config_dirs = ["config"]
    for dir_path in config_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # 创建集成系统配置文件
    if not os.path.exists("config/integration_config.json"):
        with open("config/integration_config.json", "w", encoding="utf-8") as f:
            json.dump({
                "version": "1.0.0",
                "auto_sync_enabled": True,
                "sync_interval_minutes": 60,
                "notification_email": "",
                "last_sync_time": datetime.now().isoformat(),
                "system_info": {
                    "platform": platform.system(),
                    "python_version": platform.python_version()
                }
            }, f, ensure_ascii=False, indent=2)

def render_saas_erp_integration():
    """SaaS-ERP 集成系统入口"""
    # 确保目录结构存在
    ensure_integration_dirs()
    
    st.title("🔄 SaaS-ERP 集成系统")
    st.write("实现跨境电商 SaaS 平台与 ERP 系统的无缝集成")
    
    # 创建顶部选项卡
    tabs = st.tabs([
        "🛍️ SaaS 仪表盘", 
        "🏪 店铺管理", 
        "📊 ERP 仪表盘", 
        "📦 库存管理",
        "🔄 集成中心"
    ])
    
    # SaaS 仪表盘
    with tabs[0]:
        render_saas_dashboard()
    
    # 店铺管理
    with tabs[1]:
        render_store_manager()
    
    # ERP 仪表盘
    with tabs[2]:
        render_erp_dashboard()
    
    # 库存管理
    with tabs[3]:
        render_inventory_view()
    
    # 集成中心
    with tabs[4]:
        render_sync_dashboard()

# 集成到现有系统
def integrate_with_main_app():
    """与主应用程序的集成函数"""
    # 该函数可以在 run_launcher.py 中调用
    # 创建 SaaS 和 ERP 子模块
    
    # 添加以下代码到 run_launcher.py 的适当位置:
    """
    elif sub_menu == "SaaS-ERP集成":
        from saas_erp_integration import render_saas_erp_integration
        render_saas_erp_integration()
    """
    
    # 或者可以根据 run_launcher.py 中的条件添加对应的入口:
    """
    # 在主菜单选择部分添加:
    main_menu = st.selectbox(
        "主菜单",
        ["智能体平台", "SaaS平台", "ERP系统", "集成系统"]
    )
    
    # 然后在路由逻辑部分添加:
    elif main_menu == "集成系统":
        from saas_erp_integration import render_saas_erp_integration
        render_saas_erp_integration()
    """
    pass

if __name__ == "__main__":
    # 如果直接运行此文件，显示集成系统
    st.set_page_config(
        page_title="SaaS-ERP 集成系统",
        page_icon="🔄",
        layout="wide"
    )
    render_saas_erp_integration()