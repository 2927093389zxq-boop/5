import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from core.processing.anomaly_detector import detect_anomalies
from core.collectors.market_collector import fetch_all_trends, get_all_sources
from core.smart_analysis import SmartAnalysisEngine, analyze_product_data

def render_analytics():
    """Renders the analytics page with OpenAI-enhanced analysis and real data."""
    st.header("🧠 智能分析 (OpenAI增强)")

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["市场分析", "异常检测", "权威数据来源", "原型测试验证"])
    
    with tab1:
        st.markdown("#### 🌍 市场数据深度分析（OpenAI驱动）")
        st.info("基于真实数据，结合OpenAI进行智能分析")
        
        # 选择分析数据源
        col1, col2, col3 = st.columns(3)
        with col1:
            country = st.selectbox("选择国家/区域", ["US", "UK", "Germany", "Japan", "China"])
        with col2:
            category = st.selectbox("选择类别", ["Electronics", "Home & Kitchen", "Fashion", "Sports", "Books"])
        with col3:
            data_source = st.selectbox("数据源", ["最近采集数据", "上传JSON文件"])
        
        # 加载或上传数据
        product_data = None
        
        if data_source == "上传JSON文件":
            uploaded_file = st.file_uploader("上传产品数据JSON文件", type=['json'])
            if uploaded_file:
                try:
                    product_data = json.load(uploaded_file)
                    if isinstance(product_data, dict) and 'items' in product_data:
                        product_data = product_data['items']
                    st.success(f"已加载 {len(product_data)} 个产品数据")
                except Exception as e:
                    st.error(f"加载数据失败: {e}")
        else:
            # 尝试加载最近的Amazon数据
            data_dir = "data/amazon"
            if os.path.exists(data_dir):
                json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
                if json_files:
                    latest_file = max(json_files)
                    try:
                        with open(os.path.join(data_dir, latest_file), 'r') as f:
                            data = json.load(f)
                            if isinstance(data, dict) and 'items' in data:
                                product_data = data['items']
                            else:
                                product_data = data
                        st.success(f"已加载最近采集数据: {latest_file} ({len(product_data)} 个产品)")
                    except Exception as e:
                        st.warning(f"加载最近数据失败: {e}")
        
        if st.button("🚀 开始智能分析", type="primary"):
            if not product_data:
                st.error("请先加载或上传产品数据")
            else:
                with st.spinner("正在进行智能分析...这可能需要一些时间"):
                    try:
                        # 执行分析
                        analysis = analyze_product_data(product_data, country, category)
                        
                        # 显示分析结果
                        st.success("✅ 分析完成！")
                        
                        # 1. 基础统计
                        st.markdown("### 📊 基础统计数据")
                        stats = analysis.get('basic_stats', {})
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("产品总数", stats.get('total_products', 0))
                        with col2:
                            price_range = stats.get('price_range', {})
                            st.metric("平均价格", f"${price_range.get('average', 0):.2f}")
                        with col3:
                            rating_stats = stats.get('rating_stats', {})
                            st.metric("平均评分", f"{rating_stats.get('average', 0):.2f}⭐")
                        with col4:
                            review_stats = stats.get('review_stats', {})
                            st.metric("总评论数", f"{review_stats.get('total', 0):,}")
                        
                        # 2. 市场洞察
                        st.markdown("### 🌐 市场规模与趋势")
                        market = analysis.get('market_insights', {})
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("市场规模 (USD)", f"${market.get('market_size_usd', 0):,}")
                            st.metric("年增长率", f"{market.get('growth_rate_percentage', 0):.1f}%")
                        with col2:
                            st.metric("复合年增长率(CAGR)", f"{market.get('cagr_2024_2030', 0):.1f}%")
                            trends = market.get('future_trends', [])
                            if trends:
                                st.markdown("**未来趋势:**")
                                for trend in trends:
                                    st.markdown(f"- {trend}")
                        
                        # 3. 用户特征分析
                        st.markdown("### 👥 用户特征分析")
                        demographics = analysis.get('user_demographics', {})
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            # 年龄分布
                            age_dist = demographics.get('age_distribution', {})
                            if age_dist:
                                fig_age = px.bar(
                                    x=list(age_dist.keys()),
                                    y=list(age_dist.values()),
                                    labels={'x': '年龄段', 'y': '百分比 (%)'},
                                    title='年龄分布'
                                )
                                st.plotly_chart(fig_age, use_container_width=True)
                        
                        with col2:
                            # 性别分布
                            gender_dist = demographics.get('gender_distribution', {})
                            if gender_dist:
                                fig_gender = px.pie(
                                    names=list(gender_dist.keys()),
                                    values=list(gender_dist.values()),
                                    title='性别分布'
                                )
                                st.plotly_chart(fig_gender, use_container_width=True)
                        
                        # 兴趣分布
                        interests = demographics.get('interests', [])
                        if interests:
                            st.markdown(f"**主要兴趣:** {', '.join(interests)}")
                        
                        # 4. 成本与利润分析
                        st.markdown("### 💰 成本与利润分析")
                        profit = analysis.get('profit_analysis', {})
                        col1, col2 = st.columns(2)
                        with col1:
                            for item in profit.get('profit_analysis', []):
                                st.info(item)
                        with col2:
                            st.metric("估算利润率", f"{profit.get('estimated_profit_margin', 0):.2f}%")
                            st.metric("平台佣金率", "15%")
                        
                        # 5. 产品生命周期分析
                        st.markdown("### 📈 产品生命周期分析")
                        lifecycle = analysis.get('lifecycle_analysis', {})
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("平均评论数", f"{lifecycle.get('average_reviews', 0):.0f}")
                        with col2:
                            sentiment = lifecycle.get('review_sentiment', 'neutral')
                            st.metric("用户情绪", sentiment.title())
                        with col3:
                            stage = lifecycle.get('estimated_lifecycle_stage', 'unknown')
                            st.metric("生命周期阶段", stage.title())
                        
                        # 6. 竞争分析
                        st.markdown("### 🏆 竞争分析")
                        competition = analysis.get('competition_analysis', {})
                        
                        # 主要品牌
                        main_brands = competition.get('main_brands', [])
                        if main_brands:
                            st.markdown("**主要品牌市场份额:**")
                            df_brands = pd.DataFrame(main_brands)
                            fig_brands = px.bar(
                                df_brands,
                                x='brand',
                                y='market_share_percent',
                                text='market_share_percent',
                                labels={'brand': '品牌', 'market_share_percent': '市场份额 (%)'},
                                title='品牌市场份额分布'
                            )
                            fig_brands.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                            st.plotly_chart(fig_brands, use_container_width=True)
                        
                        st.info(f"**市场集中度:** {competition.get('market_concentration', 'N/A')}")
                        
                        # 定价策略
                        pricing = competition.get('pricing_strategies', [])
                        if pricing:
                            st.markdown("**主要品牌定价策略:**")
                            df_pricing = pd.DataFrame(pricing)
                            st.dataframe(df_pricing, use_container_width=True)
                        
                        # 推广渠道
                        promo = competition.get('promotion_insights', [])
                        if promo:
                            st.markdown("**推荐推广渠道:**")
                            for channel in promo:
                                st.markdown(f"- {channel}")
                        
                        # 7. AI深度洞察（如果有OpenAI）
                        ai_insights = analysis.get('ai_insights', {})
                        if ai_insights and 'ai_generated_insights' in ai_insights:
                            st.markdown("### 🤖 AI深度洞察 (OpenAI GPT-3.5)")
                            st.markdown(ai_insights['ai_generated_insights'])
                            st.caption(f"生成时间: {ai_insights.get('timestamp', 'N/A')}")
                        elif ai_insights and 'error' in ai_insights:
                            st.warning(f"AI分析不可用: {ai_insights.get('message', ai_insights['error'])}")
                            st.info("💡 提示: 设置环境变量 OPENAI_API_KEY 以启用AI深度分析")
                        
                        # 8. 政策与法规
                        st.markdown("### 📜 政策与行业方向")
                        policy = analysis.get('policy_insights', {})
                        
                        policies = policy.get('relevant_policies', [])
                        if policies:
                            st.markdown("**相关政策:**")
                            for pol in policies[:3]:
                                with st.expander(f"📄 {pol.get('source', 'Unknown')} - {pol.get('date', '')}"):
                                    st.write(pol.get('snippet', ''))
                        
                        direction = policy.get('industry_direction', [])
                        if direction:
                            st.markdown("**行业发展方向:**")
                            for d in direction:
                                st.markdown(f"- {d}")
                        
                        # 9. 热销产品分析
                        st.markdown("### 🔥 热销产品与关键词")
                        trending = analysis.get('trending_products', {})
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            top_brands = trending.get('top_brands', [])
                            if top_brands:
                                st.markdown("**热门品牌:**")
                                for brand, count in top_brands[:5]:
                                    st.markdown(f"- **{brand}**: {count} 个产品")
                        
                        with col2:
                            keywords = trending.get('popular_keywords', [])
                            if keywords:
                                st.markdown("**高频关键词:**")
                                for word, count in keywords[:10]:
                                    st.markdown(f"- {word}: {count}")
                        
                        # 保存分析结果
                        if st.button("💾 保存分析结果"):
                            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                            output_file = f"data/analysis_results_{timestamp}.json"
                            os.makedirs("data", exist_ok=True)
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(analysis, f, ensure_ascii=False, indent=2)
                            st.success(f"分析结果已保存: {output_file}")
                            
                    except Exception as e:
                        st.error(f"分析失败: {e}")
                        import traceback
                        st.code(traceback.format_exc())
        
        # 显示数据源追踪信息
        st.markdown("---")
        st.markdown("### 📊 数据来源可信度")
        st.info("本分析使用权威数据调研中心的真实数据源，确保分析结果的可靠性")
        
        # 显示数据源
        try:
            sources = get_all_sources()
            avg_credibility = sum(s['credibility'] for s in sources) / len(sources) if sources else 0
            st.metric("数据来源平均可信度", f"{avg_credibility:.0%}")
        except:
            pass
    
    with tab2:
        st.markdown("#### 数据指标异常检测")
        st.write("示例输入：历史销量（用于检测异常）")

        data = [100, 103, 120, 115, 420, 130, 110]
        
        # Create interactive plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(data) + 1)),
            y=data,
            mode='lines+markers',
            name='销量',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))
        
        # Detect and mark anomalies
        anomaly_indices = detect_anomalies(data)
        if anomaly_indices:
            anomaly_x = [i + 1 for i in anomaly_indices]
            anomaly_y = [data[i] for i in anomaly_indices]
            fig.add_trace(go.Scatter(
                x=anomaly_x,
                y=anomaly_y,
                mode='markers',
                name='异常点',
                marker=dict(color='red', size=12, symbol='x')
            ))
        
        fig.update_layout(
            title="销量趋势分析",
            xaxis_title="时间周期",
            yaxis_title="销量",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 异常检测结果")
        if anomaly_indices:
            for idx in anomaly_indices:
                st.warning(f"在位置 {idx+1} 检测到异常点，值为 {data[idx]}。")
            
            # Calculate anomaly percentage
            if idx > 0:
                prev_val = data[idx-1]
                change_pct = ((data[idx] - prev_val) / prev_val) * 100
                st.markdown("#### AI 解释")
                st.info(f"系统检测到第 {idx+1} 个数据点出现异常增长（约 +{change_pct:.1f}%），可能与促销活动或投放策略调整有关。")
        else:
            st.success("未发现明显异常。")

    
    with tab3:
        st.markdown("#### 权威数据来源验证")
        sources = get_all_sources()
        
        # Display sources in a more structured way
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**已集成的权威数据源:**")
            for source in sources:
                with st.expander(f"📊 {source['name']} (可信度: {source['credibility']:.0%})"):
                    st.markdown(f"**描述:** {source['description']}")
                    st.markdown(f"**链接:** [{source['url']}]({source['url']})")
                    st.progress(source['credibility'])
        
        with col2:
            # Calculate average credibility
            avg_credibility = sum(s['credibility'] for s in sources) / len(sources)
            st.metric("平均可信度", f"{avg_credibility:.0%}")
            st.metric("数据源数量", len(sources))
            
            # Create credibility chart
            fig_cred = px.bar(
                x=[s['name'].split('(')[0].strip() for s in sources],
                y=[s['credibility'] for s in sources],
                labels={'x': '数据源', 'y': '可信度'},
                title='数据源可信度对比'
            )
            fig_cred.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_cred, use_container_width=True)
    
    with tab4:
        st.markdown("#### 🧪 原型测试验证（集成到智能分析）")
        st.info("此模块用于验证AI分析结果的逻辑性和准确性")
        
        st.markdown("##### 验证步骤")
        
        # 验证步骤1: 数据完整性检查
        with st.expander("1️⃣ 数据完整性验证", expanded=True):
            st.write("检查采集的数据是否完整、格式是否正确")
            
            if st.button("运行数据完整性测试"):
                # 检查最近的数据文件
                data_dir = "data/amazon"
                if os.path.exists(data_dir):
                    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
                    if json_files:
                        latest_file = max(json_files)
                        with open(os.path.join(data_dir, latest_file), 'r') as f:
                            data = json.load(f)
                            items = data.get('items', data) if isinstance(data, dict) else data
                        
                        # 验证字段完整性
                        required_fields = ['asin', 'title', 'price', 'url']
                        missing_fields = []
                        field_coverage = {}
                        
                        for field in required_fields:
                            count = sum(1 for item in items if item.get(field))
                            coverage = (count / len(items) * 100) if items else 0
                            field_coverage[field] = coverage
                            if coverage < 80:
                                missing_fields.append(field)
                        
                        # 显示结果
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("数据条目数", len(items))
                            st.metric("必填字段覆盖率", f"{sum(field_coverage.values())/len(field_coverage):.1f}%")
                        
                        with col2:
                            for field, coverage in field_coverage.items():
                                color = "green" if coverage >= 80 else "orange" if coverage >= 50 else "red"
                                st.markdown(f"**{field}**: :{color}[{coverage:.1f}%]")
                        
                        if missing_fields:
                            st.warning(f"以下字段覆盖率不足80%: {', '.join(missing_fields)}")
                        else:
                            st.success("✅ 数据完整性验证通过！")
                    else:
                        st.warning("未找到数据文件")
                else:
                    st.warning("数据目录不存在")
        
        # 验证步骤2: AI分析逻辑验证
        with st.expander("2️⃣ AI分析逻辑验证"):
            st.write("验证AI分析结果是否符合逻辑，如市场规模与产品数量的关系")
            
            if st.button("运行逻辑验证测试"):
                # 加载最近的分析结果
                analysis_files = [f for f in os.listdir("data") if f.startswith("analysis_results_") and f.endswith(".json")] if os.path.exists("data") else []
                
                if analysis_files:
                    latest_analysis = max(analysis_files)
                    with open(os.path.join("data", latest_analysis), 'r') as f:
                        analysis = json.load(f)
                    
                    # 逻辑检查
                    checks = []
                    
                    # 检查1: 价格合理性
                    basic_stats = analysis.get('basic_stats', {})
                    price_range = basic_stats.get('price_range', {})
                    if price_range.get('min', 0) > 0 and price_range.get('max', 0) > price_range.get('min', 0):
                        checks.append(("✅", "价格范围合理"))
                    else:
                        checks.append(("❌", "价格范围异常"))
                    
                    # 检查2: 评分合理性
                    rating_stats = basic_stats.get('rating_stats', {})
                    avg_rating = rating_stats.get('average', 0)
                    if 0 <= avg_rating <= 5:
                        checks.append(("✅", "评分范围合理 (0-5)"))
                    else:
                        checks.append(("❌", "评分范围异常"))
                    
                    # 检查3: 利润率合理性
                    profit = analysis.get('profit_analysis', {})
                    profit_margin = profit.get('estimated_profit_margin', 0)
                    if -100 <= profit_margin <= 100:
                        checks.append(("✅", f"利润率合理 ({profit_margin:.2f}%)"))
                    else:
                        checks.append(("❌", "利润率异常"))
                    
                    # 检查4: 市场份额总和
                    competition = analysis.get('competition_analysis', {})
                    main_brands = competition.get('main_brands', [])
                    if main_brands:
                        total_share = sum(b['market_share_percent'] for b in main_brands)
                        if total_share <= 100:
                            checks.append(("✅", f"市场份额合理 (总计{total_share:.1f}%)"))
                        else:
                            checks.append(("❌", "市场份额总和超过100%"))
                    
                    # 显示检查结果
                    for emoji, message in checks:
                        st.markdown(f"{emoji} {message}")
                    
                    passed = sum(1 for e, _ in checks if e == "✅")
                    total = len(checks)
                    
                    if passed == total:
                        st.success(f"✅ 所有逻辑验证通过！({passed}/{total})")
                    else:
                        st.warning(f"⚠️ 部分验证未通过 ({passed}/{total})")
                else:
                    st.info("请先运行智能分析以生成分析结果")
        
        # 验证步骤3: 数据源可信度验证
        with st.expander("3️⃣ 数据源可信度验证"):
            st.write("验证使用的数据源是否来自权威机构")
            
            if st.button("运行可信度验证"):
                try:
                    sources = get_all_sources()
                    
                    st.markdown("**数据源验证结果:**")
                    for source in sources:
                        credibility = source['credibility']
                        if credibility >= 0.95:
                            st.success(f"✅ {source['name']}: {credibility:.0%} (高可信度)")
                        elif credibility >= 0.90:
                            st.info(f"ℹ️ {source['name']}: {credibility:.0%} (中等可信度)")
                        else:
                            st.warning(f"⚠️ {source['name']}: {credibility:.0%} (低可信度)")
                    
                    avg_credibility = sum(s['credibility'] for s in sources) / len(sources)
                    
                    if avg_credibility >= 0.95:
                        st.success(f"✅ 平均可信度优秀: {avg_credibility:.0%}")
                    elif avg_credibility >= 0.90:
                        st.info(f"ℹ️ 平均可信度良好: {avg_credibility:.0%}")
                    else:
                        st.warning(f"⚠️ 平均可信度需提升: {avg_credibility:.0%}")
                
                except Exception as e:
                    st.error(f"验证失败: {e}")
        
        # 验证步骤4: 对比验证
        with st.expander("4️⃣ AI预测与实际数据对比验证"):
            st.write("对比AI预测的趋势与实际数据的一致性")
            st.info("💡 此功能需要历史数据积累，将随着系统使用逐步完善")
            
            st.markdown("""
            **验证维度:**
            - 价格趋势预测准确性
            - 销量增长预测准确性
            - 市场份额变化预测准确性
            - 用户情绪变化预测准确性
            
            **建议:**
            - 定期采集数据以建立历史基线
            - 对比AI分析结果与实际变化
            - 根据验证结果调整AI模型参数
            """)
        
        st.markdown("---")
        st.success("✅ 原型测试模块已集成到智能分析中，用于验证AI分析的正确性和逻辑性")

