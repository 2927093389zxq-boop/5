"""
用户管理模块 - 负责SaaS平台的用户数据存储和管理
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import hashlib


class UserManager:
    """用户管理器 - 处理用户的增删改查"""
    
    def __init__(self, data_file: str = "data/saas/users.json"):
        self.data_file = data_file
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            self._save_users([])
    
    def _load_users(self) -> List[Dict]:
        """加载用户数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_users(self, users: List[Dict]):
        """保存用户数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def _generate_user_id(self) -> str:
        """生成唯一的用户ID"""
        users = self._load_users()
        if not users:
            return "USER_1000"
        
        # 获取最大ID号
        max_id = 999
        for user in users:
            user_id = user.get('user_id', 'USER_999')
            try:
                num = int(user_id.split('_')[1])
                max_id = max(max_id, num)
            except:
                pass
        
        return f"USER_{max_id + 1}"
    
    def add_user(self, username: str, email: str, role: str = "普通用户", 
                 status: str = "活跃") -> Dict:
        """
        添加新用户
        
        Args:
            username: 用户名
            email: 邮箱
            role: 角色（管理员、VIP用户、普通用户）
            status: 状态（活跃、禁用、待激活）
        
        Returns:
            新创建的用户信息
        """
        users = self._load_users()
        
        # 检查用户名和邮箱是否已存在
        for user in users:
            if user['username'] == username:
                raise ValueError(f"用户名 '{username}' 已存在")
            if user['email'] == email:
                raise ValueError(f"邮箱 '{email}' 已被使用")
        
        # 创建新用户
        new_user = {
            'user_id': self._generate_user_id(),
            'username': username,
            'email': email,
            'role': role,
            'status': status,
            'register_date': datetime.now().strftime('%Y-%m-%d'),
            'last_login': datetime.now().strftime('%Y-%m-%d'),
            'created_at': datetime.now().isoformat()
        }
        
        users.append(new_user)
        self._save_users(users)
        
        return new_user
    
    def get_all_users(self) -> List[Dict]:
        """获取所有用户"""
        return self._load_users()
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """根据ID获取用户"""
        users = self._load_users()
        for user in users:
            if user['user_id'] == user_id:
                return user
        return None
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段
        
        Returns:
            是否更新成功
        """
        users = self._load_users()
        
        for i, user in enumerate(users):
            if user['user_id'] == user_id:
                # 不允许修改某些字段
                protected_fields = ['user_id', 'created_at', 'register_date']
                for key, value in kwargs.items():
                    if key not in protected_fields:
                        users[i][key] = value
                
                users[i]['updated_at'] = datetime.now().isoformat()
                self._save_users(users)
                return True
        
        return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否删除成功
        """
        users = self._load_users()
        initial_count = len(users)
        
        users = [u for u in users if u['user_id'] != user_id]
        
        if len(users) < initial_count:
            self._save_users(users)
            return True
        
        return False
    
    def search_users(self, keyword: str) -> List[Dict]:
        """
        搜索用户
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            匹配的用户列表
        """
        users = self._load_users()
        keyword = keyword.lower()
        
        results = []
        for user in users:
            # 在用户名、邮箱、角色中搜索
            if (keyword in user.get('username', '').lower() or
                keyword in user.get('email', '').lower() or
                keyword in user.get('role', '').lower() or
                keyword in user.get('user_id', '').lower()):
                results.append(user)
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        获取用户统计信息
        
        Returns:
            统计信息字典
        """
        users = self._load_users()
        
        stats = {
            'total_users': len(users),
            'active_users': len([u for u in users if u.get('status') == '活跃']),
            'paid_users': len([u for u in users if u.get('role') in ['VIP用户', '管理员']]),
            'roles': {},
            'status': {}
        }
        
        # 统计角色分布
        for user in users:
            role = user.get('role', '未知')
            stats['roles'][role] = stats['roles'].get(role, 0) + 1
        
        # 统计状态分布
        for user in users:
            status = user.get('status', '未知')
            stats['status'][status] = stats['status'].get(status, 0) + 1
        
        return stats
