
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

def render_billing_management():
    """渲染 SaaS 计费管理页面"""
    st.title("💰 计费管理")
    
    # 基本统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("本月收入", "¥45,678", delta="¥5,234")
    with col2:
        st.metric("付费订阅", "89", delta="5")
    with col3:
        st.metric("待处理账单", "12", delta="-3")
    with col4:
        st.metric("平均客单价", "¥513", delta="¥42")
    
    st.divider()
    
    # 订阅计划概览
    st.subheader("📦 订阅计划概览")
    
    plans_col1, plans_col2, plans_col3 = st.columns(3)
    
    with plans_col1:
        st.info("**基础版**")
        st.write("¥99/月")
        st.write("- 100 个商品")
        st.write("- 基础分析")
        st.write("- 邮件支持")
        st.metric("订阅数", "45")
    
    with plans_col2:
        st.success("**专业版**")
        st.write("¥299/月")
        st.write("- 1000 个商品")
        st.write("- 高级分析")
        st.write("- 电话支持")
        st.metric("订阅数", "32")
    
    with plans_col3:
        st.warning("**企业版**")
        st.write("¥999/月")
        st.write("- 无限商品")
        st.write("- 自定义功能")
        st.write("- 专属客服")
        st.metric("订阅数", "12")
    
    st.divider()
    
    # 收入趋势
    st.subheader("📈 收入趋势")
    
    # 生成过去30天的收入数据
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(29, -1, -1)]
    revenue = [random.randint(30000, 60000) for _ in range(30)]
    
    revenue_df = pd.DataFrame({
        "日期": dates,
        "收入": revenue
    })
    
    st.line_chart(revenue_df.set_index("日期"))
    
    st.divider()
    
    # 最近账单
    st.subheader("📋 最近账单")
    
    # 创建示例账单数据
    bills_data = []
    for i in range(15):
        bills_data.append({
            "账单ID": f"BILL_{10000+i}",
            "客户": f"customer{i+1}@example.com",
            "计划": random.choice(["基础版", "专业版", "企业版"]),
            "金额": random.choice(["¥99", "¥299", "¥999"]),
            "状态": random.choice(["已支付", "已支付", "已支付", "待支付", "已退款"]),
            "账单日期": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "到期日期": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        })
    
    df = pd.DataFrame(bills_data)
    
    # 添加过滤器
    col1, col2 = st.columns([2, 1])
    with col1:
        status_filter = st.multiselect(
            "筛选状态",
            options=["已支付", "待支付", "已退款"],
            default=["已支付", "待支付"]
        )
    
    # 应用过滤
    if status_filter:
        df = df[df["状态"].isin(status_filter)]
    
    # 显示表格
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # 支付方式统计
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💳 支付方式分布")
        payment_data = pd.DataFrame({
            "支付方式": ["支付宝", "微信支付", "信用卡", "银行转账"],
            "数量": [45, 32, 18, 5]
        })
        st.bar_chart(payment_data.set_index("支付方式"))
    
    with col2:
        st.subheader("📊 订阅计划分布")
        plan_data = pd.DataFrame({
            "计划": ["基础版", "专业版", "企业版"],
            "数量": [45, 32, 12]
        })
        st.bar_chart(plan_data.set_index("计划"))
