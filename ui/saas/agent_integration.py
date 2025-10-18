"""
SaaS平台智能体系统对接模块
用于为SaaS客户提供智能体服务
"""

import streamlit as st
import json
import os
import secrets
import hashlib
from datetime import datetime, timedelta
import pandas as pd


def render_agent_integration():
    """渲染SaaS平台智能体对接页面"""
    st.title("🤖 智能体系统对接")
    st.markdown("为SaaS客户提供强大的智能体服务和API集成")
    
    # 顶部统计信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("已对接客户", "45", delta="8")
    with col2:
        st.metric("API调用量", "12.5K", delta="2.3K")
    with col3:
        st.metric("服务可用性", "99.8%", delta="0.1%")
    with col4:
        st.metric("平均响应时间", "156ms", delta="-12ms")
    
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🔌 API配置", "📊 服务监控", "🎯 智能推荐", "📚 使用文档"])
    
    with tab1:
        render_api_configuration()
    
    with tab2:
        render_service_monitoring()
    
    with tab3:
        render_intelligent_recommendations()
    
    with tab4:
        render_api_documentation()


def generate_api_key():
    """生成安全的API密钥"""
    # 生成随机字节
    random_bytes = secrets.token_bytes(32)
    # 转换为十六进制字符串
    api_key = "sk-" + hashlib.sha256(random_bytes).hexdigest()
    return api_key

def get_current_api_key():
    """从配置文件获取当前API密钥"""
    config_path = "config/saas/agent_integration.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if "api_key" in config:
                    return config["api_key"]
        except Exception as e:
            st.error(f"读取配置文件时出错: {e}")
    return "sk-xxxxxxxxxxxxxxxxxxxxxx"  # 默认占位符

def save_api_key(api_key):
    """保存API密钥到配置文件"""
    config_path = "config/saas/agent_integration.json"
    config = {}
    
    # 如果文件已存在，读取现有配置
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            st.error(f"读取现有配置时出错: {e}")
    
    # 更新API密钥和生成时间
    config["api_key"] = api_key
    config["api_key_generated_at"] = datetime.now().isoformat()
    
    # 保存配置
    os.makedirs("config/saas", exist_ok=True)
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存API密钥时出错: {e}")
        return False

def render_api_configuration():
    """渲染API配置界面"""
    st.subheader("API配置与管理")
    
    # API密钥管理
    st.markdown("### 🔑 API密钥管理")
    
    # 获取当前API密钥
    api_key = get_current_api_key()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        api_key_display = st.text_input(
            "您的API密钥",
            value=api_key,
            type="password",
            disabled=True
        )
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 重新生成", use_container_width=True):
            # 生成新的API密钥
            new_api_key = generate_api_key()
            if save_api_key(new_api_key):
                # 更新当前显示的API密钥
                api_key = new_api_key
                st.success("✅ 新的API密钥已生成")
                # 使用刷新按钮提示用户
                st.info("请刷新页面以查看更新后的API密钥")
            else:
                st.error("❌ 生成API密钥失败")
        if st.button("📋 复制", use_container_width=True):
            st.session_state["copied_api_key"] = api_key
            st.info("API密钥已复制到剪贴板")
    
    # 显示API密钥有效期信息
    config_path = "config/saas/agent_integration.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if "api_key_generated_at" in config:
                    generated_at = datetime.fromisoformat(config["api_key_generated_at"])
                    # 假设API密钥有效期为30天
                    expires_at = generated_at + timedelta(days=30)
                    days_left = (expires_at - datetime.now()).days
                    
                    if days_left > 0:
                        st.info(f"⚠️ 此API密钥将于 {expires_at.strftime('%Y-%m-%d')} 过期（剩余 {days_left} 天）")
                    else:
                        st.warning(f"🚨 此API密钥已过期，请重新生成")
        except Exception as e:
            pass
    
    st.markdown("---")
    
    # 服务配置
    st.markdown("### ⚙️ 服务配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 智能体服务选择")
        services = st.multiselect(
            "选择要启用的服务",
            [
                "智能分析",
                "数据采集",
                "原型测试",
                "异常检测",
                "市场洞察",
                "数据可视化",
                "自动报告生成"
            ],
            default=["智能分析", "数据采集", "市场洞察"]
        )
        
        st.markdown("#### 请求限制")
        rate_limit = st.slider("每分钟请求数", 10, 1000, 100, 10)
        daily_quota = st.number_input("每日配额", min_value=1000, value=10000, step=1000)
    
    with col2:
        st.markdown("#### 数据源配置")
        data_sources = st.multiselect(
            "可访问的数据源",
            [
                "Amazon数据",
                "权威数据中心",
                "市场趋势数据",
                "政策数据",
                "YouTube统计",
                "TikTok数据"
            ],
            default=["Amazon数据", "权威数据中心"]
        )
        
        st.markdown("#### 回调配置")
        webhook_url = st.text_input("Webhook URL (可选)", placeholder="https://your-domain.com/webhook")
        enable_notifications = st.checkbox("启用通知", value=True)
    
    st.markdown("---")
    
    # API端点
    st.markdown("### 🌐 API端点")
    
    endpoints = [
        {
            "method": "POST",
            "endpoint": "/api/v1/analyze",
            "description": "智能分析接口",
            "status": "✅ 活跃"
        },
        {
            "method": "GET",
            "endpoint": "/api/v1/data/collect",
            "description": "数据采集接口",
            "status": "✅ 活跃"
        },
        {
            "method": "POST",
            "endpoint": "/api/v1/test/prototype",
            "description": "原型测试接口",
            "status": "✅ 活跃"
        },
        {
            "method": "GET",
            "endpoint": "/api/v1/insights/market",
            "description": "市场洞察接口",
            "status": "✅ 活跃"
        }
    ]
    
    df = pd.DataFrame(endpoints)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 保存配置
    if st.button("💾 保存配置", type="primary", use_container_width=False):
        # 获取当前配置（保留API密钥信息）
        config_path = "config/saas/agent_integration.json"
        config = {}
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                st.error(f"读取现有配置时出错: {e}")
        
        # 更新配置
        config.update({
            "services": services,
            "rate_limit": rate_limit,
            "daily_quota": daily_quota,
            "data_sources": data_sources,
            "webhook_url": webhook_url,
            "enable_notifications": enable_notifications,
            "updated_at": datetime.now().isoformat()
        })
        
        os.makedirs("config/saas", exist_ok=True)
        with open("config/saas/agent_integration.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        st.success("✅ 配置已保存！")
    



def render_service_monitoring():
    """渲染服务监控界面"""
    st.subheader("服务监控与统计")
    
    # 实时状态
    st.markdown("### 📈 实时服务状态")
    
    # 提供输入框让用户填写真实数据
    with st.expander("🔧 编辑监控数据", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            online_users = st.number_input("当前在线用户", min_value=0, value=128, key="online_users")
            online_users_delta = st.number_input("变化量", value=15, key="online_users_delta")
        with col2:
            active_connections = st.number_input("活跃连接数", min_value=0, value=45, key="active_connections")
            active_connections_delta = st.number_input("变化量", value=3, key="active_connections_delta")
        with col3:
            queued_requests = st.number_input("队列中请求", min_value=0, value=12, key="queued_requests")
            queued_requests_delta = st.number_input("变化量", value=-8, key="queued_requests_delta")
    
    # 显示用户输入的数据
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("当前在线用户", online_users, delta=online_users_delta)
    with col2:
        st.metric("活跃连接数", active_connections, delta=active_connections_delta)
    with col3:
        st.metric("队列中请求", queued_requests, delta=queued_requests_delta)
    
    st.markdown("---")
    
    # API调用统计
    st.markdown("### 📊 API调用统计")
    
    # 提供选项让用户选择使用模拟数据或真实数据
    use_real_data = st.checkbox("使用真实数据", value=False)
    
    if use_real_data:
        # 让用户上传CSV文件或手动输入数据
        uploaded_file = st.file_uploader("上传API调用统计CSV文件", type=["csv"])
        if uploaded_file is not None:
            try:
                api_calls_data = pd.read_csv(uploaded_file)
                st.success("数据已成功上传")
                # 显示上传的数据
                st.dataframe(api_calls_data)
                # 绘制图表
                if "日期" in api_calls_data.columns:
                    st.line_chart(api_calls_data.set_index("日期"))
            except Exception as e:
                st.error(f"上传文件出错: {e}")
    else:
        # 使用模拟数据
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        api_calls_data = pd.DataFrame({
            "日期": dates.strftime('%Y-%m-%d'),
            "智能分析": [100 + i * 5 for i in range(30)],
            "数据采集": [80 + i * 3 for i in range(30)],
            "原型测试": [50 + i * 2 for i in range(30)],
            "异常检测": [40 + i * 1 for i in range(30)]
        })
        st.line_chart(api_calls_data.set_index("日期"))
    
    st.markdown("---")
    
    # 错误监控
    st.markdown("### ⚠️ 错误监控")
    
    # 提供选项让用户添加/编辑错误记录
    with st.expander("🔧 添加/编辑错误记录", expanded=False):
        num_errors = st.number_input("错误记录数量", min_value=1, max_value=10, value=3)
        errors = []
        for i in range(num_errors):
            st.subheader(f"错误记录 {i+1}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                time = st.text_input(f"时间 {i+1}", value=f"2025-10-18 {13+i}:{30+i*15%60:02d}", key=f"error_time_{i}")
            with col2:
                error_type = st.selectbox(f"类型 {i+1}", ["Rate Limit", "Timeout", "Auth Error", "Server Error", "Client Error"], key=f"error_type_{i}")
            with col3:
                api = st.text_input(f"API {i+1}", value=f"/api/v1/{['analyze', 'collect', 'test', 'insights', 'data'][i%5]}", key=f"error_api_{i}")
            with col4:
                status = st.selectbox(f"状态 {i+1}", ["已解决", "处理中", "未解决"], key=f"error_status_{i}")
            errors.append({"时间": time, "类型": error_type, "API": api, "状态": status})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 最近错误")
        st.dataframe(pd.DataFrame(errors), use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 错误率趋势")
        # 允许用户编辑错误率数据
        # 初始化默认数据
        error_rate = pd.DataFrame({
            "时间": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
            "错误率%": [0.5, 0.3, 0.8, 1.2, 0.6, 0.4]
        })
        
        # 允许用户编辑错误率数据
        with st.expander("编辑错误率数据", expanded=False):
            error_times = st.text_input("时间点（逗号分隔）", value="00:00,04:00,08:00,12:00,16:00,20:00")
            error_rates = st.text_input("错误率%（逗号分隔）", value="0.5,0.3,0.8,1.2,0.6,0.4")
            
            try:
                times_list = [t.strip() for t in error_times.split(",")]
                rates_list = [float(r.strip()) for r in error_rates.split(",")]
                if len(times_list) == len(rates_list):
                    error_rate = pd.DataFrame({"时间": times_list, "错误率%": rates_list})
                else:
                    st.error("时间点和错误率数量不匹配")
                    # 使用默认数据
                    error_rate = pd.DataFrame({
                        "时间": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
                        "错误率%": [0.5, 0.3, 0.8, 1.2, 0.6, 0.4]
                    })
            except Exception as e:
                st.error(f"数据格式错误: {e}")
                # 使用默认数据
                error_rate = pd.DataFrame({
                    "时间": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
                    "错误率%": [0.5, 0.3, 0.8, 1.2, 0.6, 0.4]
                })
        
        st.bar_chart(error_rate.set_index("时间"))


def render_intelligent_recommendations():
    """渲染智能推荐界面"""
    st.subheader("🎯 智能推荐功能")
    st.info("基于用户行为和数据分析，为SaaS客户提供个性化推荐")
    
    # 推荐设置
    st.markdown("### ⚙️ 推荐设置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_recommendations = st.checkbox("启用智能推荐", value=True)
        recommendation_frequency = st.selectbox(
            "推荐频率",
            ["实时", "每小时", "每日", "每周"]
        )
        min_confidence = st.slider("最低置信度", 0.0, 1.0, 0.7, 0.05)
    
    with col2:
        recommendation_types = st.multiselect(
            "推荐类型",
            [
                "产品推荐",
                "市场机会",
                "优化建议",
                "风险预警",
                "趋势预测"
            ],
            default=["产品推荐", "市场机会", "优化建议"]
        )
        max_recommendations = st.number_input("最大推荐数", 1, 50, 10)
    
    st.markdown("---")
    
    # 允许用户添加自定义推荐
    with st.expander("🔧 管理推荐内容", expanded=False):
        use_custom_recommendations = st.checkbox("使用自定义推荐", value=False)
        recommendations = []
        
        if use_custom_recommendations:
            num_recommendations = st.number_input("推荐数量", min_value=1, max_value=20, value=5)
            
            for i in range(num_recommendations):
                st.subheader(f"推荐 {i+1}")
                rec_type = st.selectbox(
                    f"类型 {i+1}",
                    ["产品推荐", "市场机会", "优化建议", "风险预警", "趋势预测"],
                    key=f"rec_type_{i}"
                )
                title = st.text_input(f"标题 {i+1}", value=f"推荐标题 {i+1}", key=f"rec_title_{i}")
                description = st.text_area(f"描述 {i+1}", value=f"这是推荐内容的详细描述 {i+1}", key=f"rec_desc_{i}")
                confidence = st.slider(f"置信度 {i+1}", 0.0, 1.0, 0.7 + i*0.03, 0.01, key=f"rec_conf_{i}")
                priority = st.selectbox(f"优先级 {i+1}", ["高", "中", "低"], key=f"rec_prio_{i}")
                
                recommendations.append({
                    "类型": rec_type,
                    "标题": title,
                    "描述": description,
                    "置信度": confidence,
                    "优先级": priority
                })
        else:
            # 默认推荐数据
            recommendations = [
                {
                    "类型": "产品推荐",
                    "标题": "高潜力产品类别",
                    "描述": "根据市场趋势分析，建议关注'智能家居'类别，预计增长率32%",
                    "置信度": 0.89,
                    "优先级": "高"
                },
                {
                    "类型": "市场机会",
                    "标题": "新兴市场机会",
                    "描述": "东南亚市场电商增长迅速，建议考虑拓展业务",
                    "置信度": 0.85,
                    "优先级": "高"
                },
                {
                    "类型": "优化建议",
                    "标题": "定价策略优化",
                    "描述": "分析显示价格区间在$50-$100的产品转化率最高",
                    "置信度": 0.82,
                    "优先级": "中"
                },
                {
                    "类型": "风险预警",
                    "标题": "库存预警",
                    "描述": "预测下月热门产品可能出现库存不足",
                    "置信度": 0.78,
                    "优先级": "中"
                },
                {
                    "类型": "趋势预测",
                    "标题": "消费趋势变化",
                    "描述": "环保产品需求预计在未来3个月增长25%",
                    "置信度": 0.75,
                    "优先级": "低"
                }
            ]
        
        # 继续处理推荐数据
        # 处理推荐数据的后续逻辑
    
    # 推荐展示区域
    if enable_recommendations:
        st.markdown("### 💡 当前推荐")
        
        for idx, rec in enumerate(recommendations[:max_recommendations], 1):
            if rec["置信度"] >= min_confidence and rec["类型"] in recommendation_types:
                with st.expander(f"{idx}. {rec['标题']} ({rec['类型']})", expanded=(idx <= 2)):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(rec["描述"])
                    
                    with col2:
                        st.metric("置信度", f"{rec['置信度']:.0%}")
                    
                    with col3:
                        priority_color = {"高": "🔴", "中": "🟡", "低": "🟢"}
                        st.metric("优先级", f"{priority_color[rec['优先级']]} {rec['优先级']}")
                    
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
                    with col_btn1:
                        st.button("✅ 采纳", key=f"accept_{idx}")
                    with col_btn2:
                        st.button("❌ 忽略", key=f"ignore_{idx}")


def render_api_documentation():
    """渲染API文档"""
    st.subheader("📚 API使用文档")
    
    # 快速开始
    st.markdown("### 🚀 快速开始")
    
    st.code("""
# 安装SDK
pip install saas-agent-sdk

# Python示例
from saas_agent import AgentClient

# 初始化客户端
client = AgentClient(api_key="your-api-key")

# 调用智能分析
result = client.analyze({
    "data_source": "amazon",
    "category": "electronics",
    "analysis_type": "market_insights"
})

print(result)
    """, language="python")
    
    st.markdown("---")
    
    # API端点详细说明
    st.markdown("### 📖 API端点详细说明")
    
    with st.expander("POST /api/v1/analyze - 智能分析", expanded=True):
        st.markdown("**描述:** 对指定数据进行智能分析，返回深度洞察")
        
        st.markdown("**请求示例:**")
        st.code("""
{
    "data_source": "amazon",
    "category": "电子产品",
    "country": "中国",
    "analysis_type": "market_insights"
}
        """, language="json")
        
        st.markdown("**响应示例:**")
        st.code("""
{
    "status": "success",
    "analysis": {
        "market_size": 1500000000,
        "growth_rate": 15.5,
        "top_brands": ["Apple", "Samsung", "Huawei"],
        "insights": "..."
    }
}
        """, language="json")
    
    with st.expander("GET /api/v1/data/collect - 数据采集"):
        st.markdown("**描述:** 启动数据采集任务")
        
        st.markdown("**请求参数:**")
        st.markdown("- `source`: 数据源类型 (amazon, shopee, etc.)")
        st.markdown("- `url`: 目标URL")
        st.markdown("- `max_items`: 最大采集数量")
        
        st.markdown("**响应示例:**")
        st.code("""
{
    "status": "success",
    "task_id": "task_123456",
    "estimated_time": "5 minutes"
}
        """, language="json")
    
    with st.expander("POST /api/v1/test/prototype - 原型测试"):
        st.markdown("**描述:** 对上传的文件进行原型测试和验证")
        
        st.markdown("**请求方式:** multipart/form-data")
        st.markdown("**参数:**")
        st.markdown("- `file`: 上传的文件")
        st.markdown("- `test_type`: 测试类型")
        
        st.markdown("**响应示例:**")
        st.code("""
{
    "status": "success",
    "test_results": {
        "data_quality": 0.89,
        "consistency": 0.92,
        "similar_sources": [...]
    }
}
        """, language="json")
    
    st.markdown("---")
    
    # 错误代码
    st.markdown("### ⚠️ 错误代码说明")
    
    error_codes = pd.DataFrame([
        {"代码": 400, "说明": "请求参数错误", "处理": "检查请求参数格式"},
        {"代码": 401, "说明": "未授权/API密钥无效", "处理": "验证API密钥"},
        {"代码": 403, "说明": "访问被拒绝", "处理": "检查权限配置"},
        {"代码": 429, "说明": "请求频率超限", "处理": "降低请求频率或升级配额"},
        {"代码": 500, "说明": "服务器内部错误", "处理": "联系技术支持"}
    ])
    
    st.dataframe(error_codes, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # SDK下载
    st.markdown("### 📦 SDK与工具下载")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Python SDK")
        st.markdown("版本: v1.2.3")
        st.button("📥 下载 Python SDK", use_container_width=True)
    
    with col2:
        st.markdown("#### JavaScript SDK")
        st.markdown("版本: v1.1.5")
        st.button("📥 下载 JS SDK", use_container_width=True)
    
    with col3:
        st.markdown("#### Postman Collection")
        st.markdown("最新版本")
        st.button("📥 下载 Collection", use_container_width=True)
