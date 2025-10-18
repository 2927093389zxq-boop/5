#!/usr/bin/env python
"""
企业功能演示脚本 - Enterprise Features Demo Script
展示如何通过代码使用新增的企业功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.crawler_manager import CrawlerManager
from core.wps_integration import WPSIntegration
from core.ai_model_manager import AIModelManager
from core.collaboration_manager import CollaborationManager


def demo_crawler_management():
    """演示爬虫管理功能"""
    print("\n" + "="*60)
    print("1. 爬虫管理中心演示 - Crawler Management Demo")
    print("="*60)
    
    manager = CrawlerManager()
    
    # 添加示例爬虫
    sample_crawler = """
import requests
from bs4 import BeautifulSoup

def scrape(url, max_items=10, **kwargs):
    '''简单的网页爬虫示例'''
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 提取标题（示例）
        items = []
        for item in soup.select('h1, h2, h3')[:max_items]:
            items.append({
                'title': item.text.strip(),
                'tag': item.name
            })
        
        return {
            'success': True,
            'data': items,
            'count': len(items),
            'url': url
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': []
        }
"""
    
    print("\n📝 添加爬虫...")
    result = manager.add_crawler(
        name="demo_crawler",
        code=sample_crawler,
        description="演示爬虫 - 提取网页标题",
        platform="custom"
    )
    print(f"   结果: {result['message']}")
    
    print("\n📋 列出所有爬虫...")
    crawlers = manager.list_crawlers()
    print(f"   总数: {len(crawlers)}")
    for crawler in crawlers:
        print(f"   - {crawler['name']} ({crawler['platform']})")
    
    print("\n🚀 执行爬虫...")
    print("   (模拟执行，实际使用需要提供真实URL)")
    # result = manager.execute_crawler("demo_crawler", url="https://example.com")
    # print(f"   结果: {result['message']}")


def demo_wps_integration():
    """演示WPS集成功能"""
    print("\n" + "="*60)
    print("2. WPS Office 集成演示 - WPS Integration Demo")
    print("="*60)
    
    wps = WPSIntegration()
    
    print("\n🔐 WPS账号认证...")
    result = wps.authenticate("demo_user@example.com", "demo_password")
    print(f"   结果: {result['message']}")
    
    print("\n📄 创建在线文档...")
    result = wps.create_document(
        title="项目计划书",
        content="这是一个示例文档的初始内容",
        doc_type="doc"
    )
    if result['success']:
        print(f"   结果: {result['message']}")
        print(f"   文档URL: {result['document']['url']}")
    
    print("\n📤 模拟上传文件...")
    print("   (实际使用需要提供真实文件路径)")
    # result = wps.upload_file("/path/to/file.docx")
    
    print("\n📊 获取协作统计...")
    stats = wps.get_collaboration_info()
    if stats['success']:
        print(f"   文档数: {stats['stats']['total_documents']}")
        print(f"   文件数: {stats['stats']['total_files']}")


def demo_ai_model_management():
    """演示AI模型管理功能"""
    print("\n" + "="*60)
    print("3. AI模型集成管理演示 - AI Model Management Demo")
    print("="*60)
    
    manager = AIModelManager()
    
    print("\n📚 支持的AI提供商...")
    providers = manager.list_providers()
    print(f"   总数: {len(providers)}")
    for provider in providers[:5]:
        print(f"   - {provider['name']} (支持模型: {', '.join(provider['models'][:2])}...)")
    
    print("\n➕ 添加AI模型配置...")
    print("   (使用测试密钥)")
    result = manager.add_model(
        provider="openai",
        model_name="gpt-3.5-turbo",
        api_key="sk-test-key-for-demo-only",
        description="演示用GPT-3.5模型"
    )
    print(f"   结果: {result['message']}")
    
    print("\n📋 列出已配置的模型...")
    models = manager.list_models()
    print(f"   总数: {len(models)}")
    for model in models:
        print(f"   - {model['provider_name']} / {model['model_name']}")
    
    print("\n🧪 测试模型连接...")
    print("   (需要有效的API密钥才能真正测试)")
    # result = manager.test_model(model_id, "Hello")


def demo_collaboration():
    """演示企业协作功能"""
    print("\n" + "="*60)
    print("4. 企业协作功能演示 - Enterprise Collaboration Demo")
    print("="*60)
    
    manager = CollaborationManager()
    
    print("\n👤 添加团队成员...")
    users_data = [
        ("张三", "zhangsan@company.com", "manager", "产品部"),
        ("李四", "lisi@company.com", "member", "开发部"),
        ("王五", "wangwu@company.com", "member", "开发部"),
    ]
    
    user_ids = []
    for username, email, role, dept in users_data:
        result = manager.add_user(username, email, role, dept)
        if result['success']:
            print(f"   添加: {username} ({role})")
            user_ids.append(result['user']['id'])
    
    print("\n👥 创建团队...")
    result = manager.create_team(
        name="产品研发团队",
        description="负责新产品的研发工作",
        leader_id=user_ids[0] if user_ids else None,
        members=user_ids[1:] if len(user_ids) > 1 else []
    )
    if result['success']:
        print(f"   结果: {result['message']}")
        team_id = result['team']['id']
    
    print("\n📁 创建项目...")
    result = manager.create_project(
        name="Q1新产品开发",
        description="2025年第一季度新产品开发项目",
        team_id=team_id if 'team_id' in locals() else None,
        status="active",
        priority="high"
    )
    if result['success']:
        print(f"   结果: {result['message']}")
        project_id = result['project']['id']
    
    print("\n✅ 创建任务...")
    tasks_data = [
        ("需求分析", "完成产品需求分析文档", "high", "todo"),
        ("UI设计", "设计产品界面原型", "medium", "todo"),
        ("后端开发", "开发后端API接口", "high", "in_progress"),
    ]
    
    for title, desc, priority, status in tasks_data:
        result = manager.create_task(
            title=title,
            description=desc,
            project_id=project_id if 'project_id' in locals() else None,
            assignee_id=user_ids[1] if len(user_ids) > 1 else None,
            priority=priority,
            status=status
        )
        if result['success']:
            print(f"   创建: {title} [{status}]")
    
    print("\n💬 发送团队消息...")
    if len(user_ids) >= 2:
        result = manager.send_message(
            sender_id=user_ids[0],
            receiver_id=user_ids[1],
            content="请查看最新的项目任务分配"
        )
        if result['success']:
            print(f"   结果: {result['message']}")
    
    print("\n📊 获取协作统计...")
    stats = manager.get_stats()
    print(f"   用户数: {stats['total_users']}")
    print(f"   团队数: {stats['total_teams']}")
    print(f"   项目数: {stats['total_projects']}")
    print(f"   任务数: {stats['total_tasks']}")
    print(f"   待办任务: {stats['pending_tasks']}")


def main():
    """主函数"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     京盛传媒企业版智能体 - 企业功能演示                  ║")
    print("║     Enterprise Features Demo                              ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    try:
        # 演示各个功能
        demo_crawler_management()
        demo_wps_integration()
        demo_ai_model_management()
        demo_collaboration()
        
        print("\n" + "="*60)
        print("✅ 所有演示完成！")
        print("="*60)
        
        print("\n💡 提示:")
        print("   1. 启动Web界面查看完整功能: streamlit run run_launcher.py")
        print("   2. 查看详细文档: ENTERPRISE_FEATURES.md")
        print("   3. 在Web界面中可以进行完整的交互操作")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
