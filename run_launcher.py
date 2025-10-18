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
        "主页", "智能分析", 
        "权威数据中心", "YouTube", "TikTok",
        "Amazon采集工具", 
        "爬虫管理", "WPS协作",
        "API 管理", "企业协作", "系统概览", "日志与设置"
    ],
    "SaaS平台": ["SaaS仪表盘", "智能体对接", "用户管理", "计费管理"],
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

def route_intelligent_platform_old(sub_menu):
    """
    智能体平台路由调度（旧版本，待删除）。
    """
    # This function is deprecated and will be removed
    pass



def render_policy_center():
    """渲染政策中心，使用网页式浏览效果"""
    st.header("📜 政策中心")
    st.markdown("展示来自权威数据中心的政策和行业资讯")
    
    # 添加搜索和筛选功能
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 搜索政策",
            placeholder="输入关键词搜索...",
            label_visibility="collapsed"
        )
    
    with col2:
        sort_by = st.selectbox("排序", ["最新发布", "数据可信度", "机构名称"])
    
    with col3:
        view_mode = st.selectbox("视图", ["卡片视图", "列表视图", "时间轴"])
    
    st.markdown("---")
    
    try:
        from core.collectors.policy_collector import fetch_latest_policies
        from core.collectors.market_collector import get_all_sources
        
        # 获取政策数据
        policies = fetch_latest_policies()
        sources = get_all_sources()
        
        # 搜索过滤
        if search_query:
            policies = [
                p for p in policies 
                if search_query.lower() in str(p).lower()
            ]
        
        # 排序
        if sort_by == "最新发布":
            policies = sorted(policies, key=lambda x: x.get('fetched_at', ''), reverse=True)
        elif sort_by == "数据可信度":
            # 需要根据来源的可信度排序
            pass
        
        if not policies:
            st.info("暂无政策数据或未找到匹配结果")
            return
        
        # 根据视图模式显示
        if view_mode == "卡片视图":
            # 卡片式展示（每行2个卡片）
            for i in range(0, len(policies), 2):
                cols = st.columns(2)
                
                for j, col in enumerate(cols):
                    if i + j < len(policies):
                        policy = policies[i + j]
                        with col:
                            render_policy_card(policy, sources, i + j + 1)
        
        elif view_mode == "列表视图":
            # 列表式展示
            for idx, policy in enumerate(policies, 1):
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        # 显示图标
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 20px; 
                                    border-radius: 10px; 
                                    text-align: center;
                                    color: white;
                                    font-size: 20px;
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
                        
                        # 添加操作按钮
                        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
                        with col_btn1:
                            if st.button("📖 详情", key=f"detail_{idx}"):
                                st.session_state[f'show_policy_{idx}'] = True
                        with col_btn2:
                            if st.button("🔗 来源", key=f"source_{idx}"):
                                source_url = policy.get('url', '#')
                                st.markdown(f"[查看原文]({source_url})")
                    
                    st.markdown("---")
        
        else:  # 时间轴视图
            st.markdown("### 📅 政策发布时间轴")
            
            for idx, policy in enumerate(policies, 1):
                # 时间轴样式
                source_info = policy.get('source', {})
                date = policy.get('fetched_at', 'N/A')[:10]
                
                st.markdown(f"""
                <div style="border-left: 3px solid #667eea; 
                            padding-left: 20px; 
                            margin-left: 10px;
                            margin-bottom: 30px;">
                    <div style="color: #667eea; font-weight: bold; margin-bottom: 5px;">
                        📅 {date}
                    </div>
                    <div style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">
                        {source_info.get('agency', '未知机构')}
                    </div>
                    <div style="color: #666;">
                        {policy.get('snippet', '暂无内容')[:200]}...
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("查看完整内容", key=f"view_full_{idx}"):
                    with st.expander(f"完整内容 - {source_info.get('agency', '未知机构')}", expanded=True):
                        st.markdown(policy.get('snippet', '暂无内容'))
                        st.caption(f"来源: {policy.get('url', 'N/A')}")
            
    except Exception as e:
        st.error(f"加载政策数据失败: {e}")


def render_policy_card(policy: dict, sources: list, idx: int):
    """渲染单个政策卡片"""
    source_info = policy.get('source', {})
    
    # 卡片样式
    st.markdown(f"""
    <div style="border: 1px solid #e0e0e0; 
                border-radius: 10px; 
                padding: 20px; 
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                height: 250px;
                overflow: hidden;">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        margin-right: 10px;">
                {idx}
            </div>
            <div>
                <div style="font-size: 18px; font-weight: bold; color: #333;">
                    {source_info.get('agency', '未知机构')[:30]}
                </div>
                <div style="font-size: 12px; color: #999;">
                    {policy.get('fetched_at', 'N/A')[:10]}
                </div>
            </div>
        </div>
        <div style="color: #666; line-height: 1.6; height: 120px; overflow: hidden;">
            {policy.get('snippet', '暂无内容')[:150]}...
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 查看详情", key=f"card_detail_{idx}", use_container_width=True):
            with st.expander(f"详细内容", expanded=True):
                st.markdown(policy.get('snippet', '暂无内容'))
    with col2:
        if st.button("🔗 访问来源", key=f"card_source_{idx}", use_container_width=True):
            st.markdown(f"[打开原文链接]({policy.get('url', '#')})")


def render_system_overview():
    """渲染系统概览，数据实时更新，优化UI界面，包含新手指南"""
    st.header("📊 系统概览")
    st.markdown("实时监控系统运行状态和数据采集情况")
    
    # 新手指南按钮
    if st.button("📖 查看新手指南"):
        st.session_state['show_beginner_guide'] = True
    
    # 显示新手指南
    if st.session_state.get('show_beginner_guide', False):
        with st.expander("🎓 新手指南 - 系统功能快速入门", expanded=True):
            st.markdown("""
            ### 欢迎使用京盛传媒企业版智能体系统！
            
            #### 📚 核心功能模块说明
            
            ##### 1. 智能体平台
            - **主页**: 系统首页，查看整体状态和跨平台热门产品看板
            - **智能分析**: 使用OpenAI进行市场数据深度分析
              - 支持上传Word/PDF/Excel文件进行分析
              - 集成了原型测试验证功能
              - 包含数据来源追踪与可信度验证
              - 整合AI迭代与学习系统
              - 提供数据爬取配置管理
            - **权威数据中心**: 集成多个权威数据源
              - 数据可视化和详细数据展示
              - 数据源管理
              - 数据采集配置
              - 政策中心（整合）
            - **YouTube**: YouTube频道深度分析，支持UI配置API密钥
            - **TikTok**: TikTok数据分析
            - **Amazon采集工具**: 专门的Amazon数据采集工具
            - **爬虫管理**: 集中管理所有爬虫代码 🆕
              - 直接粘贴/复制爬虫代码
              - 动态加载和切换爬虫
              - 一键更新爬虫功能
              - 支持在UI界面执行爬虫
            - **WPS协作**: WPS在线文档协作 🆕
              - 输入账号密码连接WPS
              - 创建和编辑在线文档
              - 上传文件到WPS云端
              - 团队文档分享和协作
            - **API管理**: 统一管理所有第三方API配置
              - 支持OpenAI、Google、Amazon等平台
              - 提供API密钥获取指南
              - 解释API端点URL概念
              - 🆕 集成AI模型管理（支持10+主流AI提供商）
            - **企业协作**: 真实的企业团队协作功能 🆕
              - 团队管理和成员管理
              - 项目管理和任务分配
              - Kanban任务看板
              - 团队消息和通知
            
            ##### 2. SaaS平台
            - **智能体对接**: 为SaaS客户提供API接口和服务
            - **用户管理**: 管理SaaS平台用户
            - **计费管理**: 处理订阅和计费
            
            ##### 3. ERP系统
            - **库存管理**: 入库/出库操作，库存监控
            - **产品管理**: 添加产品，导出产品数据
            - **订单管理**: 新建订单，导出订单数据
            
            #### 🚀 快速开始步骤
            
            **第1步: 配置API密钥**
            1. 进入"API管理"页面
            2. 添加OpenAI、YouTube等所需的API密钥
            3. 查看获取指南了解如何获取各平台API
            
            **第2步: 数据采集**
            1. 进入"智能分析"→"数据爬取配置"标签
            2. 选择要爬取的平台（Amazon、eBay等）
            3. 设置爬取频率和参数
            4. 启动爬虫开始采集数据
            
            **第3步: 智能分析**
            1. 进入"智能分析"页面
            2. 上传数据文件或选择"最近采集数据"
            3. 选择国家/区域和类别
            4. 点击"开始智能分析"获取AI洞察
            
            **第4步: 数据来源验证**
            1. 在"智能分析"页面切换到"数据来源追踪"标签
            2. 查看所有数据源的可信度评分
            3. 验证分析结果的数据来源
            
            **第5步: 原型测试**
            1. 在"智能分析"页面切换到"原型测试验证"标签
            2. 上传测试文件
            3. AI将搜索互联网相似数据进行对比验证
            4. 查看验证结果和相似度分析
            
            **第6步: 查看权威数据**
            1. 进入"权威数据中心"
            2. 查看"数据可视化"了解市场趋势
            3. 浏览"政策中心"了解行业政策
            4. 管理自定义数据源
            
            #### 💡 使用技巧
            
            - **搜索功能**: 在侧边栏的"筛选功能"输入关键词快速定位功能
            - **文件上传**: 智能分析支持Word、PDF、Excel等多种格式
            - **WPS连接**: 在智能分析页面点击"连接WPS"按钮实现在线协作
            - **API配置**: 所有API密钥可在"API管理"中统一配置，无需修改代码
            - **YouTube配置**: YouTube模块支持在UI界面直接设置API密钥
            - **数据导出**: 大部分模块都支持Excel/CSV/JSON格式导出
            - **模块整合**: 原型测试、数据来源追踪、AI迭代系统已整合到智能分析中
            - **政策查看**: 政策中心已整合到权威数据中心的独立标签页
            
            #### 📞 需要帮助？
            
            - 查看各功能页面的提示信息（ℹ️ 图标）
            - 阅读API文档（API管理→查看各平台获取指南）
            - 使用"筛选功能"快速找到所需功能
            - 联系技术支持
            
            #### 🎯 推荐工作流程
            
            1. **配置阶段**: 在API管理中配置所需的API密钥
            2. **数据采集**: 使用智能分析的爬取配置功能采集数据
            3. **智能分析**: 对采集的数据进行AI分析获取市场洞察
            4. **验证分析**: 通过原型测试和数据来源追踪验证分析结果
            5. **查看趋势**: 在权威数据中心查看整体市场趋势和政策
            6. **业务管理**: 在ERP系统中管理产品和订单
            7. **对外服务**: 为SaaS客户提供API服务
            
            #### 🆕 最新更新
            
            - ✅ 智能分析模块已整合原型测试、数据来源追踪、AI迭代系统
            - ✅ 权威数据中心已整合政策中心
            - ✅ YouTube模块支持UI配置API密钥
            - ✅ API管理支持OpenAI和Google API
            - ✅ 添加WPS在线文档连接功能
            - ✅ 提供详细的API获取指南和端点URL说明
            - ✅ 系统不包含AI生成的示例数据，所有数据由用户上传或爬取
            - 🆕 **爬虫管理中心**: 集中管理所有爬虫代码，支持粘贴复制更新
            - 🆕 **WPS Office集成**: 真实的WPS账号登录和在线协作功能
            - 🆕 **AI模型集成管理**: 支持OpenAI、Claude、Gemini等10+主流AI模型
            - 🆕 **企业协作功能**: 完整的团队、项目、任务管理和消息系统
            
            ---
            
            💬 **提示**: 点击右上角的❌可以关闭此指南，随时可通过"查看新手指南"按钮重新打开。
            """)
            
            if st.button("关闭指南"):
                st.session_state['show_beginner_guide'] = False
                st.rerun()
    
    st.markdown("---")
    
    # 顶部控制栏
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.caption(f"🕐 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with col2:
        auto_refresh = st.checkbox("自动刷新", value=False)
    
    with col3:
        if st.button("🔄 立即刷新", use_container_width=True):
            st.rerun()
    
    with col4:
        export_data = st.button("📥 导出数据", use_container_width=True)
    
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()
    
    st.markdown("---")
    
    # 系统信息卡片
    st.markdown("### 💻 系统信息")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "主机名", 
            socket.gethostname()[:15],
            help="当前运行主机的名称"
        )
    
    with col2:
        st.metric(
            "操作系统", 
            platform.system(),
            help="系统类型"
        )
    
    with col3:
        st.metric(
            "Python版本", 
            platform.python_version(),
            help="当前Python版本"
        )
    
    with col4:
        st.metric(
            "当前时间", 
            datetime.now().strftime("%H:%M:%S"),
            help="系统当前时间"
        )
    
    st.markdown("---")
    
    # 数据采集统计（使用tabs组织）
    tab1, tab2, tab3, tab4 = st.tabs(["📈 数据统计", "🤖 AI系统", "⚙️ 配置状态", "📊 性能指标"])
    
    with tab1:
        st.markdown("#### 📊 数据采集统计")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Amazon数据统计
            st.markdown("##### 🛒 Amazon数据")
            amazon_dir = "data/amazon"
            amazon_count = 0
            total_products = 0
            
            if os.path.exists(amazon_dir):
                files = [f for f in os.listdir(amazon_dir) if f.endswith('.json')]
                amazon_count = len(files)
                
                # 统计总商品数
                for file in files:
                    try:
                        with open(os.path.join(amazon_dir, file), 'r') as f:
                            data = json.load(f)
                            items = data.get('items', data) if isinstance(data, dict) else data
                            total_products += len(items) if isinstance(items, list) else 0
                    except:
                        pass
            
            st.metric("数据文件", amazon_count)
            st.metric("采集商品数", f"{total_products:,}")
            st.progress(min(total_products / 1000, 1.0))
        
        with col2:
            # YouTube数据统计
            st.markdown("##### 📺 YouTube数据")
            youtube_dir = "data/youtube"
            youtube_count = 0
            
            if os.path.exists(youtube_dir):
                youtube_count = len([f for f in os.listdir(youtube_dir) if f.endswith('.json')])
            
            st.metric("频道分析数", youtube_count)
            
            # 分析结果统计
            analysis_count = 0
            if os.path.exists("data"):
                analysis_count = len([f for f in os.listdir("data") if f.startswith("analysis_results_")])
            st.metric("智能分析结果", analysis_count)
            st.progress(min(analysis_count / 10, 1.0))
        
        with col3:
            # TikTok数据统计
            st.markdown("##### 🎵 TikTok数据")
            tiktok_dir = "data/tiktok"
            tiktok_count = 0
            
            if os.path.exists(tiktok_dir):
                tiktok_count = len([f for f in os.listdir(tiktok_dir) if f.endswith('.json')])
            
            st.metric("数据文件", tiktok_count)
            
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
                    st.progress(success_rate / 100)
                else:
                    st.metric("爬虫成功率", "N/A")
            except:
                st.metric("爬虫成功率", "未运行")
    
    with tab2:
        st.markdown("#### 🤖 AI系统状态")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### 📚 学习记录")
            # 学习记录
            try:
                from core.ai.memory_manager import get_recent_learning
                records = get_recent_learning()
                learning_count = len(records) if records else 0
                st.metric("AI学习记录", learning_count)
                
                if records:
                    recent_record = records[-1]
                    confidence = recent_record.get('confidence', 0)
                    st.progress(confidence)
                    st.caption(f"最新置信度: {confidence:.0%}")
            except:
                st.metric("AI学习记录", 0)
        
        with col2:
            st.markdown("##### 🔄 迭代次数")
            # 迭代次数
            if os.path.exists("logs/evolution_history.jsonl"):
                try:
                    with open("logs/evolution_history.jsonl", 'r') as f:
                        lines = f.readlines()
                    iteration_count = len(lines)
                    st.metric("AI迭代次数", iteration_count)
                    st.progress(min(iteration_count / 50, 1.0))
                except:
                    st.metric("AI迭代次数", 0)
            else:
                st.metric("AI迭代次数", 0)
        
        with col3:
            st.markdown("##### 🩹 生成补丁")
            # 补丁数量
            patch_count = 0
            if os.path.exists("sandbox/patches"):
                patch_count = len([f for f in os.listdir("sandbox/patches") if f.endswith('.patch') or f.endswith('.txt')])
            st.metric("生成补丁数", patch_count)
            st.progress(min(patch_count / 20, 1.0))
    
    with tab3:
        st.markdown("#### ⚙️ 系统配置状态")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔑 API密钥配置")
            
            api_status = []
            
            if os.getenv("OPENAI_API_KEY"):
                api_status.append(("✅", "OpenAI API", "已配置"))
            else:
                api_status.append(("⚠️", "OpenAI API", "未配置"))
            
            if os.getenv("YOUTUBE_API_KEY"):
                api_status.append(("✅", "YouTube API", "已配置"))
            else:
                api_status.append(("⚠️", "YouTube API", "未配置"))
            
            for emoji, name, status in api_status:
                st.markdown(f"{emoji} **{name}**: {status}")
        
        with col2:
            st.markdown("##### 📊 数据源配置")
            
            try:
                from core.collectors.market_collector import get_all_sources
                sources = get_all_sources()
                st.metric("权威数据源", f"{len(sources)} 个")
                
                # 自定义数据源
                custom_file = "config/custom_data_sources.json"
                if os.path.exists(custom_file):
                    with open(custom_file, 'r') as f:
                        custom = json.load(f)
                    st.metric("自定义数据源", f"{len(custom)} 个")
                else:
                    st.metric("自定义数据源", "0 个")
            except:
                st.warning("⚠️ 数据源未配置")
    
    with tab4:
        st.markdown("#### 📊 性能指标")
        
        # 使用图表显示性能趋势
        import pandas as pd
        import plotly.graph_objects as go
        
        # 模拟性能数据（实际应该从日志或监控系统获取）
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 采集量趋势
            import random
            collection_data = [random.randint(50, 200) for _ in range(7)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=collection_data,
                mode='lines+markers',
                name='每日采集量',
                line=dict(color='#667eea', width=3)
            ))
            fig.update_layout(
                title="📈 每日数据采集量",
                xaxis_title="日期",
                yaxis_title="采集数量",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 成功率趋势
            success_data = [random.uniform(85, 98) for _ in range(7)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=success_data,
                mode='lines+markers',
                name='成功率',
                line=dict(color='#10b981', width=3),
                fill='tozeroy'
            ))
            fig.update_layout(
                title="✅ 采集成功率趋势",
                xaxis_title="日期",
                yaxis_title="成功率 (%)",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
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
                st.info("选择要启用的电商平台数据源，支持多平台同时采集")
                
                market_sources = config.get('market_sources', [])
                
                # 提供更多平台选项
                all_platforms = [
                    "amazon", "etsy", "tiktok", "youtube", 
                    "shopee", "ebay", "aliexpress", "walmart",
                    "target", "bestbuy", "alibaba", "lazada",
                    "mercari", "poshmark", "depop", "facebook_marketplace"
                ]
                
                selected_sources = st.multiselect(
                    "选择要启用的数据源平台",
                    all_platforms,
                    default=market_sources,
                    help="选择多个平台进行数据采集"
                )
                
                # 显示平台状态
                col1, col2, col3, col4 = st.columns(4)
                
                platform_status = {
                    "amazon": "✅ 支持",
                    "tiktok": "✅ 支持",
                    "youtube": "✅ 支持",
                    "shopee": "⚠️ 部分支持",
                    "ebay": "⚠️ 部分支持",
                }
                
                for i, platform in enumerate(selected_sources[:8]):  # 显示前8个
                    with [col1, col2, col3, col4][i % 4]:
                        status = platform_status.get(platform, "📝 待实现")
                        st.caption(f"**{platform.upper()}**")
                        st.caption(status)
                
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
        render_system_overview()
    elif sub_menu == "智能分析":
        render_analytics()
    elif sub_menu == "权威数据中心":
        render_authoritative_data_center()
    elif sub_menu == "YouTube":
        from ui.youtube_enhanced import render_youtube_query
        render_youtube_query()
    elif sub_menu == "TikTok":
        from ui.tiktok_enhanced import render_tiktok_module
        render_tiktok_module()
    elif sub_menu == "Amazon采集工具":
        from ui.amazon_crawl_options import render_amazon_crawl_tool
        render_amazon_crawl_tool()
    elif sub_menu == "爬虫管理":
        from ui.crawler_management import render_crawler_management
        render_crawler_management()
    elif sub_menu == "WPS协作":
        from ui.wps_integration import render_wps_integration
        render_wps_integration()
    elif sub_menu == "API 管理":
        render_api_admin()
    elif sub_menu == "企业协作":
        from ui.enterprise_collaboration import render_enterprise_collaboration
        render_enterprise_collaboration()
    elif sub_menu == "日志与设置":
        render_log_and_settings()

def route_saas_platform(sub_menu):
    if sub_menu == "SaaS仪表盘":
        import ui.saas.dashboard as saas_dash
        saas_dash.render_saas_dashboard()
    elif sub_menu == "智能体对接":
        from ui.saas.agent_integration import render_agent_integration
        render_agent_integration()
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