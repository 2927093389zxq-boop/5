import os
import json
import socket
import platform
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# 加载 .env 环境变量（如 OPENAI_API_KEY、MASTER_KEY 等）
load_dotenv()

# 分发与遥测
from distribution.license_manager import LicenseManager
from distribution.telemetry import TelemetrySystem

# 已有 UI / 采集模块导入（保持你的原结构）
from ui.dashboard import render_dashboard
from ui.analytics import render_analytics
from ui.prototype_view import render_prototype
from core.collectors.market_collector import fetch_all_trends
from core.collectors.youtube_collector import fetch_channel_stats
from core.collectors.policy_collector import fetch_latest_policies
from ui.api_admin import render_api_admin
from ui.auto_evolution import render_auto_evolution
from ui.auto_patch_view import render_auto_patch
from ui.ai_learning_center import render_ai_learning_center
from ui.source_attribution import render_sources

# 全局遥测对象
telemetry = None

# 菜单配置（第 13 点：结构化 + 易扩展）
MENU_STRUCTURE = {
    "智能体平台": [
        "主页", "智能分析", "原型测试",
        "权威数据中心", "数据来源追踪", "YouTube", "TikTok",
        "Amazon采集工具", "爬虫自迭代",
        "AI 学习中心", "AI 自主迭代", "AI 自动修复",
        "API 管理", "政策中心", "路线图", "系统概览", "日志与设置"
    ],
    "SaaS平台": ["SaaS仪表盘", "用户管理", "计费管理"],
    "ERP系统": ["库存管理", "产品管理", "订单管理"]
}

def ensure_basic_config():
    """
    基础目录保障。可根据需要扩展更多目录。
    """
    for d in ["config", "logs", "data", "checkpoint"]:
        os.makedirs(d, exist_ok=True)

def check_license():
    """
    读取并验证 license.json。
    若存在 .dev 文件则允许开发模式直接通过。
    """
    lm = LicenseManager()
    lic_path = "license.json"
    if not os.path.exists(lic_path):
        if os.path.exists(".dev"):
            return {"valid": True, "feature_set": "all", "telemetry_enabled": False}
        return {"valid": False, "reason": "未找到许可证文件"}
    try:
        with open(lic_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return lm.verify_license(data)
    except Exception as e:
        return {"valid": False, "reason": f"验证失败: {e}"}

def render_license_page():
    """
    许可证激活界面：
    - 上传 JSON
    - 用户可勾选是否启用 telemetry（匿名遥测）
    """
    st.title("📄 许可证激活")
    st.write("请上传有效许可证文件以继续使用。")
    uploaded_file = st.file_uploader("选择许可证文件", type=["json"])
    enable_telemetry = st.checkbox("启用匿名遥测（改进体验）", value=True)
    if uploaded_file:
        try:
            license_data = json.load(uploaded_file)
            # 覆盖遥测偏好（如果 schema 中包含 telemetry_enabled）
            if isinstance(license_data, dict) and "data" in license_data:
                license_data["data"]["telemetry_enabled"] = enable_telemetry
            lm = LicenseManager()
            result = lm.verify_license(license_data)
            if result.get("valid"):
                with open("license.json", "w", encoding="utf-8") as f:
                    json.dump(license_data, f, ensure_ascii=False, indent=2)
                st.success("许可证已激活 ✅")
                st.write(f"功能集: {result.get('feature_set','N/A')}")
                st.write(f"剩余天数: {result.get('expires_in_days','N/A')}")
                if st.button("进入系统"):
                    st.rerun()
            else:
                st.error(f"无效许可证: {result.get('reason')}")
        except Exception as e:
            st.error(f"读取失败: {e}")

def init_telemetry_if_needed(license_result):
    """
    如果许可证允许且用户开启 telemetry，则初始化 TelemetrySystem。
    """
    global telemetry
    if license_result.get("telemetry_enabled") and telemetry is None:
        telemetry = TelemetrySystem()
        telemetry.collect_system_info()

def sidebar_navigation():
    """
    侧边栏导航（支持搜索过滤）。
    返回 (main_menu, sub_menu) 选择结果。
    """
    st.sidebar.header("导航")
    main_menu = st.sidebar.selectbox("主菜单", list(MENU_STRUCTURE.keys()))

    # 搜索子菜单（可选增强）
    search_keyword = st.sidebar.text_input("筛选功能(模糊)", "")
    candidates = MENU_STRUCTURE[main_menu]
    if search_keyword.strip():
        kw = search_keyword.strip().lower()
        candidates = [c for c in candidates if kw in c.lower()]

    sub_menu = st.sidebar.selectbox("功能项", candidates)
    if telemetry:
        telemetry.track_feature_usage(f"{main_menu}-{sub_menu}")
    return main_menu, sub_menu

def route_intelligent_platform(sub_menu):
    """
    智能体平台路由调度。
    """
    if sub_menu == "主页":
        render_dashboard()
    elif sub_menu == "系统概览":
        st.header("系统概览")
        st.metric("主机名", socket.gethostname())
        st.metric("系统", platform.platform())
        st.metric("时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    elif sub_menu == "智能分析":
        render_analytics()
    elif sub_menu == "原型测试":
        render_prototype()
    elif sub_menu == "权威数据中心":
        st.header("权威数据中心")
        st.info("示例来源：1688 / QuestMobile / 艾瑞 / 易观 等")
        for d in fetch_all_trends():
            st.markdown(
                f"**来源**：[{d.get('source')}]({d.get('url')})  \n"
                f"- 时间：{d.get('fetched_at')}  \n"
                f"- 内容：{d.get('metric', d.get('data',''))}  \n"
                f"- 权威度：{d.get('credibility','N/A')}"
            )
    elif sub_menu == "数据来源追踪":
        render_sources()
    elif sub_menu == "YouTube":
        st.header("YouTube 频道查询")
        cid = st.text_input("频道 ID")
        if st.button("获取频道统计"):
            try:
                res = fetch_channel_stats(cid)
                st.json(res)
            except Exception as e:
                st.error(f"查询失败: {e}")
    elif sub_menu == "TikTok":
        st.header("TikTok 趋势（占位）")
        st.write("后续通过 API 管理模块添加真实数据接口。")
    elif sub_menu == "Amazon采集工具":
        # 延迟导入，避免初始加载开销
        import ui.amazon_crawl_options
    elif sub_menu == "爬虫自迭代":
        import ui.auto_evolution_crawler
    elif sub_menu == "AI 学习中心":
        render_ai_learning_center()
    elif sub_menu == "AI 自主迭代":
        render_auto_evolution()
    elif sub_menu == "AI 自动修复":
        render_auto_patch()
    elif sub_menu == "API 管理":
        render_api_admin()
    elif sub_menu == "政策中心":
        st.header("政策中心")
        for p in fetch_latest_policies():
            st.markdown(
                f"**{p.get('source',{}).get('agency','未知')}** - {p.get('fetched_at')}  \n"
                f"{p.get('snippet','')}"
            )
    elif sub_menu == "路线图":
        from ui.roadmap_view import render_roadmap
        render_roadmap()
    elif sub_menu == "日志与设置":
        st.header("日志与设置")
        st.write("请在 config/ 下维护系统配置（示例：调度、密钥、邮箱等）。")

def route_saas_platform(sub_menu):
    if sub_menu == "SaaS仪表盘":
        import ui.saas.dashboard as saas_dash
        saas_dash.render_saas_dashboard()
    elif sub_menu == "用户管理":
        import ui.saas.users as saas_users
        saas_users.render_users_management()
    elif sub_menu == "计费管理":
        import ui.saas.billing as saas_bill
        saas_bill.render_billing_management()

def route_erp_platform(sub_menu):
    if sub_menu == "库存管理":
        import ui.erp.inventory as erp_inv
        erp_inv.render_inventory_management()
    elif sub_menu == "产品管理":
        import ui.erp.products as erp_prod
        erp_prod.render_product_management()
    elif sub_menu == "订单管理":
        import ui.erp.orders as erp_orders
        erp_orders.render_order_management()

def main():
    ensure_basic_config()
    st.set_page_config(page_title="京盛传媒 企业版智能体", layout="wide")

    license_result = check_license()
    if not license_result.get("valid"):
        render_license_page()
        return

    init_telemetry_if_needed(license_result)
    st.title("京盛传媒 企业版智能体")

    main_menu, sub_menu = sidebar_navigation()

    try:
        if main_menu == "智能体平台":
            route_intelligent_platform(sub_menu)
        elif main_menu == "SaaS平台":
            route_saas_platform(sub_menu)
        elif main_menu == "ERP系统":
            route_erp_platform(sub_menu)
        else:
            st.error("未知主菜单选择。")
    except Exception as e:
        st.error(f"渲染视图失败: {e}")

if __name__ == "__main__":
    main()