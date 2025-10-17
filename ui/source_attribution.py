import streamlit as st
from core.collectors.market_collector import fetch_all_trends
from core.collectors.policy_collector import fetch_latest_policies

def render_sources():
    st.header("🔍 数据来源追踪与验证")
    st.info("展示当前权威数据来源、抓取时间与可信度综合评分。")

    if st.button("刷新"):
        st.rerun()

    with st.spinner("获取权威数据节点..."):
        trends = fetch_all_trends()
        st.subheader("权威趋势源")
        for d in trends:
            st.write(f"来源: {d.get('source')}")
            st.write(f"链接: {d.get('url', '#')}")
            st.write(f"时间: {d.get('fetched_at', 'N/A')}")
            st.write(f"摘要: {d.get('metric', d.get('data',''))}")
            st.write(f"权威度: {d.get('credibility','N/A')}")
            st.markdown("---")

    st.subheader("政策源快照")
    policies = fetch_latest_policies()
    for p in policies:
        src = p["source"]
        st.write(f"{src.get('agency','未知')} - {src.get('country','')}")
        st.write(f"状态: {'OK' if p.get('ok') else 'ERROR'}  HTTP={p.get('http_status')}")
        st.write(f"可信度: {p.get('credibility')}")
        if p.get("snippet"):
            st.text(p.get("snippet")[:300])
        if p.get("error"):
            st.error(p.get("error"))
        st.markdown("---")

    st.success("✅ 交叉验证示例：整体可信度指数约 0.90（演示值）。")