"""
AI模型集成管理模块 - 统一管理多个AI模型接入
AI Model Integration Manager - Unified management of multiple AI model integrations
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests


class AIModelManager:
    """AI模型管理器 - 统一管理各种AI模型的接入"""
    
    # 支持的AI模型提供商
    SUPPORTED_PROVIDERS = {
        'openai': {
            'name': 'OpenAI',
            'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'],
            'api_base': 'https://api.openai.com/v1',
            'endpoints': {
                'chat': '/chat/completions',
                'completion': '/completions',
                'embedding': '/embeddings'
            }
        },
        'anthropic': {
            'name': 'Anthropic (Claude)',
            'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku', 'claude-2.1'],
            'api_base': 'https://api.anthropic.com/v1',
            'endpoints': {
                'messages': '/messages'
            }
        },
        'google': {
            'name': 'Google AI (Gemini)',
            'models': ['gemini-pro', 'gemini-pro-vision', 'gemini-ultra'],
            'api_base': 'https://generativelanguage.googleapis.com/v1beta',
            'endpoints': {
                'generate': '/models/{model}:generateContent'
            }
        },
        'cohere': {
            'name': 'Cohere',
            'models': ['command', 'command-light', 'command-nightly'],
            'api_base': 'https://api.cohere.ai/v1',
            'endpoints': {
                'generate': '/generate',
                'chat': '/chat',
                'embed': '/embed'
            }
        },
        'huggingface': {
            'name': 'HuggingFace',
            'models': ['custom'],  # 支持用户自定义模型
            'api_base': 'https://api-inference.huggingface.co/models',
            'endpoints': {
                'inference': '/{model}'
            }
        },
        'azure_openai': {
            'name': 'Azure OpenAI',
            'models': ['gpt-4', 'gpt-35-turbo'],
            'api_base': 'https://{resource}.openai.azure.com',
            'endpoints': {
                'chat': '/openai/deployments/{deployment}/chat/completions'
            }
        },
        'deepseek': {
            'name': 'DeepSeek',
            'models': ['deepseek-chat', 'deepseek-coder'],
            'api_base': 'https://api.deepseek.com/v1',
            'endpoints': {
                'chat': '/chat/completions'
            }
        },
        'moonshot': {
            'name': 'Moonshot AI (月之暗面)',
            'models': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
            'api_base': 'https://api.moonshot.cn/v1',
            'endpoints': {
                'chat': '/chat/completions'
            }
        },
        'zhipu': {
            'name': 'Zhipu AI (智谱)',
            'models': ['glm-4', 'glm-3-turbo'],
            'api_base': 'https://open.bigmodel.cn/api/paas/v4',
            'endpoints': {
                'chat': '/chat/completions'
            }
        },
        'baidu': {
            'name': 'Baidu (文心一言)',
            'models': ['ernie-bot-4', 'ernie-bot-turbo', 'ernie-bot'],
            'api_base': 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1',
            'endpoints': {
                'chat': '/wenxinworkshop/chat/{model}'
            }
        }
    }
    
    def __init__(self, config_file: str = "config/ai_models_config.json"):
        """
        初始化AI模型管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.models = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载AI模型配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_config(self):
        """保存AI模型配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.models, f, ensure_ascii=False, indent=2)
    
    def add_model(self, provider: str, model_name: str, api_key: str,
                 custom_endpoint: str = None, **kwargs) -> Dict[str, Any]:
        """
        添加AI模型配置
        
        Args:
            provider: 提供商（如 'openai', 'anthropic'）
            model_name: 模型名称
            api_key: API密钥
            custom_endpoint: 自定义端点（可选）
            **kwargs: 其他配置参数
            
        Returns:
            操作结果
        """
        if provider not in self.SUPPORTED_PROVIDERS:
            return {
                'success': False,
                'message': f'不支持的提供商: {provider}'
            }
        
        model_id = f"{provider}_{model_name}_{datetime.now().timestamp()}"
        
        provider_info = self.SUPPORTED_PROVIDERS[provider]
        
        model_config = {
            'id': model_id,
            'provider': provider,
            'provider_name': provider_info['name'],
            'model_name': model_name,
            'api_key': api_key,
            'api_base': custom_endpoint or provider_info['api_base'],
            'endpoints': provider_info['endpoints'],
            'enabled': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            **kwargs
        }
        
        self.models[model_id] = model_config
        self._save_config()
        
        return {
            'success': True,
            'message': f'AI模型 {provider_info["name"]} - {model_name} 添加成功',
            'model': model_config
        }
    
    def update_model(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """
        更新AI模型配置
        
        Args:
            model_id: 模型ID
            **kwargs: 要更新的字段
            
        Returns:
            操作结果
        """
        if model_id not in self.models:
            return {
                'success': False,
                'message': f'模型不存在: {model_id}'
            }
        
        # 更新配置
        self.models[model_id].update(kwargs)
        self.models[model_id]['updated_at'] = datetime.now().isoformat()
        self._save_config()
        
        return {
            'success': True,
            'message': '模型配置更新成功',
            'model': self.models[model_id]
        }
    
    def delete_model(self, model_id: str) -> Dict[str, Any]:
        """
        删除AI模型配置
        
        Args:
            model_id: 模型ID
            
        Returns:
            操作结果
        """
        if model_id not in self.models:
            return {
                'success': False,
                'message': f'模型不存在: {model_id}'
            }
        
        del self.models[model_id]
        self._save_config()
        
        return {
            'success': True,
            'message': '模型配置删除成功'
        }
    
    def list_models(self, provider: str = None, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        列出AI模型配置
        
        Args:
            provider: 过滤提供商
            enabled_only: 只返回启用的模型
            
        Returns:
            模型列表
        """
        models = list(self.models.values())
        
        if provider:
            models = [m for m in models if m.get('provider') == provider]
        
        if enabled_only:
            models = [m for m in models if m.get('enabled', True)]
        
        return models
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        获取AI模型配置
        
        Args:
            model_id: 模型ID
            
        Returns:
            模型配置
        """
        return self.models.get(model_id)
    
    def test_model(self, model_id: str, test_prompt: str = "Hello") -> Dict[str, Any]:
        """
        测试AI模型连接
        
        Args:
            model_id: 模型ID
            test_prompt: 测试提示词
            
        Returns:
            测试结果
        """
        if model_id not in self.models:
            return {
                'success': False,
                'message': '模型不存在'
            }
        
        model = self.models[model_id]
        provider = model['provider']
        
        try:
            # 根据不同提供商执行测试
            if provider == 'openai' or provider == 'azure_openai':
                return self._test_openai_compatible(model, test_prompt)
            elif provider == 'anthropic':
                return self._test_anthropic(model, test_prompt)
            elif provider == 'google':
                return self._test_google(model, test_prompt)
            else:
                # 通用测试
                return self._test_generic(model, test_prompt)
        
        except Exception as e:
            return {
                'success': False,
                'message': f'测试失败: {str(e)}',
                'error': str(e)
            }
    
    def _test_openai_compatible(self, model: Dict, test_prompt: str) -> Dict[str, Any]:
        """测试OpenAI兼容的API"""
        api_base = model['api_base']
        api_key = model['api_key']
        model_name = model['model_name']
        
        url = f"{api_base}/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model_name,
            'messages': [{'role': 'user', 'content': test_prompt}],
            'max_tokens': 10
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': '模型连接测试成功',
                'response': response.json()
            }
        else:
            return {
                'success': False,
                'message': f'测试失败: HTTP {response.status_code}',
                'error': response.text
            }
    
    def _test_anthropic(self, model: Dict, test_prompt: str) -> Dict[str, Any]:
        """测试Anthropic API"""
        api_base = model['api_base']
        api_key = model['api_key']
        model_name = model['model_name']
        
        url = f"{api_base}/messages"
        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model_name,
            'messages': [{'role': 'user', 'content': test_prompt}],
            'max_tokens': 10
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': '模型连接测试成功',
                'response': response.json()
            }
        else:
            return {
                'success': False,
                'message': f'测试失败: HTTP {response.status_code}',
                'error': response.text
            }
    
    def _test_google(self, model: Dict, test_prompt: str) -> Dict[str, Any]:
        """测试Google AI API"""
        # 简化版测试
        return {
            'success': True,
            'message': '配置已保存（需要实际API密钥进行完整测试）'
        }
    
    def _test_generic(self, model: Dict, test_prompt: str) -> Dict[str, Any]:
        """通用测试"""
        return {
            'success': True,
            'message': '配置已保存（需要根据具体API文档进行测试）'
        }
    
    def get_provider_info(self, provider: str) -> Optional[Dict[str, Any]]:
        """
        获取提供商信息
        
        Args:
            provider: 提供商名称
            
        Returns:
            提供商信息
        """
        return self.SUPPORTED_PROVIDERS.get(provider)
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """
        列出所有支持的提供商
        
        Returns:
            提供商列表
        """
        return [
            {
                'id': key,
                'name': info['name'],
                'models': info['models'],
                'api_base': info['api_base']
            }
            for key, info in self.SUPPORTED_PROVIDERS.items()
        ]
