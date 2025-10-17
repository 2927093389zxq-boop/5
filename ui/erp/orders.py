
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

def render_order_management():
    """渲染 ERP 订单管理页面"""
    st.title("📝 订单管理")
    
    # 基本统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总订单数", "1,245", delta="89")
    with col2:
        st.metric("待处理订单", "23", delta="-5")
    with col3:
        st.metric("今日订单额", "¥45,678", delta="¥5,234")
    with col4:
        st.metric("平均订单价值", "¥386", delta="¥42")
    
    st.divider()
    
    # 订单操作
    st.subheader("⚙️ 订单操作")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_term = st.text_input("搜索订单", placeholder="输入订单号、客户名称...")
    with col2:
        st.write("")
        st.write("")
        if st.button("➕ 新建订单", use_container_width=True):
            st.info("新建订单功能开发中...")
    with col3:
        st.write("")
        st.write("")
        if st.button("📊 导出订单", use_container_width=True):
            st.info("导出功能开发中...")
    with col4:
        st.write("")
        st.write("")
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # 订单列表
    st.subheader("📋 订单列表")
    
    # 创建示例订单数据
    orders_data = []
    statuses = ["待付款", "待发货", "已发货", "已完成", "已取消", "退款中"]
    payment_methods = ["支付宝", "微信支付", "信用卡", "货到付款"]
    
    for i in range(30):
        order_date = datetime.now() - timedelta(days=random.randint(0, 60))
        status = random.choice(statuses)
        
        # 根据状态设置合理的时间
        if status == "已完成":
            delivery_date = order_date + timedelta(days=random.randint(3, 7))
        elif status == "已发货":
            delivery_date = order_date + timedelta(days=random.randint(1, 3))
        else:
            delivery_date = None
        
        orders_data.append({
            "订单号": f"ORD{20250000+i}",
            "客户": f"customer{i+1}@example.com",
            "产品数量": random.randint(1, 5),
            "订单金额": f"¥{random.randint(50, 2000):,}",
            "支付方式": random.choice(payment_methods),
            "状态": status,
            "下单时间": order_date.strftime("%Y-%m-%d %H:%M"),
            "发货时间": delivery_date.strftime("%Y-%m-%d %H:%M") if delivery_date else "-",
            "备注": random.choice(["", "", "", "急件", "礼品包装"])
        })
    
    df = pd.DataFrame(orders_data)
    
    # 添加过滤器
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "筛选状态",
            options=statuses,
            default=["待付款", "待发货", "已发货"]
        )
    with col2:
        payment_filter = st.multiselect(
            "支付方式",
            options=payment_methods,
            default=payment_methods
        )
    with col3:
        date_range = st.selectbox(
            "时间范围",
            options=["全部", "今天", "最近7天", "最近30天", "最近90天"]
        )
    
    # 应用过滤
    if status_filter:
        df = df[df["状态"].isin(status_filter)]
    if payment_filter:
        df = df[df["支付方式"].isin(payment_filter)]
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)]
    
    # 应用时间范围过滤
    if date_range != "全部":
        days_map = {"今天": 1, "最近7天": 7, "最近30天": 30, "最近90天": 90}
        days = days_map.get(date_range, 365)
        cutoff_date = datetime.now() - timedelta(days=days)
        df["下单时间_dt"] = pd.to_datetime(df["下单时间"])
        df = df[df["下单时间_dt"] >= cutoff_date]
        df = df.drop("下单时间_dt", axis=1)
    
    # 显示表格
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    st.info(f"共找到 {len(df)} 个订单")
    
    st.divider()
    
    # 订单分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 订单状态分布")
        status_count = df["状态"].value_counts()
        st.bar_chart(status_count)
    
    with col2:
        st.subheader("💳 支付方式分布")
        payment_count = df["支付方式"].value_counts()
        st.bar_chart(payment_count)
    
    st.divider()
    
    # 订单趋势
    st.subheader("📈 订单趋势")
    
    # 生成过去30天的订单数据
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(29, -1, -1)]
    order_counts = [random.randint(20, 60) for _ in range(30)]
    order_amounts = [random.randint(5000, 20000) for _ in range(30)]
    
    trend_df = pd.DataFrame({
        "日期": dates,
        "订单数": order_counts,
        "订单额": order_amounts
    })
    
    st.line_chart(trend_df.set_index("日期"))
    
    st.divider()
    
    # 待处理订单提醒
    st.subheader("⚠️ 待处理订单")
    
    pending_df = df[df["状态"].isin(["待付款", "待发货"])].copy()
    
    if len(pending_df) > 0:
        st.warning(f"发现 {len(pending_df)} 个订单需要处理！")
        st.dataframe(
            pending_df[["订单号", "客户", "订单金额", "状态", "下单时间", "备注"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("所有订单已处理完毕！")
