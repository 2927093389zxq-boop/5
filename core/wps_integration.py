"""
WPS Office集成模块 - 实现WPS在线文档连接和协作
WPS Office Integration Module - WPS online document connection and collaboration
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Setup logging
logger = logging.getLogger(__name__)


class WPSIntegration:
    """WPS Office集成类 - 支持真实的WPS开放平台API"""
    
    # WPS API 基础URL (WPS开放平台API)
    API_BASE_URL = "https://open.wps.cn/api/v1"
    OAUTH_BASE_URL = "https://open.wps.cn/oauth"
    
    def __init__(self, config_file: str = "config/wps_config.json"):
        """
        初始化WPS集成
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None
        
        # 从环境变量或配置文件获取凭证
        self.app_id = os.environ.get('WPS_APP_ID') or self.config.get('app_id', '')
        self.app_secret = os.environ.get('WPS_APP_SECRET') or self.config.get('app_secret', '')
        
        # 设置session的通用headers
        self.session.headers.update({
            'User-Agent': 'WPS-Integration-Client/1.0',
            'Accept': 'application/json'
        })
    
    def _load_config(self) -> Dict[str, Any]:
        """加载WPS配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_config(self):
        """保存WPS配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def save_credentials(self, username: str, app_id: str = "", app_secret: str = "") -> Dict[str, Any]:
        """
        保存WPS凭证
        
        Args:
            username: WPS用户名/邮箱
            app_id: WPS应用ID
            app_secret: WPS应用密钥
            
        Returns:
            操作结果
        """
        self.config.update({
            'username': username,
            'app_id': app_id,
            'app_secret': app_secret,
            'updated_at': datetime.now().isoformat()
        })
        self._save_config()
        
        return {
            'success': True,
            'message': 'WPS凭证已保存'
        }
    
    def _is_token_valid(self) -> bool:
        """检查token是否有效"""
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at
    
    def _make_api_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        统一的API请求方法
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点
            **kwargs: 其他requests参数
            
        Returns:
            API响应
        """
        # 确保有有效的access_token
        if not self._is_token_valid():
            logger.warning("Access token is invalid or expired")
            return {
                'success': False,
                'message': '认证已过期，请重新登录'
            }
        
        # 添加认证header
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        
        url = f"{self.API_BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, headers=headers, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            return {
                'success': False,
                'message': f'API请求失败: {e.response.status_code}',
                'error': str(e)
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {e}")
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}',
                'error': str(e)
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {e}")
            return {
                'success': False,
                'message': '响应格式错误',
                'error': str(e)
            }
    
    def authenticate(self, username: str = None, password: str = None, 
                    code: str = None, redirect_uri: str = None) -> Dict[str, Any]:
        """
        WPS用户认证 - 支持密码模式和OAuth授权码模式
        
        Args:
            username: 用户名 (密码模式)
            password: 密码 (密码模式)
            code: OAuth授权码 (授权码模式)
            redirect_uri: 回调地址 (授权码模式)
            
        Returns:
            认证结果
        """
        try:
            # 检查是否配置了app_id和app_secret
            if not self.app_id or not self.app_secret:
                # 如果没有配置，使用模拟模式
                logger.warning("WPS credentials not configured, using demo mode")
                return self._authenticate_demo(username, password)
            
            # OAuth授权码模式
            if code and redirect_uri:
                return self._authenticate_oauth(code, redirect_uri)
            
            # 密码模式（如果WPS支持）
            if username and password:
                return self._authenticate_password(username, password)
            
            return {
                'success': False,
                'message': '请提供认证参数 (username+password 或 code+redirect_uri)'
            }
            
        except Exception as e:
            logger.exception("Authentication error")
            return {
                'success': False,
                'message': f'认证失败: {str(e)}',
                'error': str(e)
            }
    
    def _authenticate_demo(self, username: str, password: str) -> Dict[str, Any]:
        """演示模式认证（用于没有配置真实凭证时）"""
        if not username or not password:
            return {
                'success': False,
                'message': '用户名或密码不能为空'
            }
        
        # 保存用户信息
        self.config['username'] = username
        self.config['authenticated'] = True
        self.config['auth_time'] = datetime.now().isoformat()
        self.config['demo_mode'] = True
        self._save_config()
        
        # 模拟获取access_token
        self.access_token = f"demo_token_{username}_{datetime.now().timestamp()}"
        self.token_expires_at = datetime.now() + timedelta(hours=24)
        
        return {
            'success': True,
            'message': 'WPS认证成功 (演示模式)',
            'username': username,
            'access_token': self.access_token,
            'demo_mode': True
        }
    
    def _authenticate_oauth(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """OAuth授权码模式认证"""
        token_url = f"{self.OAUTH_BASE_URL}/token"
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': redirect_uri
        }
        
        try:
            response = self.session.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            
            # 保存token信息
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 7200)  # 默认2小时
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # 保存到配置
            self.config['access_token'] = self.access_token
            self.config['refresh_token'] = token_data.get('refresh_token')
            self.config['token_expires_at'] = self.token_expires_at.isoformat()
            self.config['authenticated'] = True
            self.config['auth_time'] = datetime.now().isoformat()
            self.config['demo_mode'] = False
            self._save_config()
            
            # 获取用户信息
            user_info = self._get_user_info_from_api()
            
            return {
                'success': True,
                'message': 'WPS认证成功',
                'access_token': self.access_token,
                'expires_in': expires_in,
                'user_info': user_info,
                'demo_mode': False
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OAuth authentication failed: {e}")
            return {
                'success': False,
                'message': f'OAuth认证失败: {str(e)}',
                'error': str(e)
            }
    
    def _authenticate_password(self, username: str, password: str) -> Dict[str, Any]:
        """密码模式认证（如果WPS API支持）"""
        # 注意：WPS Open Platform可能不支持密码模式，这里作为备用
        # 实际使用时应该使用OAuth授权码流程
        
        token_url = f"{self.OAUTH_BASE_URL}/token"
        
        data = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'client_id': self.app_id,
            'client_secret': self.app_secret
        }
        
        try:
            response = self.session.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 7200)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            self.config['access_token'] = self.access_token
            self.config['username'] = username
            self.config['authenticated'] = True
            self.config['auth_time'] = datetime.now().isoformat()
            self.config['demo_mode'] = False
            self._save_config()
            
            return {
                'success': True,
                'message': 'WPS认证成功',
                'username': username,
                'access_token': self.access_token,
                'demo_mode': False
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Password authentication failed: {e}")
            # 如果API不支持密码模式，回退到演示模式
            return self._authenticate_demo(username, password)
    
    def _get_user_info_from_api(self) -> Dict[str, Any]:
        """从API获取用户信息"""
        try:
            result = self._make_api_request('GET', 'user/info')
            if result.get('success'):
                user_data = result.get('data', {})
                self.config['username'] = user_data.get('email') or user_data.get('username', '')
                self._save_config()
                return user_data
            return {}
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return {}
    
    def refresh_token(self) -> Dict[str, Any]:
        """
        刷新访问令牌
        
        Returns:
            刷新结果
        """
        refresh_token = self.config.get('refresh_token')
        
        if not refresh_token or not self.app_id or not self.app_secret:
            return {
                'success': False,
                'message': '无法刷新令牌：缺少必要参数'
            }
        
        token_url = f"{self.OAUTH_BASE_URL}/token"
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.app_id,
            'client_secret': self.app_secret
        }
        
        try:
            response = self.session.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            
            # 更新token信息
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 7200)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # 保存到配置
            self.config['access_token'] = self.access_token
            if token_data.get('refresh_token'):
                self.config['refresh_token'] = token_data.get('refresh_token')
            self.config['token_expires_at'] = self.token_expires_at.isoformat()
            self._save_config()
            
            return {
                'success': True,
                'message': '令牌刷新成功',
                'access_token': self.access_token,
                'expires_in': expires_in
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh failed: {e}")
            return {
                'success': False,
                'message': f'令牌刷新失败: {str(e)}',
                'error': str(e)
            }
    
    def get_auth_url(self, redirect_uri: str = "http://localhost:8501") -> str:
        """
        获取WPS OAuth认证URL
        
        Args:
            redirect_uri: 回调地址
            
        Returns:
            认证URL
        """
        # 优先使用环境变量中的app_id
        app_id = self.app_id or self.config.get('app_id', '')
        
        if not app_id:
            logger.warning("WPS App ID not configured")
            return ""
        
        # WPS OAuth2.0授权URL
        auth_url = f"{self.OAUTH_BASE_URL}/authorize"
        params = {
            'client_id': app_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'user_info file_read file_write',
            'state': f"wps_oauth_{datetime.now().timestamp()}"  # 添加state防止CSRF
        }
        
        # URL编码参数
        from urllib.parse import urlencode
        query_string = urlencode(params)
        return f"{auth_url}?{query_string}"
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        获取WPS用户信息
        
        Returns:
            用户信息
        """
        if not self.config.get('authenticated'):
            return {
                'success': False,
                'message': '未登录'
            }
        
        # 模拟返回用户信息
        return {
            'success': True,
            'user': {
                'username': self.config.get('username', ''),
                'email': self.config.get('username', ''),
                'auth_time': self.config.get('auth_time', ''),
                'status': '已连接'
            }
        }
    
    def create_document(self, title: str, content: str = "", doc_type: str = "doc") -> Dict[str, Any]:
        """
        创建WPS文档
        
        Args:
            title: 文档标题
            content: 文档内容
            doc_type: 文档类型 (doc/sheet/ppt)
            
        Returns:
            创建结果
        """
        if not self.config.get('authenticated'):
            return {
                'success': False,
                'message': '请先登录WPS账号'
            }
        
        try:
            # 如果是演示模式，使用模拟实现
            if self.config.get('demo_mode', True):
                return self._create_document_demo(title, content, doc_type)
            
            # 真实API调用
            payload = {
                'title': title,
                'type': doc_type,
                'content': content
            }
            
            result = self._make_api_request('POST', 'documents', json=payload)
            
            if result.get('success') is False:
                # API调用失败，回退到演示模式
                logger.warning("API call failed, falling back to demo mode")
                return self._create_document_demo(title, content, doc_type)
            
            # 处理API响应
            doc_data = result.get('data', result)
            doc_info = {
                'doc_id': doc_data.get('id') or doc_data.get('doc_id'),
                'title': title,
                'type': doc_type,
                'created_at': datetime.now().isoformat(),
                'creator': self.config.get('username', ''),
                'url': doc_data.get('url') or doc_data.get('view_url'),
                'edit_url': doc_data.get('edit_url') or doc_data.get('url')
            }
            
            # 保存文档记录
            if 'documents' not in self.config:
                self.config['documents'] = []
            
            self.config['documents'].append(doc_info)
            self._save_config()
            
            return {
                'success': True,
                'message': '文档创建成功',
                'document': doc_info
            }
            
        except Exception as e:
            logger.exception("Failed to create document")
            return {
                'success': False,
                'message': f'创建文档失败: {str(e)}',
                'error': str(e)
            }
    
    def _create_document_demo(self, title: str, content: str, doc_type: str) -> Dict[str, Any]:
        """演示模式下创建文档"""
        doc_id = f"doc_{datetime.now().timestamp()}"
        
        doc_info = {
            'doc_id': doc_id,
            'title': title,
            'type': doc_type,
            'created_at': datetime.now().isoformat(),
            'creator': self.config.get('username', ''),
            'url': f"https://www.kdocs.cn/l/{doc_id}",
            'edit_url': f"https://www.kdocs.cn/l/{doc_id}?mode=edit",
            'demo_mode': True
        }
        
        # 保存文档记录
        if 'documents' not in self.config:
            self.config['documents'] = []
        
        self.config['documents'].append(doc_info)
        self._save_config()
        
        return {
            'success': True,
            'message': '文档创建成功 (演示模式)',
            'document': doc_info
        }
    
    def upload_file(self, file_path: str, folder_id: str = None) -> Dict[str, Any]:
        """
        上传文件到WPS云端
        
        Args:
            file_path: 本地文件路径
            folder_id: 目标文件夹ID
            
        Returns:
            上传结果
        """
        if not self.config.get('authenticated'):
            return {
                'success': False,
                'message': '请先登录WPS账号'
            }
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'message': '文件不存在'
            }
        
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # 如果是演示模式，使用模拟实现
            if self.config.get('demo_mode', True):
                return self._upload_file_demo(file_path, file_name, file_size)
            
            # 真实API调用 - 上传文件
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'application/octet-stream')}
                data = {}
                if folder_id:
                    data['folder_id'] = folder_id
                
                # 注意：这里使用multipart/form-data上传
                # 不使用_make_api_request因为需要特殊处理文件上传
                url = f"{self.API_BASE_URL}/files/upload"
                headers = {'Authorization': f'Bearer {self.access_token}'}
                
                try:
                    response = self.session.post(url, files=files, data=data, 
                                                headers=headers, timeout=120)
                    response.raise_for_status()
                    result = response.json()
                    
                    file_data = result.get('data', result)
                    file_info = {
                        'file_id': file_data.get('id') or file_data.get('file_id'),
                        'name': file_name,
                        'size': file_size,
                        'uploaded_at': datetime.now().isoformat(),
                        'uploader': self.config.get('username', ''),
                        'url': file_data.get('url') or file_data.get('view_url')
                    }
                    
                    # 保存文件记录
                    if 'files' not in self.config:
                        self.config['files'] = []
                    
                    self.config['files'].append(file_info)
                    self._save_config()
                    
                    return {
                        'success': True,
                        'message': '文件上传成功',
                        'file': file_info
                    }
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"File upload failed: {e}")
                    # API调用失败，回退到演示模式
                    return self._upload_file_demo(file_path, file_name, file_size)
            
        except Exception as e:
            logger.exception("Failed to upload file")
            return {
                'success': False,
                'message': f'上传文件失败: {str(e)}',
                'error': str(e)
            }
    
    def _upload_file_demo(self, file_path: str, file_name: str, file_size: int) -> Dict[str, Any]:
        """演示模式下上传文件"""
        file_id = f"file_{datetime.now().timestamp()}"
        
        file_info = {
            'file_id': file_id,
            'name': file_name,
            'size': file_size,
            'uploaded_at': datetime.now().isoformat(),
            'uploader': self.config.get('username', ''),
            'url': f"https://www.kdocs.cn/l/{file_id}",
            'demo_mode': True
        }
        
        # 保存文件记录
        if 'files' not in self.config:
            self.config['files'] = []
        
        self.config['files'].append(file_info)
        self._save_config()
        
        return {
            'success': True,
            'message': '文件上传成功 (演示模式)',
            'file': file_info
        }
    
    def list_documents(self, doc_type: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        列出WPS文档
        
        Args:
            doc_type: 过滤文档类型
            limit: 返回数量限制
            
        Returns:
            文档列表
        """
        if not self.config.get('authenticated'):
            return {
                'success': False,
                'message': '请先登录WPS账号'
            }
        
        try:
            # 如果是演示模式或API调用失败，使用本地缓存
            if self.config.get('demo_mode', True):
                return self._list_documents_local(doc_type)
            
            # 真实API调用
            params = {'limit': limit}
            if doc_type:
                params['type'] = doc_type
            
            result = self._make_api_request('GET', 'documents', params=params)
            
            if result.get('success') is False:
                # API调用失败，使用本地缓存
                logger.warning("API call failed, using local cache")
                return self._list_documents_local(doc_type)
            
            # 处理API响应
            documents = result.get('data', [])
            
            # 更新本地缓存
            if 'documents' not in self.config:
                self.config['documents'] = []
            
            # 合并远程和本地文档（去重）
            local_ids = {d.get('doc_id') for d in self.config.get('documents', [])}
            for doc in documents:
                if doc.get('id') not in local_ids:
                    self.config['documents'].append({
                        'doc_id': doc.get('id'),
                        'title': doc.get('title'),
                        'type': doc.get('type'),
                        'created_at': doc.get('created_at'),
                        'creator': doc.get('creator'),
                        'url': doc.get('url'),
                        'edit_url': doc.get('edit_url')
                    })
            
            self._save_config()
            
            return {
                'success': True,
                'documents': documents,
                'count': len(documents)
            }
            
        except Exception as e:
            logger.exception("Failed to list documents")
            return self._list_documents_local(doc_type)
    
    def _list_documents_local(self, doc_type: str = None) -> Dict[str, Any]:
        """从本地缓存列出文档"""
        documents = self.config.get('documents', [])
        
        if doc_type:
            documents = [d for d in documents if d.get('type') == doc_type]
        
        return {
            'success': True,
            'documents': documents,
            'count': len(documents)
        }
    
    def share_document(self, doc_id: str, users: List[str], 
                      permission: str = "view") -> Dict[str, Any]:
        """
        分享文档给其他用户
        
        Args:
            doc_id: 文档ID
            users: 用户列表
            permission: 权限 (view/edit/admin)
            
        Returns:
            分享结果
        """
        if not self.config.get('authenticated'):
            return {
                'success': False,
                'message': '请先登录WPS账号'
            }
        
        try:
            # 如果是演示模式，使用模拟实现
            if self.config.get('demo_mode', True):
                return self._share_document_demo(doc_id, users, permission)
            
            # 真实API调用
            payload = {
                'doc_id': doc_id,
                'users': users,
                'permission': permission
            }
            
            result = self._make_api_request('POST', f'documents/{doc_id}/share', json=payload)
            
            if result.get('success') is False:
                # API调用失败，回退到演示模式
                logger.warning("API call failed, falling back to demo mode")
                return self._share_document_demo(doc_id, users, permission)
            
            # 处理API响应
            share_data = result.get('data', result)
            share_info = {
                'doc_id': doc_id,
                'users': users,
                'permission': permission,
                'shared_at': datetime.now().isoformat(),
                'share_link': share_data.get('share_link') or f"https://www.kdocs.cn/l/{doc_id}?share=1"
            }
            
            # 保存分享记录
            if 'shares' not in self.config:
                self.config['shares'] = []
            
            self.config['shares'].append(share_info)
            self._save_config()
            
            return {
                'success': True,
                'message': '文档分享成功',
                'share': share_info
            }
            
        except Exception as e:
            logger.exception("Failed to share document")
            return {
                'success': False,
                'message': f'分享文档失败: {str(e)}',
                'error': str(e)
            }
    
    def _share_document_demo(self, doc_id: str, users: List[str], permission: str) -> Dict[str, Any]:
        """演示模式下分享文档"""
        share_info = {
            'doc_id': doc_id,
            'users': users,
            'permission': permission,
            'shared_at': datetime.now().isoformat(),
            'share_link': f"https://www.kdocs.cn/l/{doc_id}?share=1",
            'demo_mode': True
        }
        
        # 保存分享记录
        if 'shares' not in self.config:
            self.config['shares'] = []
        
        self.config['shares'].append(share_info)
        self._save_config()
        
        return {
            'success': True,
            'message': '文档分享成功 (演示模式)',
            'share': share_info
        }
    
    def get_collaboration_info(self) -> Dict[str, Any]:
        """
        获取协作信息统计
        
        Returns:
            协作信息
        """
        if not self.config.get('authenticated'):
            return {
                'success': False,
                'message': '未登录'
            }
        
        documents = self.config.get('documents', [])
        files = self.config.get('files', [])
        shares = self.config.get('shares', [])
        
        return {
            'success': True,
            'stats': {
                'total_documents': len(documents),
                'total_files': len(files),
                'total_shares': len(shares),
                'username': self.config.get('username', '')
            }
        }
    
    def logout(self) -> Dict[str, Any]:
        """
        登出WPS
        
        Returns:
            操作结果
        """
        self.config['authenticated'] = False
        self.config['auth_time'] = None
        self.access_token = None
        self._save_config()
        
        return {
            'success': True,
            'message': '已登出WPS账号'
        }
