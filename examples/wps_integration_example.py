"""
WPS Office集成示例 / WPS Office Integration Example

本示例展示如何使用WPS集成功能
This example demonstrates how to use WPS integration features
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.wps_integration import WPSIntegration


def example_demo_mode():
    """示例1：演示模式使用 / Example 1: Demo Mode Usage"""
    print("\n" + "="*60)
    print("示例1：演示模式 (无需配置)")
    print("Example 1: Demo Mode (No configuration required)")
    print("="*60)
    
    # 创建WPS集成实例
    wps = WPSIntegration()
    
    # 1. 认证登录（演示模式）
    print("\n1. 用户认证...")
    result = wps.authenticate("demo@example.com", "demo_password")
    print(f"   结果: {result['message']}")
    print(f"   模式: {'演示模式' if result.get('demo_mode') else '生产模式'}")
    
    if result['success']:
        # 2. 创建文档
        print("\n2. 创建Word文档...")
        result = wps.create_document(
            title="项目需求文档",
            content="这是一个示例文档的初始内容",
            doc_type="doc"
        )
        print(f"   结果: {result['message']}")
        if result['success']:
            doc = result['document']
            print(f"   文档ID: {doc['doc_id']}")
            print(f"   文档URL: {doc['url']}")
        
        # 3. 创建Excel表格
        print("\n3. 创建Excel表格...")
        result = wps.create_document(
            title="数据统计表",
            doc_type="sheet"
        )
        print(f"   结果: {result['message']}")
        
        # 4. 列出所有文档
        print("\n4. 列出所有文档...")
        result = wps.list_documents()
        print(f"   文档总数: {result['count']}")
        for doc in result['documents']:
            print(f"   - {doc['title']} ({doc['type']})")
        
        # 5. 分享文档
        print("\n5. 分享文档...")
        if result['documents']:
            doc_id = result['documents'][0]['doc_id']
            result = wps.share_document(
                doc_id=doc_id,
                users=["user1@example.com", "user2@example.com"],
                permission="edit"
            )
            print(f"   结果: {result['message']}")
            if result['success']:
                print(f"   分享链接: {result['share']['share_link']}")
        
        # 6. 获取协作统计
        print("\n6. 获取协作统计...")
        stats = wps.get_collaboration_info()
        if stats['success']:
            print(f"   文档数: {stats['stats']['total_documents']}")
            print(f"   文件数: {stats['stats']['total_files']}")
            print(f"   分享数: {stats['stats']['total_shares']}")


def example_production_mode():
    """示例2：生产模式使用 / Example 2: Production Mode Usage"""
    print("\n" + "="*60)
    print("示例2：生产模式 (需要配置WPS API凭证)")
    print("Example 2: Production Mode (Requires WPS API credentials)")
    print("="*60)
    
    # 检查环境变量
    app_id = os.environ.get('WPS_APP_ID')
    app_secret = os.environ.get('WPS_APP_SECRET')
    
    if not app_id or not app_secret:
        print("\n⚠️  未检测到WPS API凭证")
        print("请设置环境变量：")
        print("  export WPS_APP_ID='your-app-id'")
        print("  export WPS_APP_SECRET='your-app-secret'")
        print("\n详细配置说明请查看: docs/WPS_INTEGRATION_GUIDE.md")
        return
    
    print(f"\n✅ 检测到WPS凭证")
    print(f"   App ID: {app_id[:8]}...")
    
    wps = WPSIntegration()
    
    # 1. OAuth授权URL
    print("\n1. 生成OAuth授权URL...")
    auth_url = wps.get_auth_url("http://localhost:8501")
    if auth_url:
        print(f"   授权URL: {auth_url}")
        print("\n   请访问上述URL完成授权，然后:")
        print("   1. 从回调URL中获取授权码(code参数)")
        print("   2. 使用授权码调用 wps.authenticate(code='xxx', redirect_uri='...')")
    
    # 2. 如果已有授权码，可以这样认证
    print("\n2. OAuth认证流程...")
    print("   (需要手动完成授权并提供授权码)")
    
    # 示例代码（需要实际的授权码）
    code = input("\n   输入授权码 (按Enter跳过): ").strip()
    if code:
        result = wps.authenticate(code=code, redirect_uri="http://localhost:8501")
        print(f"   结果: {result['message']}")
        
        if result['success']:
            print(f"   模式: 生产模式")
            print(f"   Access Token: {result['access_token'][:20]}...")
            
            # 创建真实的文档
            print("\n3. 创建真实的WPS文档...")
            result = wps.create_document(
                title="生产环境测试文档",
                content="这是通过API创建的真实文档",
                doc_type="doc"
            )
            print(f"   结果: {result['message']}")
            if result['success']:
                print(f"   文档URL: {result['document']['url']}")
    else:
        print("   已跳过OAuth认证")


def example_file_operations():
    """示例3：文件操作 / Example 3: File Operations"""
    print("\n" + "="*60)
    print("示例3：文件上传和管理")
    print("Example 3: File Upload and Management")
    print("="*60)
    
    wps = WPSIntegration()
    
    # 先认证
    result = wps.authenticate("demo@example.com", "password")
    if not result['success']:
        print("认证失败")
        return
    
    # 创建临时测试文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("这是一个测试文件的内容\nThis is test file content")
        temp_file = f.name
    
    try:
        # 上传文件
        print("\n1. 上传文件到WPS云端...")
        result = wps.upload_file(temp_file)
        print(f"   结果: {result['message']}")
        if result['success']:
            file_info = result['file']
            print(f"   文件ID: {file_info['file_id']}")
            print(f"   文件名: {file_info['name']}")
            print(f"   大小: {file_info['size']} bytes")
            print(f"   URL: {file_info['url']}")
        
        # 获取协作信息
        print("\n2. 查看文件统计...")
        stats = wps.get_collaboration_info()
        if stats['success']:
            print(f"   已上传文件数: {stats['stats']['total_files']}")
    
    finally:
        # 清理临时文件
        os.unlink(temp_file)


def example_credential_management():
    """示例4：凭证管理 / Example 4: Credential Management"""
    print("\n" + "="*60)
    print("示例4：凭证配置和管理")
    print("Example 4: Credential Configuration and Management")
    print("="*60)
    
    wps = WPSIntegration()
    
    # 1. 保存凭证
    print("\n1. 保存WPS API凭证...")
    result = wps.save_credentials(
        username="api_user",
        app_id="example_app_id_123",
        app_secret="example_secret_456"
    )
    print(f"   结果: {result['message']}")
    
    # 2. 获取授权URL
    print("\n2. 生成授权URL...")
    auth_url = wps.get_auth_url("http://localhost:8501")
    if auth_url:
        print(f"   URL已生成")
        print(f"   包含参数: client_id, redirect_uri, response_type, scope")
    
    # 3. 检查配置
    print("\n3. 检查当前配置...")
    print(f"   App ID: {wps.app_id}")
    print(f"   配置文件: {wps.config_file}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("WPS Office 集成示例")
    print("WPS Office Integration Examples")
    print("="*60)
    
    print("\n可用示例：")
    print("1. 演示模式使用")
    print("2. 生产模式使用")
    print("3. 文件操作")
    print("4. 凭证管理")
    print("0. 运行所有示例")
    
    choice = input("\n请选择示例 (1-4, 0运行全部, 按Enter退出): ").strip()
    
    if choice == '1':
        example_demo_mode()
    elif choice == '2':
        example_production_mode()
    elif choice == '3':
        example_file_operations()
    elif choice == '4':
        example_credential_management()
    elif choice == '0':
        example_demo_mode()
        example_file_operations()
        example_credential_management()
        example_production_mode()
    else:
        print("已退出")
        return
    
    print("\n" + "="*60)
    print("示例运行完成！")
    print("\n更多信息请查看: docs/WPS_INTEGRATION_GUIDE.md")
    print("="*60)


if __name__ == "__main__":
    main()
