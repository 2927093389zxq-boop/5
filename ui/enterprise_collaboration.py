"""
企业协作界面 - 团队协作功能UI
Enterprise Collaboration UI - Team collaboration features interface
"""

import streamlit as st
from core.collaboration_manager import CollaborationManager
from datetime import datetime
import pandas as pd


def render_enterprise_collaboration():
    """渲染企业协作主界面"""
    st.header("👥 企业协作中心")
    st.markdown("团队协作、项目管理、任务分配和实时沟通")
    
    # 初始化协作管理器
    if 'collab_manager' not in st.session_state:
        st.session_state.collab_manager = CollaborationManager()
    
    manager = st.session_state.collab_manager
    
    # 显示统计信息
    stats = manager.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👤 团队成员", stats['total_users'])
    
    with col2:
        st.metric("👥 团队数", stats['total_teams'])
    
    with col3:
        st.metric("📁 活跃项目", stats['active_projects'])
    
    with col4:
        st.metric("✅ 待办任务", stats['pending_tasks'])
    
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 团队管理",
        "📁 项目管理",
        "✅ 任务看板",
        "💬 团队消息",
        "👤 成员管理"
    ])
    
    with tab1:
        render_team_management(manager)
    
    with tab2:
        render_project_management(manager)
    
    with tab3:
        render_task_board(manager)
    
    with tab4:
        render_team_messages(manager)
    
    with tab5:
        render_member_management(manager)


def render_team_management(manager: CollaborationManager):
    """渲染团队管理界面"""
    st.markdown("### 👥 团队管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 团队列表")
    
    with col2:
        if st.button("➕ 创建新团队", use_container_width=True):
            st.session_state['creating_team'] = True
    
    # 创建团队表单
    if st.session_state.get('creating_team', False):
        with st.form("create_team_form"):
            st.markdown("#### 创建新团队")
            
            name = st.text_input("团队名称", placeholder="例如: 产品开发团队")
            description = st.text_area("团队描述", placeholder="描述团队的职责和目标...")
            
            # 选择团队负责人
            users = manager.list_users()
            if users:
                user_options = {f"{u['username']} ({u['email']})": u['id'] for u in users}
                leader = st.selectbox("团队负责人", [""] + list(user_options.keys()))
                leader_id = user_options.get(leader) if leader else None
            else:
                st.warning("暂无用户，请先在成员管理中添加用户")
                leader_id = None
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("✅ 创建", use_container_width=True)
            with col2:
                if st.form_submit_button("❌ 取消", use_container_width=True):
                    st.session_state['creating_team'] = False
                    st.rerun()
            
            if submitted:
                if not name:
                    st.error("请输入团队名称")
                else:
                    result = manager.create_team(
                        name=name,
                        description=description,
                        leader_id=leader_id
                    )
                    if result['success']:
                        st.success(result['message'])
                        st.session_state['creating_team'] = False
                        st.rerun()
    
    # 显示团队列表
    teams = manager.list_teams()
    
    if not teams:
        st.info("暂无团队，请创建第一个团队")
    else:
        for team in teams:
            with st.expander(f"👥 {team['name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**描述:** {team.get('description', '无')}")
                    
                    # 显示负责人
                    if team.get('leader_id'):
                        leader = manager.get_user(team['leader_id'])
                        if leader:
                            st.markdown(f"**负责人:** {leader['username']}")
                    
                    # 显示成员数
                    member_count = len(team.get('members', []))
                    st.markdown(f"**成员数:** {member_count}")
                    
                    st.caption(f"创建时间: {team.get('created_at', 'N/A')[:19]}")
                
                with col2:
                    if st.button("👤 管理成员", key=f"manage_{team['id']}", use_container_width=True):
                        st.session_state[f'managing_{team["id"]}'] = True
                
                # 成员管理
                if st.session_state.get(f'managing_{team["id"]}', False):
                    st.markdown("##### 添加成员")
                    
                    users = manager.list_users()
                    available_users = [
                        u for u in users 
                        if u['id'] not in team.get('members', [])
                    ]
                    
                    if available_users:
                        user_options = {
                            f"{u['username']} - {u['email']}": u['id'] 
                            for u in available_users
                        }
                        
                        selected_user = st.selectbox(
                            "选择用户",
                            list(user_options.keys()),
                            key=f"select_user_{team['id']}"
                        )
                        
                        if st.button("添加到团队", key=f"add_{team['id']}"):
                            user_id = user_options[selected_user]
                            result = manager.add_team_member(team['id'], user_id)
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                    else:
                        st.info("所有用户已在团队中")
                    
                    # 显示当前成员
                    st.markdown("##### 当前成员")
                    for member_id in team.get('members', []):
                        member = manager.get_user(member_id)
                        if member:
                            st.markdown(f"- {member['username']} ({member['email']})")


def render_project_management(manager: CollaborationManager):
    """渲染项目管理界面"""
    st.markdown("### 📁 项目管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 项目列表")
    
    with col2:
        if st.button("➕ 创建新项目", use_container_width=True):
            st.session_state['creating_project'] = True
    
    # 创建项目表单
    if st.session_state.get('creating_project', False):
        with st.form("create_project_form"):
            st.markdown("#### 创建新项目")
            
            name = st.text_input("项目名称", placeholder="例如: Q1产品升级")
            description = st.text_area("项目描述", placeholder="描述项目的目标和范围...")
            
            # 选择团队
            teams = manager.list_teams()
            if teams:
                team_options = {t['name']: t['id'] for t in teams}
                team = st.selectbox("关联团队", [""] + list(team_options.keys()))
                team_id = team_options.get(team) if team else None
            else:
                st.warning("暂无团队，建议先创建团队")
                team_id = None
            
            col1, col2 = st.columns(2)
            
            with col1:
                status = st.selectbox("项目状态", ["active", "planning", "on_hold", "completed"])
            
            with col2:
                priority = st.selectbox("优先级", ["low", "medium", "high", "urgent"])
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("✅ 创建", use_container_width=True)
            with col2:
                if st.form_submit_button("❌ 取消", use_container_width=True):
                    st.session_state['creating_project'] = False
                    st.rerun()
            
            if submitted:
                if not name:
                    st.error("请输入项目名称")
                else:
                    result = manager.create_project(
                        name=name,
                        description=description,
                        team_id=team_id,
                        status=status,
                        priority=priority
                    )
                    if result['success']:
                        st.success(result['message'])
                        st.session_state['creating_project'] = False
                        st.rerun()
    
    # 过滤选项
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("状态筛选", ["全部", "active", "planning", "on_hold", "completed"])
    with col2:
        teams = manager.list_teams()
        team_filter = st.selectbox("团队筛选", ["全部"] + [t['name'] for t in teams])
    
    # 获取项目列表
    projects = manager.list_projects()
    
    # 应用过滤
    if status_filter != "全部":
        projects = [p for p in projects if p.get('status') == status_filter]
    
    if team_filter != "全部":
        team_id = next((t['id'] for t in teams if t['name'] == team_filter), None)
        if team_id:
            projects = [p for p in projects if p.get('team_id') == team_id]
    
    if not projects:
        st.info("暂无项目，请创建第一个项目")
    else:
        for project in projects:
            status_icon = {
                'active': '🟢',
                'planning': '🔵',
                'on_hold': '🟡',
                'completed': '✅'
            }.get(project.get('status', 'active'), '⚪')
            
            with st.expander(f"{status_icon} {project['name']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**描述:** {project.get('description', '无')}")
                    st.markdown(f"**状态:** {project.get('status', 'N/A')}")
                    st.markdown(f"**优先级:** {project.get('priority', 'N/A')}")
                    
                    # 显示团队
                    if project.get('team_id'):
                        team = manager.teams.get(project['team_id'])
                        if team:
                            st.markdown(f"**团队:** {team['name']}")
                    
                    # 显示任务统计
                    task_count = len(project.get('tasks', []))
                    st.markdown(f"**任务数:** {task_count}")
                    
                    st.caption(f"创建时间: {project.get('created_at', 'N/A')[:19]}")
                
                with col2:
                    if st.button("📋 任务", key=f"tasks_{project['id']}", use_container_width=True):
                        st.session_state['selected_project'] = project['id']
                        st.session_state['active_tab'] = 2  # 切换到任务看板


def render_task_board(manager: CollaborationManager):
    """渲染任务看板"""
    st.markdown("### ✅ 任务看板")
    
    # 选择项目
    projects = manager.list_projects()
    
    if not projects:
        st.warning("暂无项目，请先创建项目")
        return
    
    project_options = {p['name']: p['id'] for p in projects}
    selected_project_name = st.selectbox("选择项目", list(project_options.keys()))
    selected_project_id = project_options[selected_project_name]
    
    st.markdown("---")
    
    # 创建任务按钮
    if st.button("➕ 创建新任务"):
        st.session_state['creating_task'] = True
    
    # 创建任务表单
    if st.session_state.get('creating_task', False):
        with st.form("create_task_form"):
            st.markdown("#### 创建新任务")
            
            title = st.text_input("任务标题", placeholder="例如: 完成功能模块A的开发")
            description = st.text_area("任务描述", placeholder="详细描述任务要求...")
            
            col1, col2 = st.columns(2)
            
            with col1:
                priority = st.selectbox("优先级", ["low", "medium", "high", "urgent"])
                status = st.selectbox("状态", ["todo", "in_progress", "review", "done"])
            
            with col2:
                # 选择负责人
                users = manager.list_users()
                if users:
                    user_options = {f"{u['username']}": u['id'] for u in users}
                    assignee = st.selectbox("负责人", ["未分配"] + list(user_options.keys()))
                    assignee_id = user_options.get(assignee) if assignee != "未分配" else None
                else:
                    assignee_id = None
                
                due_date = st.date_input("截止日期")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("✅ 创建", use_container_width=True)
            with col2:
                if st.form_submit_button("❌ 取消", use_container_width=True):
                    st.session_state['creating_task'] = False
                    st.rerun()
            
            if submitted:
                if not title:
                    st.error("请输入任务标题")
                else:
                    result = manager.create_task(
                        title=title,
                        description=description,
                        project_id=selected_project_id,
                        assignee_id=assignee_id,
                        priority=priority,
                        status=status,
                        due_date=due_date.isoformat() if due_date else None
                    )
                    if result['success']:
                        st.success(result['message'])
                        st.session_state['creating_task'] = False
                        st.rerun()
    
    # 显示任务看板（Kanban风格）
    st.markdown("#### 📊 任务状态看板")
    
    tasks = manager.list_tasks(project_id=selected_project_id)
    
    # 按状态分组
    status_columns = {
        'todo': '📝 待办',
        'in_progress': '⚙️ 进行中',
        'review': '👀 审核中',
        'done': '✅ 已完成'
    }
    
    cols = st.columns(4)
    
    for i, (status_key, status_label) in enumerate(status_columns.items()):
        with cols[i]:
            st.markdown(f"### {status_label}")
            
            status_tasks = [t for t in tasks if t.get('status') == status_key]
            st.caption(f"{len(status_tasks)} 个任务")
            
            for task in status_tasks:
                priority_icon = {
                    'low': '🟢',
                    'medium': '🟡',
                    'high': '🟠',
                    'urgent': '🔴'
                }.get(task.get('priority', 'medium'), '⚪')
                
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; 
                                padding: 10px; 
                                border-radius: 5px; 
                                margin-bottom: 10px;
                                background: white;">
                        <div style="font-weight: bold; margin-bottom: 5px;">
                            {priority_icon} {task['title']}
                        </div>
                        <div style="font-size: 12px; color: #666;">
                            {task.get('description', '')[:50]}...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 状态更新按钮
                    if status_key != 'done':
                        next_status = {
                            'todo': 'in_progress',
                            'in_progress': 'review',
                            'review': 'done'
                        }[status_key]
                        
                        if st.button("→", key=f"next_{task['id']}", help="移至下一状态"):
                            manager.update_task_status(task['id'], next_status)
                            st.rerun()


def render_team_messages(manager: CollaborationManager):
    """渲染团队消息界面"""
    st.markdown("### 💬 团队消息")
    
    users = manager.list_users()
    
    if not users:
        st.warning("暂无用户，无法发送消息")
        return
    
    # 选择当前用户（模拟登录）
    user_options = {f"{u['username']} ({u['email']})": u['id'] for u in users}
    current_user = st.selectbox("当前用户", list(user_options.keys()))
    current_user_id = user_options[current_user]
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 📨 发送消息")
        
        with st.form("send_message_form"):
            receiver = st.selectbox("接收者", [u for u in list(user_options.keys()) if user_options[u] != current_user_id])
            message_content = st.text_area("消息内容", placeholder="输入消息...")
            
            if st.form_submit_button("📤 发送"):
                if message_content:
                    receiver_id = user_options[receiver]
                    result = manager.send_message(
                        sender_id=current_user_id,
                        receiver_id=receiver_id,
                        content=message_content
                    )
                    if result['success']:
                        st.success("消息已发送")
                        st.rerun()
    
    with col2:
        st.markdown("#### 📬 收件箱")
        
        messages = manager.get_messages(current_user_id)
        
        if not messages:
            st.info("暂无消息")
        else:
            for msg in messages[:10]:  # 显示最近10条
                sender = manager.get_user(msg['sender_id'])
                sender_name = sender['username'] if sender else "未知用户"
                
                read_status = "" if msg.get('read') else "🔴 "
                
                with st.expander(f"{read_status}来自 {sender_name} - {msg.get('created_at', 'N/A')[:19]}"):
                    st.markdown(msg['content'])


def render_member_management(manager: CollaborationManager):
    """渲染成员管理界面"""
    st.markdown("### 👤 成员管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 成员列表")
    
    with col2:
        if st.button("➕ 添加成员", use_container_width=True):
            st.session_state['adding_member'] = True
    
    # 添加成员表单
    if st.session_state.get('adding_member', False):
        with st.form("add_member_form"):
            st.markdown("#### 添加新成员")
            
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("用户名", placeholder="例如: zhangsan")
                email = st.text_input("邮箱", placeholder="zhangsan@company.com")
            
            with col2:
                role = st.selectbox("角色", ["member", "manager", "admin"])
                department = st.text_input("部门", placeholder="例如: 产品部")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("✅ 添加", use_container_width=True)
            with col2:
                if st.form_submit_button("❌ 取消", use_container_width=True):
                    st.session_state['adding_member'] = False
                    st.rerun()
            
            if submitted:
                if not username or not email:
                    st.error("请填写用户名和邮箱")
                else:
                    result = manager.add_user(
                        username=username,
                        email=email,
                        role=role,
                        department=department
                    )
                    if result['success']:
                        st.success(result['message'])
                        st.session_state['adding_member'] = False
                        st.rerun()
                    else:
                        st.error(result['message'])
    
    # 显示成员列表
    users = manager.list_users()
    
    if not users:
        st.info("暂无成员，请添加第一个成员")
    else:
        # 转换为DataFrame显示
        user_data = []
        for user in users:
            user_data.append({
                '用户名': user.get('username', 'N/A'),
                '邮箱': user.get('email', 'N/A'),
                '角色': user.get('role', 'N/A'),
                '部门': user.get('department', 'N/A'),
                '状态': user.get('status', 'N/A'),
                '创建时间': user.get('created_at', 'N/A')[:19]
            })
        
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
