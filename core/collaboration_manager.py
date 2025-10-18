"""
企业协作功能模块 - 提供真实的团队协作能力
Enterprise Collaboration Module - Provides real team collaboration capabilities
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib


class CollaborationManager:
    """企业协作管理器"""
    
    def __init__(self, data_dir: str = "data/collaboration"):
        """
        初始化协作管理器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 配置文件路径
        self.users_file = os.path.join(data_dir, "users.json")
        self.teams_file = os.path.join(data_dir, "teams.json")
        self.projects_file = os.path.join(data_dir, "projects.json")
        self.tasks_file = os.path.join(data_dir, "tasks.json")
        self.messages_file = os.path.join(data_dir, "messages.json")
        
        # 加载数据
        self.users = self._load_data(self.users_file, {})
        self.teams = self._load_data(self.teams_file, {})
        self.projects = self._load_data(self.projects_file, {})
        self.tasks = self._load_data(self.tasks_file, {})
        self.messages = self._load_data(self.messages_file, [])
    
    def _load_data(self, file_path: str, default: Any) -> Any:
        """加载数据文件"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return default
        return default
    
    def _save_data(self, file_path: str, data: Any):
        """保存数据文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, prefix: str = "id") -> str:
        """生成唯一ID"""
        timestamp = datetime.now().timestamp()
        hash_input = f"{prefix}_{timestamp}".encode()
        return f"{prefix}_{hashlib.md5(hash_input).hexdigest()[:12]}"
    
    # ===== 用户管理 =====
    
    def add_user(self, username: str, email: str, role: str = "member",
                department: str = "", **kwargs) -> Dict[str, Any]:
        """
        添加用户
        
        Args:
            username: 用户名
            email: 邮箱
            role: 角色（admin/manager/member）
            department: 部门
            **kwargs: 其他用户信息
            
        Returns:
            操作结果
        """
        # 检查用户是否已存在
        if any(u.get('email') == email for u in self.users.values()):
            return {
                'success': False,
                'message': '邮箱已被使用'
            }
        
        user_id = self._generate_id('user')
        
        user = {
            'id': user_id,
            'username': username,
            'email': email,
            'role': role,
            'department': department,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            **kwargs
        }
        
        self.users[user_id] = user
        self._save_data(self.users_file, self.users)
        
        return {
            'success': True,
            'message': f'用户 {username} 添加成功',
            'user': user
        }
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        return self.users.get(user_id)
    
    def list_users(self, role: str = None, department: str = None) -> List[Dict[str, Any]]:
        """列出用户"""
        users = list(self.users.values())
        
        if role:
            users = [u for u in users if u.get('role') == role]
        
        if department:
            users = [u for u in users if u.get('department') == department]
        
        return users
    
    # ===== 团队管理 =====
    
    def create_team(self, name: str, description: str = "", 
                   leader_id: str = None, members: List[str] = None) -> Dict[str, Any]:
        """
        创建团队
        
        Args:
            name: 团队名称
            description: 团队描述
            leader_id: 团队负责人ID
            members: 成员ID列表
            
        Returns:
            操作结果
        """
        team_id = self._generate_id('team')
        
        team = {
            'id': team_id,
            'name': name,
            'description': description,
            'leader_id': leader_id,
            'members': members or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.teams[team_id] = team
        self._save_data(self.teams_file, self.teams)
        
        return {
            'success': True,
            'message': f'团队 {name} 创建成功',
            'team': team
        }
    
    def add_team_member(self, team_id: str, user_id: str) -> Dict[str, Any]:
        """向团队添加成员"""
        if team_id not in self.teams:
            return {'success': False, 'message': '团队不存在'}
        
        if user_id not in self.users:
            return {'success': False, 'message': '用户不存在'}
        
        if user_id not in self.teams[team_id]['members']:
            self.teams[team_id]['members'].append(user_id)
            self.teams[team_id]['updated_at'] = datetime.now().isoformat()
            self._save_data(self.teams_file, self.teams)
        
        return {
            'success': True,
            'message': '成员添加成功'
        }
    
    def list_teams(self) -> List[Dict[str, Any]]:
        """列出所有团队"""
        return list(self.teams.values())
    
    # ===== 项目管理 =====
    
    def create_project(self, name: str, description: str = "",
                      team_id: str = None, status: str = "active",
                      **kwargs) -> Dict[str, Any]:
        """
        创建项目
        
        Args:
            name: 项目名称
            description: 项目描述
            team_id: 关联团队ID
            status: 项目状态（active/completed/archived）
            **kwargs: 其他项目信息
            
        Returns:
            操作结果
        """
        project_id = self._generate_id('proj')
        
        project = {
            'id': project_id,
            'name': name,
            'description': description,
            'team_id': team_id,
            'status': status,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tasks': [],
            **kwargs
        }
        
        self.projects[project_id] = project
        self._save_data(self.projects_file, self.projects)
        
        return {
            'success': True,
            'message': f'项目 {name} 创建成功',
            'project': project
        }
    
    def list_projects(self, team_id: str = None, status: str = None) -> List[Dict[str, Any]]:
        """列出项目"""
        projects = list(self.projects.values())
        
        if team_id:
            projects = [p for p in projects if p.get('team_id') == team_id]
        
        if status:
            projects = [p for p in projects if p.get('status') == status]
        
        return projects
    
    # ===== 任务管理 =====
    
    def create_task(self, title: str, description: str = "",
                   project_id: str = None, assignee_id: str = None,
                   priority: str = "medium", status: str = "todo",
                   due_date: str = None, **kwargs) -> Dict[str, Any]:
        """
        创建任务
        
        Args:
            title: 任务标题
            description: 任务描述
            project_id: 所属项目ID
            assignee_id: 负责人ID
            priority: 优先级（low/medium/high/urgent）
            status: 状态（todo/in_progress/review/done）
            due_date: 截止日期
            **kwargs: 其他任务信息
            
        Returns:
            操作结果
        """
        task_id = self._generate_id('task')
        
        task = {
            'id': task_id,
            'title': title,
            'description': description,
            'project_id': project_id,
            'assignee_id': assignee_id,
            'priority': priority,
            'status': status,
            'due_date': due_date,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            **kwargs
        }
        
        self.tasks[task_id] = task
        
        # 更新项目的任务列表
        if project_id and project_id in self.projects:
            if 'tasks' not in self.projects[project_id]:
                self.projects[project_id]['tasks'] = []
            self.projects[project_id]['tasks'].append(task_id)
            self._save_data(self.projects_file, self.projects)
        
        self._save_data(self.tasks_file, self.tasks)
        
        return {
            'success': True,
            'message': f'任务 {title} 创建成功',
            'task': task
        }
    
    def update_task_status(self, task_id: str, status: str) -> Dict[str, Any]:
        """更新任务状态"""
        if task_id not in self.tasks:
            return {'success': False, 'message': '任务不存在'}
        
        self.tasks[task_id]['status'] = status
        self.tasks[task_id]['updated_at'] = datetime.now().isoformat()
        self._save_data(self.tasks_file, self.tasks)
        
        return {
            'success': True,
            'message': '任务状态更新成功',
            'task': self.tasks[task_id]
        }
    
    def list_tasks(self, project_id: str = None, assignee_id: str = None,
                  status: str = None, priority: str = None) -> List[Dict[str, Any]]:
        """列出任务"""
        tasks = list(self.tasks.values())
        
        if project_id:
            tasks = [t for t in tasks if t.get('project_id') == project_id]
        
        if assignee_id:
            tasks = [t for t in tasks if t.get('assignee_id') == assignee_id]
        
        if status:
            tasks = [t for t in tasks if t.get('status') == status]
        
        if priority:
            tasks = [t for t in tasks if t.get('priority') == priority]
        
        return tasks
    
    # ===== 消息/通知 =====
    
    def send_message(self, sender_id: str, receiver_id: str,
                    content: str, message_type: str = "direct",
                    **kwargs) -> Dict[str, Any]:
        """
        发送消息
        
        Args:
            sender_id: 发送者ID
            receiver_id: 接收者ID（可以是用户ID或团队ID）
            content: 消息内容
            message_type: 消息类型（direct/team/broadcast）
            **kwargs: 其他消息信息
            
        Returns:
            操作结果
        """
        message = {
            'id': self._generate_id('msg'),
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'content': content,
            'type': message_type,
            'read': False,
            'created_at': datetime.now().isoformat(),
            **kwargs
        }
        
        self.messages.append(message)
        self._save_data(self.messages_file, self.messages)
        
        return {
            'success': True,
            'message': '消息发送成功',
            'message_data': message
        }
    
    def get_messages(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """获取用户消息"""
        messages = [
            m for m in self.messages
            if m.get('receiver_id') == user_id
        ]
        
        if unread_only:
            messages = [m for m in messages if not m.get('read', False)]
        
        return sorted(messages, key=lambda x: x.get('created_at', ''), reverse=True)
    
    # ===== 统计信息 =====
    
    def get_stats(self) -> Dict[str, Any]:
        """获取协作统计信息"""
        return {
            'total_users': len(self.users),
            'total_teams': len(self.teams),
            'total_projects': len(self.projects),
            'total_tasks': len(self.tasks),
            'active_projects': len([p for p in self.projects.values() if p.get('status') == 'active']),
            'pending_tasks': len([t for t in self.tasks.values() if t.get('status') in ['todo', 'in_progress']]),
            'unread_messages': len([m for m in self.messages if not m.get('read', False)])
        }
