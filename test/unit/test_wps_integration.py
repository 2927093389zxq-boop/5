"""
WPS Integration Unit Tests
测试WPS集成功能
"""

import unittest
import os
import json
import tempfile
from datetime import datetime
from core.wps_integration import WPSIntegration


class TestWPSIntegration(unittest.TestCase):
    """WPS集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'wps_config_test.json')
        self.wps = WPSIntegration(config_file=self.config_file)
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.wps)
        self.assertIsNotNone(self.wps.session)
        self.assertEqual(self.wps.config, {})
    
    def test_demo_mode_authentication(self):
        """测试演示模式认证"""
        result = self.wps.authenticate("test@example.com", "password")
        
        self.assertTrue(result['success'])
        self.assertTrue(result.get('demo_mode'))
        self.assertEqual(self.wps.config['username'], "test@example.com")
        self.assertTrue(self.wps.config['authenticated'])
        self.assertIsNotNone(self.wps.access_token)
    
    def test_authentication_without_credentials(self):
        """测试没有凭证时的认证"""
        result = self.wps.authenticate("", "")
        
        self.assertFalse(result['success'])
        self.assertIn('不能为空', result['message'])
    
    def test_create_document_demo_mode(self):
        """测试演示模式下创建文档"""
        # 先认证
        self.wps.authenticate("test@example.com", "password")
        
        # 创建文档
        result = self.wps.create_document(
            title="测试文档",
            content="测试内容",
            doc_type="doc"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('document', result)
        
        doc = result['document']
        self.assertEqual(doc['title'], "测试文档")
        self.assertEqual(doc['type'], "doc")
        self.assertIn('doc_id', doc)
        self.assertIn('url', doc)
    
    def test_create_document_without_auth(self):
        """测试未认证时创建文档"""
        result = self.wps.create_document("测试文档", "内容", "doc")
        
        self.assertFalse(result['success'])
        self.assertIn('登录', result['message'])
    
    def test_upload_file_demo_mode(self):
        """测试演示模式下上传文件"""
        # 先认证
        self.wps.authenticate("test@example.com", "password")
        
        # 创建临时测试文件
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # 上传文件
        result = self.wps.upload_file(test_file)
        
        self.assertTrue(result['success'])
        self.assertIn('file', result)
        
        file_info = result['file']
        self.assertEqual(file_info['name'], 'test.txt')
        self.assertIn('file_id', file_info)
        
        # 清理测试文件
        os.remove(test_file)
    
    def test_upload_nonexistent_file(self):
        """测试上传不存在的文件"""
        self.wps.authenticate("test@example.com", "password")
        
        result = self.wps.upload_file("/nonexistent/file.txt")
        
        self.assertFalse(result['success'])
        self.assertIn('不存在', result['message'])
    
    def test_list_documents_demo_mode(self):
        """测试演示模式下列出文档"""
        # 先认证
        self.wps.authenticate("test@example.com", "password")
        
        # 创建几个文档
        self.wps.create_document("文档1", "", "doc")
        self.wps.create_document("文档2", "", "sheet")
        self.wps.create_document("文档3", "", "doc")
        
        # 列出所有文档
        result = self.wps.list_documents()
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 3)
        
        # 按类型过滤
        result = self.wps.list_documents(doc_type="doc")
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
    
    def test_share_document_demo_mode(self):
        """测试演示模式下分享文档"""
        # 先认证
        self.wps.authenticate("test@example.com", "password")
        
        # 创建文档
        doc_result = self.wps.create_document("分享测试文档", "", "doc")
        doc_id = doc_result['document']['doc_id']
        
        # 分享文档
        result = self.wps.share_document(
            doc_id=doc_id,
            users=["user1@example.com", "user2@example.com"],
            permission="edit"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('share', result)
        
        share_info = result['share']
        self.assertEqual(share_info['doc_id'], doc_id)
        self.assertEqual(len(share_info['users']), 2)
        self.assertEqual(share_info['permission'], "edit")
    
    def test_get_user_info(self):
        """测试获取用户信息"""
        # 未认证时
        result = self.wps.get_user_info()
        self.assertFalse(result['success'])
        
        # 认证后
        self.wps.authenticate("test@example.com", "password")
        result = self.wps.get_user_info()
        self.assertTrue(result['success'])
        self.assertIn('user', result)
    
    def test_get_collaboration_info(self):
        """测试获取协作信息"""
        # 先认证并创建一些内容
        self.wps.authenticate("test@example.com", "password")
        self.wps.create_document("文档1", "", "doc")
        
        # 获取协作信息
        result = self.wps.get_collaboration_info()
        
        self.assertTrue(result['success'])
        self.assertIn('stats', result)
        
        stats = result['stats']
        self.assertEqual(stats['total_documents'], 1)
        self.assertEqual(stats['username'], "test@example.com")
    
    def test_logout(self):
        """测试登出"""
        # 先认证
        self.wps.authenticate("test@example.com", "password")
        self.assertTrue(self.wps.config['authenticated'])
        
        # 登出
        result = self.wps.logout()
        
        self.assertTrue(result['success'])
        self.assertFalse(self.wps.config['authenticated'])
        self.assertIsNone(self.wps.access_token)
    
    def test_save_credentials(self):
        """测试保存凭证"""
        result = self.wps.save_credentials(
            username="test@example.com",
            app_id="test_app_id",
            app_secret="test_app_secret"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(self.wps.config['app_id'], "test_app_id")
        self.assertEqual(self.wps.config['app_secret'], "test_app_secret")
    
    def test_get_auth_url(self):
        """测试获取认证URL"""
        # 没有凭证时
        url = self.wps.get_auth_url()
        self.assertEqual(url, "")
        
        # 有凭证时
        self.wps.save_credentials("test", "app_id_123", "secret")
        url = self.wps.get_auth_url("http://localhost:8501")
        
        self.assertIn("authorize", url)
        self.assertIn("app_id_123", url)
        self.assertIn("redirect_uri", url)
    
    def test_config_persistence(self):
        """测试配置持久化"""
        # 认证并创建文档
        self.wps.authenticate("test@example.com", "password")
        self.wps.create_document("持久化测试", "", "doc")
        
        # 创建新实例，应该能读取配置
        wps2 = WPSIntegration(config_file=self.config_file)
        
        self.assertEqual(wps2.config['username'], "test@example.com")
        self.assertTrue(wps2.config['authenticated'])
        self.assertEqual(len(wps2.config['documents']), 1)
    
    def test_environment_variables(self):
        """测试环境变量支持"""
        # 设置环境变量
        os.environ['WPS_APP_ID'] = 'env_app_id'
        os.environ['WPS_APP_SECRET'] = 'env_app_secret'
        
        # 创建新实例
        wps = WPSIntegration(config_file=self.config_file)
        
        # 检查是否读取了环境变量
        self.assertEqual(wps.app_id, 'env_app_id')
        self.assertEqual(wps.app_secret, 'env_app_secret')
        
        # 清理环境变量
        del os.environ['WPS_APP_ID']
        del os.environ['WPS_APP_SECRET']


class TestWPSIntegrationEdgeCases(unittest.TestCase):
    """WPS集成边缘案例测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'wps_config_test.json')
        self.wps = WPSIntegration(config_file=self.config_file)
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_create_document_with_special_characters(self):
        """测试创建包含特殊字符的文档"""
        self.wps.authenticate("test@example.com", "password")
        
        result = self.wps.create_document(
            title="测试文档 @#$%^&*()",
            content="内容包含特殊字符: <>&\"'",
            doc_type="doc"
        )
        
        self.assertTrue(result['success'])
    
    def test_multiple_document_operations(self):
        """测试多个文档操作"""
        self.wps.authenticate("test@example.com", "password")
        
        # 创建多个文档
        doc_ids = []
        for i in range(5):
            result = self.wps.create_document(f"文档{i}", "", "doc")
            doc_ids.append(result['document']['doc_id'])
        
        # 列出文档
        result = self.wps.list_documents()
        self.assertEqual(result['count'], 5)
        
        # 分享所有文档
        for doc_id in doc_ids:
            result = self.wps.share_document(
                doc_id=doc_id,
                users=["user@example.com"],
                permission="view"
            )
            self.assertTrue(result['success'])
    
    def test_invalid_doc_type(self):
        """测试无效的文档类型"""
        self.wps.authenticate("test@example.com", "password")
        
        # 虽然API可能会拒绝，但我们的代码应该能处理
        result = self.wps.create_document("测试", "", "invalid_type")
        # 在演示模式下应该成功
        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
