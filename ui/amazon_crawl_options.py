import streamlit as st
from core.data_fetcher import get_platform_data
from core.crawl.dispatcher import run_batch
from scrapers.logger import log_info
import os
import json


def render_amazon_crawl_tool():
    """渲染Amazon采集工具页面"""
    def render_amazon_crawl_tool():
        """渲染Amazon采集工具页面"""
        st.header("🛒 Amazon采集工具（全量增强版 + 自迭代控制台）")

        # 创建两个主标签页
        main_tab1, main_tab2 = st.tabs(["数据采集", "爬虫自我迭代控制台"])

    with main_tab1:
        st.markdown("### 📊 Amazon数据采集")
    
        mode = st.radio("模式选择", ["单页采集", "批量URL采集", "API接口模式"], horizontal=True)

        storage_mode = st.selectbox("存储模式", ["local", "mongo", "mysql", "cloud"], index=0)
        deep_detail = st.checkbox("采集详情页（包含评论、规格等）", value=True)
        max_items = st.slider("单页最大商品数", 10, 200, 50, 10)
    
        # API密钥配置（用于API模式）
        if mode == "API接口模式":
            st.info("💡 如果爬虫爬取失败，可以使用API接口获取数据")
            api_key = st.text_input("Amazon Product API密钥", type="password", 
                                   placeholder="可选：输入第三方Amazon数据API密钥")
            st.caption("支持的API: RapidAPI Amazon Product Data, Rainforest API等")

        if mode == "单页采集":
            pattern = st.radio("页面类型", ["Bestseller", "关键词搜索", "分类URL"], horizontal=True)
            keyword = ""
            category_url = ""
            if pattern == "关键词搜索":
                keyword = st.text_input("关键词", value="laptop")
            elif pattern == "分类URL":
                category_url = st.text_input("分类URL", value="https://www.amazon.com/bestsellers")

            if st.button("开始单页采集 🚀", type="primary"):
                with st.spinner("采集中..."):
                    try:
                        data = get_platform_data(
                            platform_name="Amazon",
                            keyword=keyword,
                            category_url=category_url,
                            max_items=max_items,
                            deep_detail=deep_detail
                        )
                    
                        if data:
                            st.success(f"完成，采集 {len(data)} 条数据")
                        
                            # 显示数据预览
                            st.markdown("#### 数据预览（前5条）")
                            for idx, item in enumerate(data[:5], 1):
                                with st.expander(f"📦 {idx}. {item.get('title', 'Unknown')[:100]}"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write("**ASIN:**", item.get('asin', 'N/A'))
                                        st.write("**价格:**", item.get('price', item.get('current_price', 'N/A')))
                                        st.write("**品牌:**", item.get('brand', 'N/A'))
                                        st.write("**评分:**", item.get('rating', item.get('average_rating', 'N/A')))
                                    with col2:
                                        st.write("**评论数:**", item.get('review_count', 'N/A'))
                                        st.write("**BSR:**", item.get('bsr_ranking', 'N/A')[:50] if item.get('bsr_ranking') else 'N/A')
                                        st.write("**FBA:**", "✅" if item.get('is_fba') else "❌")
                                        st.write("**库存:**", item.get('stock_status', 'N/A')[:30] if item.get('stock_status') else 'N/A')
                        
                            # 显示完整JSON
                            with st.expander("📄 查看完整JSON数据"):
                                st.json(data)
                        else:
                            st.error("未采集到数据。请尝试以下方法：")
                            st.markdown("""
                            1. 检查URL是否正确
                            2. 切换到"API接口模式"使用API获取数据
                            3. 查看爬虫自我迭代控制台进行调优
                            4. 检查日志文件: scraper.log
                            """)
                    except Exception as e:
                        st.error(f"采集失败: {e}")
                    
                        # 提供API接口选项
                        if st.button("🔄 切换到API接口模式"):
                            st.info("切换到'API接口模式'标签页，使用第三方API获取数据")

        elif mode == "批量URL采集":
            st.write("批量模式：输入多个 URL（每行一个）")
            urls_text = st.text_area("URL 列表", value="https://www.amazon.com/bestsellers\nhttps://www.amazon.com/s?k=usb+hub", height=150)
        
            if st.button("开始批量采集 🧩", type="primary"):
                urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
                if not urls:
                    st.error("请提供至少一个 URL。")
                else:
                    st.info(f"共 {len(urls)} 个任务，开始调度...")
                    with st.spinner("批量采集中..."):
                        try:
                            run_batch(urls, storage_mode=storage_mode)
                            st.success("批量任务已完成（查看 data/ 或数据库中结果）。")
                        except Exception as e:
                            st.error(f"批量采集失败: {e}")
    
        elif mode == "API接口模式":
            st.markdown("### 🔌 使用API接口获取Amazon数据")
            st.info("此模式通过第三方API获取数据，避免爬虫被封禁")
        
            api_endpoint = st.text_input("API端点URL", placeholder="https://api.example.com/amazon/products")
        
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("搜索关键词", value="laptop")
            with col2:
                api_max_results = st.number_input("结果数量", min_value=1, max_value=100, value=50)
        
            if st.button("📡 通过API获取数据", type="primary"):
                st.warning("⚠️ 此功能需要有效的第三方API密钥")
                st.info("请联系API提供商获取密钥，如: RapidAPI, Rainforest API, ScraperAPI等")
            
                # 示例：显示如何使用API
                st.markdown("""
                **API使用示例代码:**
                ```python
                import requests
            
                url = "https://rapidapi.com/api/amazon-product"
                headers = {
                    "X-RapidAPI-Key": "your_api_key",
                    "X-RapidAPI-Host": "amazon-product.p.rapidapi.com"
                }
                params = {
                    "query": "laptop",
                    "max_results": 50
                }
            
                response = requests.get(url, headers=headers, params=params)
                data = response.json()
                ```
                """)

        st.divider()
        st.markdown("**💡 提示：**")
        st.markdown("- 查看根目录 scraper.log 获取详细日志")
        st.markdown("- 如果爬取失败，尝试使用'爬虫自我迭代控制台'优化爬虫")
        st.markdown("- 或切换到'API接口模式'使用第三方API")

    with main_tab2:
        st.markdown("### 🧬 爬虫自我迭代控制台（集成优化）")
        st.info("此控制台用于监控和优化Amazon爬虫性能")
    
        # 导入迭代引擎
        try:
            from core.auto_crawler_iter.iteration_engine import CrawlerIterationEngine
            from core.auto_crawler_iter.metrics_collector import MetricsCollector
        
            engine = CrawlerIterationEngine()
            collector = MetricsCollector()
        
            # 显示当前指标
            col1, col2 = st.columns(2)
        
            with col1:
                st.markdown("#### 📊 当前爬虫指标")
                if st.button("🔄 刷新指标", key="refresh_metrics"):
                    metrics = collector.collect()
                
                    st.metric("抓取商品总数", metrics.get('items_total', 0))
                    st.metric("零结果页面数", metrics.get('pages_zero', 0))
                    st.metric("错误次数", metrics.get('errors_total', 0))
                    st.metric("验证码命中次数", metrics.get('captcha_hits', 0))
                    st.metric("平均页面加载时间", f"{metrics.get('avg_list_time', 0):.2f}秒")
                
                    # 计算成功率
                    total_pages = metrics.get('items_total', 0) + metrics.get('pages_zero', 0)
                    if total_pages > 0:
                        success_rate = (metrics.get('items_total', 0) / total_pages) * 100
                        st.metric("成功率", f"{success_rate:.1f}%")
        
            with col2:
                st.markdown("#### 🔧 优化控制")
            
                if st.button("▶️ 运行一轮迭代优化", key="run_iteration", type="primary"):
                    with st.spinner("正在运行迭代优化..."):
                        result = engine.run_once()
                        st.success("✅ 迭代优化完成")
                        st.json(result)
            
                st.markdown("---")
            
                # 自动优化开关
                auto_optimize = st.checkbox("启用自动优化（定时运行）", value=False)
                if auto_optimize:
                    st.info("自动优化将在后台运行，每2小时检查一次")
                    st.caption("通过scheduler.py配置自动优化间隔")
        
            st.divider()
        
            # 显示补丁列表
            st.markdown("#### 🩹 候选补丁列表")
            patch_dir = engine.cfg.get("patch_output_dir", "sandbox/patches")
        
            patches = []
            if os.path.isdir(patch_dir):
                patches = [f for f in os.listdir(patch_dir) if f.endswith(".patch")]
        
            if not patches:
                st.info("暂无补丁候选。点击上方'运行一轮迭代优化'生成补丁。")
            else:
                st.success(f"找到 {len(patches)} 个候选补丁")
            
                for idx, p in enumerate(patches, 1):
                    tag = p.replace(".patch", "")
                
                    with st.expander(f"🩹 补丁 {idx}: {p}"):
                        # 显示补丁内容
                        try:
                            with open(os.path.join(patch_dir, p), "r", encoding="utf-8") as f:
                                patch_content = f.read()
                            st.code(patch_content, language="diff")
                        except Exception as e:
                            st.error(f"读取补丁失败: {e}")
                    
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ 应用补丁", key=f"apply_{tag}"):
                                try:
                                    res = engine.apply_patch(tag)
                                    st.success(f"补丁已应用: {res}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"应用补丁失败: {e}")
                    
                        with col2:
                            if st.button(f"🗑️ 删除补丁", key=f"delete_{tag}"):
                                try:
                                    os.remove(os.path.join(patch_dir, p))
                                    st.success("补丁已删除")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"删除失败: {e}")
        
            st.divider()
            st.caption("💡 提示：补丁会修改 scrapers/amazon_scraper.py 中的选择器和参数，提升爬取成功率")
        
        except ImportError as e:
            st.error(f"无法加载迭代引擎: {e}")
            st.info("请确保已安装所有依赖: pip install -r requirements.txt")
        except Exception as e:
            st.error(f"迭代控制台加载失败: {e}")
            import traceback
            with st.expander("查看错误详情"):
                st.code(traceback.format_exc())

# Auto-execute if run directly
if __name__ == "__main__":
    render_amazon_crawl_tool()