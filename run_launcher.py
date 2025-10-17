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
from ui.authoritative_data_center import render_authoritative_data_center

# 全局遥测对象
telemetry = None

# 菜单配置（第 13 点：结构化 + 易扩展）
MENU_STRUCTURE = {
    "智能体平台": [
        "主页", "智能分析", "原型测试",
        "权威数据中心", "数据来源追踪", "YouTube", "TikTok",
        "Amazon采集工具", 
        "AI迭代系统",
        "API 管理", "政策中心", "系统概览", "日志与设置"
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
    elif sub_menu == "智能分析":
        render_analytics()
    elif sub_menu == "原型测试":
        render_prototype()
    elif sub_menu == "权威数据中心":
        render_authoritative_data_center()
    elif sub_menu == "数据来源追踪":
        render_sources()
    elif sub_menu == "YouTube":
        from ui.youtube_enhanced import render_youtube_query
        render_youtube_query()
    elif sub_menu == "TikTok":
        st.header("TikTok 趋势（占位）")
        st.write("后续通过 API 管理模块添加真实数据接口。")
    elif sub_menu == "Amazon采集工具":
        # 延迟导入，避免初始加载开销
        import ui.amazon_crawl_options
    elif sub_menu == "AI迭代系统":
        from ui.ai_iteration_system import render_ai_iteration_system
        render_ai_iteration_system()
    elif sub_menu == "API 管理":
        render_api_admin()
    elif sub_menu == "政策中心":
        render_policy_center()
    elif sub_menu == "系统概览":
        render_system_overview()
    elif sub_menu == "日志与设置":
        render_log_and_settings()


def render_policy_center():
    """渲染政策中心，使用图片加文字的方式显示"""
    st.header("📜 政策中心")
    st.markdown("展示来自权威数据中心的政策和行业资讯")
    
    try:
        from core.collectors.policy_collector import fetch_latest_policies
        from core.collectors.market_collector import get_all_sources
        
        # 获取政策数据
        policies = fetch_latest_policies()
        sources = get_all_sources()
        
        # 创建卡片式展示
        for idx, policy in enumerate(policies, 1):
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # 显示图标或图片
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 30px; 
                                border-radius: 10px; 
                                text-align: center;
                                color: white;
                                font-size: 24px;
                                font-weight: bold;">
                        📜<br>{idx}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    source_info = policy.get('source', {})
                    st.markdown(f"### {source_info.get('agency', '未知机构')}")
                    st.markdown(f"**发布时间:** {policy.get('fetched_at', 'N/A')}")
                    st.markdown(f"{policy.get('snippet', '暂无内容')}")
                    
                    # 显示相关数据源信息
                    related_source = next((s for s in sources if source_info.get('agency', '') in s.get('name', '')), None)
                    if related_source:
                        st.caption(f"数据可信度: {related_source.get('credibility', 0):.0%}")
                
                st.markdown("---")
        
        if not policies:
            st.info("暂无政策数据")
            
    except Exception as e:
        st.error(f"加载政策数据失败: {e}")


def render_system_overview():
    """渲染系统概览，数据实时更新"""
    st.header("📊 系统概览（实时数据）")
    
    # 自动刷新
    if st.button("🔄 刷新数据"):
        st.rerun()
    
    st.caption(f"最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 系统信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("主机名", socket.gethostname())
    
    with col2:
        st.metric("系统", platform.system())
    
    with col3:
        st.metric("平台", platform.platform()[:20])
    
    with col4:
        st.metric("当前时间", datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")
    
    # 数据统计
    st.markdown("### 📈 数据采集统计")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Amazon数据统计
        amazon_dir = "data/amazon"
        amazon_count = 0
        if os.path.exists(amazon_dir):
            files = [f for f in os.listdir(amazon_dir) if f.endswith('.json')]
            amazon_count = len(files)
            
            # 统计总商品数
            total_products = 0
            for file in files:
                try:
                    with open(os.path.join(amazon_dir, file), 'r') as f:
                        data = json.load(f)
                        items = data.get('items', data) if isinstance(data, dict) else data
                        total_products += len(items) if isinstance(items, list) else 0
                except:
                    pass
            
            st.metric("Amazon数据文件", amazon_count)
            st.metric("采集商品总数", f"{total_products:,}")
    
    with col2:
        # YouTube数据统计
        youtube_dir = "data/youtube"
        youtube_count = 0
        if os.path.exists(youtube_dir):
            youtube_count = len([f for f in os.listdir(youtube_dir) if f.endswith('.json')])
        
        st.metric("YouTube分析数", youtube_count)
        
        # 分析结果统计
        analysis_count = 0
        if os.path.exists("data"):
            analysis_count = len([f for f in os.listdir("data") if f.startswith("analysis_results_")])
        st.metric("智能分析结果", analysis_count)
    
    with col3:
        # 系统健康度
        try:
            from core.auto_crawler_iter.metrics_collector import MetricsCollector
            collector = MetricsCollector()
            metrics = collector.collect()
            
            total_items = metrics.get('items_total', 0)
            zero_pages = metrics.get('pages_zero', 0)
            
            if total_items + zero_pages > 0:
                success_rate = (total_items / (total_items + zero_pages)) * 100
                st.metric("爬虫成功率", f"{success_rate:.1f}%")
            else:
                st.metric("爬虫成功率", "N/A")
            
            st.metric("错误次数", metrics.get('errors_total', 0))
        except:
            st.metric("爬虫成功率", "未运行")
    
    st.markdown("---")
    
    # AI系统状态
    st.markdown("### 🤖 AI系统状态")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 学习记录
        try:
            from core.ai.memory_manager import get_recent_learning
            records = get_recent_learning()
            st.metric("AI学习记录", len(records) if records else 0)
        except:
            st.metric("AI学习记录", 0)
    
    with col2:
        # 迭代次数
        if os.path.exists("logs/evolution_history.jsonl"):
            try:
                with open("logs/evolution_history.jsonl", 'r') as f:
                    lines = f.readlines()
                st.metric("AI迭代次数", len(lines))
            except:
                st.metric("AI迭代次数", 0)
        else:
            st.metric("AI迭代次数", 0)
    
    with col3:
        # 补丁数量
        patch_count = 0
        if os.path.exists("sandbox/patches"):
            patch_count = len([f for f in os.listdir("sandbox/patches") if f.endswith('.patch')])
        st.metric("生成补丁数", patch_count)
    
    st.markdown("---")
    
    # 配置状态
    st.markdown("### ⚙️ 系统配置状态")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # API密钥配置
        st.markdown("**API密钥配置:**")
        
        if os.getenv("OPENAI_API_KEY"):
            st.success("✅ OpenAI API")
        else:
            st.warning("⚠️ OpenAI API 未配置")
        
        if os.getenv("YOUTUBE_API_KEY"):
            st.success("✅ YouTube API")
        else:
            st.warning("⚠️ YouTube API 未配置")
    
    with col2:
        # 数据源配置
        st.markdown("**数据源:**")
        
        try:
            from core.collectors.market_collector import get_all_sources
            sources = get_all_sources()
            st.success(f"✅ {len(sources)} 个权威数据源")
            
            # 自定义数据源
            custom_file = "config/custom_data_sources.json"
            if os.path.exists(custom_file):
                with open(custom_file, 'r') as f:
                    custom = json.load(f)
                st.info(f"ℹ️ {len(custom)} 个自定义数据源")
        except:
            st.warning("⚠️ 数据源未配置")


def render_log_and_settings():
    """渲染日志与设置模块，提供config.json的UI界面"""
    st.header("⚙️ 日志与设置")
    
    # 创建标签页
    tab1, tab2 = st.tabs(["📋 查看日志", "⚙️ 系统配置"])
    
    with tab1:
        st.markdown("### 📋 系统日志")
        
        # 选择日志文件
        log_files = []
        if os.path.exists("logs"):
            log_files.extend([f"logs/{f}" for f in os.listdir("logs") if f.endswith(('.log', '.jsonl'))])
        if os.path.exists("scraper.log"):
            log_files.append("scraper.log")
        
        if log_files:
            selected_log = st.selectbox("选择日志文件", log_files)
            
            # 行数控制
            num_lines = st.slider("显示行数", 10, 500, 100)
            
            if st.button("加载日志"):
                try:
                    with open(selected_log, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    
                    # 显示最后N行
                    st.text_area("日志内容", ''.join(lines[-num_lines:]), height=400)
                    
                    st.caption(f"文件: {selected_log} | 总行数: {len(lines)}")
                    
                except Exception as e:
                    st.error(f"读取日志失败: {e}")
        else:
            st.info("未找到日志文件")
    
    with tab2:
        st.markdown("### ⚙️ 系统配置管理")
        st.info("在此配置系统参数，包括调度、密钥、邮箱等")
        
        config_file = "config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                st.success("✅ 配置文件已加载")
                
                # 邮件配置
                st.markdown("#### 📧 邮件配置")
                
                email_config = config.get('email', {})
                
                with st.form("email_config"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        sender = st.text_input("发件人邮箱", value=email_config.get('sender', ''))
                        receiver = st.text_input("收件人邮箱", value=email_config.get('receiver', ''))
                        smtp_server = st.text_input("SMTP服务器", value=email_config.get('smtp_server', ''))
                    
                    with col2:
                        password = st.text_input("邮箱密码/授权码", value=email_config.get('password', ''), type="password")
                        smtp_port = st.number_input("SMTP端口", value=email_config.get('smtp_port', 465))
                    
                    if st.form_submit_button("保存邮件配置"):
                        config['email'] = {
                            'sender': sender,
                            'password': password,
                            'receiver': receiver,
                            'smtp_server': smtp_server,
                            'smtp_port': smtp_port
                        }
                        
                        with open(config_file, 'w', encoding='utf-8') as f:
                            json.dump(config, f, ensure_ascii=False, indent=2)
                        
                        st.success("✅ 邮件配置已保存")
                        st.rerun()
                
                st.markdown("---")
                
                # 调度配置
                st.markdown("#### ⏰ 调度配置")
                
                with st.form("schedule_config"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        report_time = st.text_input("报告发送时间", value=config.get('report_time', '08:00'))
                        poll_interval = st.number_input("数据轮询间隔(分钟)", value=config.get('poll_interval_minutes', 60))
                    
                    with col2:
                        evolution_interval = st.number_input("AI进化检查间隔(小时)", value=config.get('evolution_check_interval_hours', 2))
                        confidence_threshold = st.slider("置信度阈值", 0.0, 1.0, config.get('confidence_threshold', 0.7))
                    
                    if st.form_submit_button("保存调度配置"):
                        config['report_time'] = report_time
                        config['poll_interval_minutes'] = poll_interval
                        config['evolution_check_interval_hours'] = evolution_interval
                        config['confidence_threshold'] = confidence_threshold
                        
                        with open(config_file, 'w', encoding='utf-8') as f:
                            json.dump(config, f, ensure_ascii=False, indent=2)
                        
                        st.success("✅ 调度配置已保存")
                        st.rerun()
                
                st.markdown("---")
                
                # 数据源配置
                st.markdown("#### 📊 数据源配置")
                
                market_sources = config.get('market_sources', [])
                selected_sources = st.multiselect(
                    "启用的市场数据源",
                    ["amazon", "etsy", "tiktok", "youtube", "shopee", "ebay"],
                    default=market_sources
                )
                
                if st.button("保存数据源配置"):
                    config['market_sources'] = selected_sources
                    
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    
                    st.success("✅ 数据源配置已保存")
                    st.rerun()
                
                st.markdown("---")
                
                # 显示完整配置
                with st.expander("查看完整配置JSON"):
                    st.json(config)
                
            except Exception as e:
                st.error(f"加载配置失败: {e}")
        else:
            st.warning("配置文件不存在")
            
            if st.button("创建默认配置"):
                default_config = {
                    "email": {
                        "sender": "",
                        "password": "",
                        "receiver": "",
                        "smtp_server": "",
                        "smtp_port": 465
                    },
                    "report_time": "08:00",
                    "market_sources": ["amazon", "etsy", "tiktok", "youtube"],
                    "confidence_threshold": 0.7,
                    "poll_interval_minutes": 60,
                    "evolution_check_interval_hours": 2
                }
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
                
                st.success("✅ 默认配置已创建")
                st.rerun()


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
        render_authoritative_data_center()
    elif sub_menu == "数据来源追踪":
        render_sources()
    elif sub_menu == "YouTube":
        from ui.youtube_enhanced import render_youtube_query
        render_youtube_query()
    elif sub_menu == "TikTok":
        st.header("TikTok 趋势（占位）")
        st.write("后续通过 API 管理模块添加真实数据接口。")
    elif sub_menu == "Amazon采集工具":
        # 延迟导入，避免初始加载开销
        import ui.amazon_crawl_options
    elif sub_menu == "AI迭代系统":
        from ui.ai_iteration_system import render_ai_iteration_system
        render_ai_iteration_system()
    elif sub_menu == "API 管理":
        render_api_admin()
    elif sub_menu == "政策中心":
        render_policy_center()
    elif sub_menu == "系统概览":
        render_system_overview()
    elif sub_menu == "日志与设置":
        render_log_and_settings()

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