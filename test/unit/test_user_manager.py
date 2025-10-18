"""
单元测试：用户管理器
"""
import unittest
import os
import json
import tempfile
from datetime import datetime
from core.user_manager import UserManager


class TestUserManager(unittest.TestCase):
    """测试用户管理器的各项功能"""
    
    def setUp(self):
        """设置测试环境 - 使用临时文件"""
        # 使用 mkstemp 更安全的方式创建临时文件
        fd, self.temp_file_path = tempfile.mkstemp(suffix='.json')
        os.close(fd)  # 立即关闭文件描述符
        self.user_manager = UserManager(data_file=self.temp_file_path)
    
    def tearDown(self):
        """清理测试环境"""
        try:
            if os.path.exists(self.temp_file_path):
                os.unlink(self.temp_file_path)
        except Exception:
            pass  # 静默处理清理错误
    
    def test_add_user(self):
        """测试添加用户"""
        user = self.user_manager.add_user(
            username="testuser",
            email="test@example.com",
            role="普通用户",
            status="活跃"
        )
        
        self.assertEqual(user['username'], "testuser")
        self.assertEqual(user['email'], "test@example.com")
        self.assertEqual(user['role'], "普通用户")
        self.assertEqual(user['status'], "活跃")
        self.assertIn('user_id', user)
        self.assertIn('register_date', user)
    
    def test_add_duplicate_username(self):
        """测试添加重复用户名"""
        self.user_manager.add_user("user1", "email1@test.com")
        
        with self.assertRaises(ValueError) as context:
            self.user_manager.add_user("user1", "email2@test.com")
        
        self.assertIn("用户名", str(context.exception))
    
    def test_add_duplicate_email(self):
        """测试添加重复邮箱"""
        self.user_manager.add_user("user1", "test@example.com")
        
        with self.assertRaises(ValueError) as context:
            self.user_manager.add_user("user2", "test@example.com")
        
        self.assertIn("邮箱", str(context.exception))
    
    def test_get_all_users(self):
        """测试获取所有用户"""
        self.user_manager.add_user("user1", "user1@test.com")
        self.user_manager.add_user("user2", "user2@test.com")
        self.user_manager.add_user("user3", "user3@test.com")
        
        users = self.user_manager.get_all_users()
        self.assertEqual(len(users), 3)
    
    def test_get_user(self):
        """测试根据ID获取用户"""
        user = self.user_manager.add_user("user1", "user1@test.com")
        user_id = user['user_id']
        
        retrieved_user = self.user_manager.get_user(user_id)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user['username'], "user1")
    
    def test_get_nonexistent_user(self):
        """测试获取不存在的用户"""
        user = self.user_manager.get_user("USER_999999")
        self.assertIsNone(user)
    
    def test_update_user(self):
        """测试更新用户"""
        user = self.user_manager.add_user("user1", "user1@test.com")
        user_id = user['user_id']
        
        result = self.user_manager.update_user(user_id, status="禁用", role="VIP用户")
        self.assertTrue(result)
        
        updated_user = self.user_manager.get_user(user_id)
        self.assertEqual(updated_user['status'], "禁用")
        self.assertEqual(updated_user['role'], "VIP用户")
    
    def test_update_protected_fields(self):
        """测试更新受保护的字段（不应该被更新）"""
        user = self.user_manager.add_user("user1", "user1@test.com")
        user_id = user['user_id']
        original_id = user['user_id']
        original_date = user['register_date']
        
        # 尝试更新受保护的字段
        self.user_manager.update_user(user_id, register_date="2020-01-01")
        
        updated_user = self.user_manager.get_user(user_id)
        # 应该保持原ID和日期不变
        self.assertEqual(updated_user['user_id'], original_id)
        self.assertEqual(updated_user['register_date'], original_date)
    
    def test_delete_user(self):
        """测试删除用户"""
        user = self.user_manager.add_user("user1", "user1@test.com")
        user_id = user['user_id']
        
        result = self.user_manager.delete_user(user_id)
        self.assertTrue(result)
        
        deleted_user = self.user_manager.get_user(user_id)
        self.assertIsNone(deleted_user)
    
    def test_delete_nonexistent_user(self):
        """测试删除不存在的用户"""
        result = self.user_manager.delete_user("USER_999999")
        self.assertFalse(result)
    
    def test_search_users(self):
        """测试搜索用户"""
        self.user_manager.add_user("张三", "zhangsan@test.com", role="管理员")
        self.user_manager.add_user("李四", "lisi@test.com", role="VIP用户")
        self.user_manager.add_user("王五", "wangwu@test.com", role="普通用户")
        
        # 按用户名搜索
        results = self.user_manager.search_users("张三")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], "张三")
        
        # 按邮箱搜索
        results = self.user_manager.search_users("lisi")
        self.assertEqual(len(results), 1)
        
        # 按角色搜索
        results = self.user_manager.search_users("VIP")
        self.assertEqual(len(results), 1)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        self.user_manager.add_user("user1", "user1@test.com", role="管理员", status="活跃")
        self.user_manager.add_user("user2", "user2@test.com", role="VIP用户", status="活跃")
        self.user_manager.add_user("user3", "user3@test.com", role="普通用户", status="禁用")
        self.user_manager.add_user("user4", "user4@test.com", role="普通用户", status="活跃")
        
        stats = self.user_manager.get_statistics()
        
        # 测试基本统计
        self.assertEqual(stats['total_users'], 4)
        self.assertEqual(stats['active_users'], 3)
        
        # 测试付费用户数（验证逻辑：管理员 + VIP用户）
        # 使用显式计算而不是硬编码，使测试更加清晰
        expected_paid = (stats['roles'].get('管理员', 0) + 
                        stats['roles'].get('VIP用户', 0))
        self.assertEqual(stats['paid_users'], expected_paid)
        
        # 测试角色分布
        self.assertEqual(stats['roles']['管理员'], 1)
        self.assertEqual(stats['roles']['VIP用户'], 1)
        self.assertEqual(stats['roles']['普通用户'], 2)
        
        # 测试状态分布
        self.assertEqual(stats['status']['活跃'], 3)
        self.assertEqual(stats['status']['禁用'], 1)
    
    def test_user_id_generation(self):
        """测试用户ID生成"""
        user1 = self.user_manager.add_user("user1", "user1@test.com")
        user2 = self.user_manager.add_user("user2", "user2@test.com")
        user3 = self.user_manager.add_user("user3", "user3@test.com")
        
        # 验证ID格式
        self.assertTrue(user1['user_id'].startswith("USER_"))
        self.assertTrue(user2['user_id'].startswith("USER_"))
        self.assertTrue(user3['user_id'].startswith("USER_"))
        
        # 验证ID递增
        id1 = int(user1['user_id'].split('_')[1])
        id2 = int(user2['user_id'].split('_')[1])
        id3 = int(user3['user_id'].split('_')[1])
        
        self.assertEqual(id2, id1 + 1)
        self.assertEqual(id3, id2 + 1)
    
    def test_data_persistence(self):
        """测试数据持久化"""
        # 添加用户
        self.user_manager.add_user("user1", "user1@test.com")
        
        # 创建新的管理器实例，读取相同的文件
        new_manager = UserManager(data_file=self.temp_file_path)
        users = new_manager.get_all_users()
        
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['username'], "user1")


if __name__ == '__main__':
    unittest.main()
