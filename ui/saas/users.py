
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
from core.user_manager import UserManager

def render_users_management():
    """渲染 SaaS 用户管理页面"""
    st.title("👥 用户管理")
    
    # 初始化用户管理器
    user_manager = UserManager()
    
    # 获取统计信息
    stats = user_manager.get_statistics()
    
    # 基本统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总用户数", stats['total_users'])
    with col2:
        st.metric("活跃用户", stats['active_users'])
    with col3:
        st.metric("付费用户", stats['paid_users'])
    with col4:
        # 计算月增长率（简化版）
        st.metric("状态正常", f"{stats['active_users']}/{stats['total_users']}")
    
    st.divider()
    
    # 用户操作区
    st.subheader("⚙️ 用户操作")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("搜索用户", placeholder="输入用户名或邮箱...")
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("➕ 添加新用户", use_container_width=True):
            st.session_state.show_add_user_form = True
    
    # 添加用户表单（弹窗式）
    if st.session_state.get('show_add_user_form', False):
        with st.expander("📝 添加新用户", expanded=True):
            with st.form("add_user_form"):
                st.write("请填写新用户信息")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_username = st.text_input("用户名*", placeholder="请输入用户名")
                    new_email = st.text_input("邮箱*", placeholder="user@example.com")
                
                with col2:
                    new_role = st.selectbox("角色", ["普通用户", "VIP用户", "管理员"])
                    new_status = st.selectbox("状态", ["活跃", "禁用", "待激活"])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    submit_button = st.form_submit_button("✅ 确认添加", use_container_width=True)
                with col2:
                    cancel_button = st.form_submit_button("❌ 取消", use_container_width=True)
                
                if submit_button:
                    if not new_username or not new_email:
                        st.error("请填写用户名和邮箱")
                    elif '@' not in new_email:
                        st.error("请输入有效的邮箱地址")
                    else:
                        try:
                            user = user_manager.add_user(
                                username=new_username,
                                email=new_email,
                                role=new_role,
                                status=new_status
                            )
                            st.success(f"✅ 成功添加用户: {user['username']} ({user['user_id']})")
                            st.session_state.show_add_user_form = False
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ 添加失败: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ 系统错误: {str(e)}")
                
                if cancel_button:
                    st.session_state.show_add_user_form = False
                    st.rerun()
    
    # 用户列表
    st.subheader("📋 用户列表")
    
    # 获取用户数据
    if search_term:
        users_list = user_manager.search_users(search_term)
    else:
        users_list = user_manager.get_all_users()
    
    if users_list:
        # 转换为DataFrame
        users_data = []
        for user in users_list:
            users_data.append({
                "用户ID": user.get('user_id', 'N/A'),
                "用户名": user.get('username', 'N/A'),
                "邮箱": user.get('email', 'N/A'),
                "状态": user.get('status', 'N/A'),
                "角色": user.get('role', 'N/A'),
                "注册日期": user.get('register_date', 'N/A'),
                "最后登录": user.get('last_login', 'N/A')
            })
        
        df = pd.DataFrame(users_data)
        
        # 显示表格
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # 用户操作（编辑和删除）
        st.markdown("---")
        st.markdown("##### 🔧 用户操作")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_user_id = st.selectbox(
                "选择要操作的用户",
                options=[u['user_id'] for u in users_list],
                format_func=lambda x: f"{x} - {next((u['username'] for u in users_list if u['user_id'] == x), 'Unknown')}"
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("🗑️ 删除用户", use_container_width=True, type="secondary"):
                if user_manager.delete_user(selected_user_id):
                    st.success(f"✅ 已删除用户: {selected_user_id}")
                    st.rerun()
                else:
                    st.error("❌ 删除失败")
    else:
        st.info("暂无用户数据。点击'添加新用户'按钮开始添加用户。")
    
    
    st.divider()
    
    # 用户活跃度分析
    st.subheader("📊 用户活跃度分析")
    
    # 生成过去7天的活跃数据（基于实际用户数）
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)]
    # 使用实际用户数据生成模拟活跃度
    base_active = max(stats['active_users'], 1)
    active_users = [max(1, base_active + random.randint(-5, 5)) for _ in range(7)]
    
    activity_df = pd.DataFrame({
        "日期": dates,
        "活跃用户数": active_users
    })
    
    st.line_chart(activity_df.set_index("日期"))
    
    # 用户角色分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 用户角色分布")
        if stats['roles']:
            role_data = pd.DataFrame({
                "角色": list(stats['roles'].keys()),
                "数量": list(stats['roles'].values())
            })
            st.bar_chart(role_data.set_index("角色"))
        else:
            st.info("暂无角色分布数据")
    
    with col2:
        st.subheader("✅ 用户状态分布")
        if stats['status']:
            status_data = pd.DataFrame({
                "状态": list(stats['status'].keys()),
                "数量": list(stats['status'].values())
            })
            st.bar_chart(status_data.set_index("状态"))
        else:
            st.info("暂无状态分布数据")
