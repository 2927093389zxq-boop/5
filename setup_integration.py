import os
import json
from datetime import datetime

# 必要的目录结构
directories = [
    "core/saas",
    "core/saas/models",
    "core/saas/services",
    "core/saas/connectors",
    "core/erp",
    "core/erp/inventory",
    "core/erp/orders",
    "core/erp/suppliers",
    "core/erp/accounting",
    "core/integration",
    "ui/saas",
    "ui/erp",
    "ui/integration",
    "data/saas/stores",
    "data/saas/products",
    "data/saas/orders",
    "data/erp/inventory/products",
    "data/erp/inventory/movements",
    "data/erp/suppliers",
    "data/integration/sync_logs",
    "config"
]

# 创建目录
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    init_file = os.path.join(directory, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# 初始化模块\n")

print("目录结构已创建")

# 创建基本的模型文件
models = {
    "core/saas/models/__init__.py": "# 初始化 SaaS 模型\n",
    "core/saas/models/store.py": """
from datetime import datetime
from typing import List, Dict, Optional

class Store:
    \"\"\"店铺模型\"\"\"
    def __init__(self, 
                 store_id: str = None, 
                 name: str = "", 
                 platform: str = "",
                 api_key: str = "",
                 api_secret: str = "",
                 status: str = "active",
                 created_at: datetime = None):
        self.store_id = store_id or f"store_{int(datetime.now().timestamp())}"
        self.name = name
        self.platform = platform  # amazon, etsy, shopify 等
        self.api_key = api_key
        self.api_secret = api_secret
        self.status = status  # active, inactive, suspended
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict:
        \"\"\"将店铺对象转换为字典\"\"\"
        return {
            "store_id": self.store_id,
            "name": self.name,
            "platform": self.platform,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Store':
        \"\"\"从字典创建店铺对象\"\"\"
        created_at = datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else None
        return cls(
            store_id=data.get("store_id"),
            name=data.get("name", ""),
            platform=data.get("platform", ""),
            api_key=data.get("api_key", ""),
            api_secret=data.get("api_secret", ""),
            status=data.get("status", "active"),
            created_at=created_at
        )
""",
    "core/saas/services/__init__.py": "# 初始化 SaaS 服务\n",
    "core/saas/services/store_service.py": """
import os
import json
from typing import List, Dict, Optional
import traceback
from ..models.store import Store

class TelemetrySystem:
    def track_feature_usage(self, feature_name, data=None):
        # 简单实现，仅用于示例
        pass
    
    def track_error(self, error_type, error_message, stack_trace=None):
        # 简单实现，仅用于示例
        pass

class StoreService:
    \"\"\"店铺服务\"\"\"
    def __init__(self, data_path="data/saas/stores"):
        self.data_path = data_path
        self.telemetry = TelemetrySystem()
        os.makedirs(data_path, exist_ok=True)
    
    def save_store(self, store: Store) -> bool:
        \"\"\"保存店铺信息\"\"\"
        try:
            file_path = os.path.join(self.data_path, f"{store.store_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(store.to_dict(), f, ensure_ascii=False, indent=2)
            
            self.telemetry.track_feature_usage("saas_save_store", {"platform": store.platform})
            return True
        except Exception as e:
            self.telemetry.track_error("saas_store_save_error", str(e), traceback.format_exc())
            return False
    
    def get_store(self, store_id: str) -> Optional[Store]:
        \"\"\"获取店铺信息\"\"\"
        try:
            file_path = os.path.join(self.data_path, f"{store_id}.json")
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Store.from_dict(data)
        except Exception as e:
            self.telemetry.track_error("saas_store_get_error", str(e), traceback.format_exc())
            return None
    
    def list_stores(self) -> List[Store]:
        \"\"\"列出所有店铺\"\"\"
        try:
            stores = []
            if not os.path.exists(self.data_path):
                return []
                
            for file_name in os.listdir(self.data_path):
                if file_name.endswith(".json"):
                    file_path = os.path.join(self.data_path, file_name)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        stores.append(Store.from_dict(data))
            return stores
        except Exception as e:
            self.telemetry.track_error("saas_store_list_error", str(e), traceback.format_exc())
            return []
    
    def delete_store(self, store_id: str) -> bool:
        \"\"\"删除店铺\"\"\"
        try:
            file_path = os.path.join(self.data_path, f"{store_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            self.telemetry.track_error("saas_store_delete_error", str(e), traceback.format_exc())
            return False
    
    def update_store_status(self, store_id: str, status: str) -> bool:
        \"\"\"更新店铺状态\"\"\"
        try:
            store = self.get_store(store_id)
            if store:
                store.status = status
                return self.save_store(store)
            return False
        except Exception as e:
            self.telemetry.track_error("saas_store_status_update_error", str(e), traceback.format_exc())
            return False
""",
    "ui/saas/dashboard.py": """
import streamlit as st
import pandas as pd
from core.saas.services.store_service import StoreService
from datetime import datetime, timedelta
import random

def render_saas_dashboard():
    \"\"\"渲染 SaaS 仪表板\"\"\"
    st.title("🛍️ 电商 SaaS 仪表盘")
    
    # 初始化服务
    store_service = StoreService()
    
    # 获取所有店铺
    stores = store_service.list_stores()
    
    if not stores:
        st.info("暂无店铺信息，请先添加店铺。")
        if st.button("添加示例店铺"):
            # 添加示例店铺
            from core.saas.models.store import Store
            store = Store(
                name="示例店铺",
                platform="Shopify",
                status="active"
            )
            store_service.save_store(store)
            st.success("已添加示例店铺")
            st.rerun()
        return
    
    # 店铺选择器
    selected_store = st.selectbox(
        "选择店铺",
        options=[store.store_id for store in stores],
        format_func=lambda x: next((s.name for s in stores if s.store_id == x), x)
    )
    
    # 获取选中的店铺
    store = next((s for s in stores if s.store_id == selected_store), None)
    
    if not store:
        st.warning("未找到选中的店铺")
        return
    
    # 基础信息卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("平台", store.platform)
    with col2:
        st.metric("状态", store.status)
    with col3:
        st.metric("创建日期", store.created_at.strftime("%Y-%m-%d"))
    
    # 模拟数据
    st.subheader("📊 销售概览")
    
    # 生成过去30天的日期
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)]
    
    # 模拟销售数据
    random.seed(hash(store.store_id))
    sales = [random.randint(1000, 5000) for _ in range(30)]
    orders = [random.randint(10, 50) for _ in range(30)]
    
    # 使用折线图代替matplotlib
    sales_df = pd.DataFrame({
        "日期": dates,
        "销售额": sales,
        "订单数": orders
    })
    
    st.line_chart(
        sales_df.set_index("日期")[["销售额", "订单数"]]
    )
    
    # 绩效指标
    st.subheader("🔍 关键绩效指标")
    
    # 计算平均订单价值
    aov = sum(sales) / sum(orders)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总销售额", f"¥{sum(sales):,}", f"+{random.randint(5, 15)}%")
    with col2:
        st.metric("总订单数", f"{sum(orders)}", f"+{random.randint(3, 10)}%")
    with col3:
        st.metric("平均订单价值", f"¥{aov:.2f}", f"{random.randint(-5, 5)}%")
    with col4:
        st.metric("转化率", f"{random.uniform(1.5, 3.5):.2f}%", f"{random.uniform(-0.5, 0.5):.2f}%")
"""
}

# 创建核心文件
for file_path, content in models.items():
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("核心模块文件已创建")

# 创建UI文件
ui_files = {
    "ui/saas/store_manager.py": """
import streamlit as st
import pandas as pd
from core.saas.models.store import Store
from core.saas.services.store_service import StoreService
from datetime import datetime

def render_store_manager():
    \"\"\"渲染店铺管理界面\"\"\"
    st.title("🏪 店铺管理")
    
    # 初始化服务
    store_service = StoreService()
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["📋 店铺列表", "➕ 添加店铺", "⚙️ 店铺设置"])
    
    # 店铺列表选项卡
    with tab1:
        st.header("店铺列表")
        
        # 获取所有店铺
        stores = store_service.list_stores()
        
        if not stores:
            st.info("暂无店铺信息，请添加店铺。")
        else:
            # 将店铺转换为表格格式
            stores_data = []
            for store in stores:
                stores_data.append({
                    "店铺ID": store.store_id,
                    "店铺名称": store.name,
                    "平台": store.platform,
                    "状态": store.status,
                    "创建时间": store.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })
            
            # 显示店铺表格
            st.dataframe(pd.DataFrame(stores_data))
    
    # 添加店铺选项卡
    with tab2:
        st.header("添加新店铺")
        
        # 表单
        with st.form("add_store_form"):
            name = st.text_input("店铺名称", max_chars=100)
            platform = st.selectbox("电商平台", ["Amazon", "Shopify", "Etsy", "eBay", "Walmart", "其他"])
            
            col1, col2 = st.columns(2)
            with col1:
                api_key = st.text_input("API Key", type="password")
            with col2:
                api_secret = st.text_input("API Secret", type="password")
            
            status = st.selectbox("状态", ["active", "inactive", "pending"])
            
            submitted = st.form_submit_button("添加店铺")
            if submitted:
                if name and platform:
                    # 创建新店铺对象
                    store = Store(
                        name=name,
                        platform=platform,
                        api_key=api_key,
                        api_secret=api_secret,
                        status=status
                    )
                    
                    # 保存店铺
                    if store_service.save_store(store):
                        st.success(f"店铺 '{name}' 添加成功！")
                    else:
                        st.error("店铺添加失败！")
                else:
                    st.warning("请填写店铺名称和平台。")
    
    # 店铺设置选项卡
    with tab3:
        st.header("店铺设置")
        st.info("请在店铺列表中选择要设置的店铺")
""",
    "ui/erp/dashboard.py": """
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

def render_erp_dashboard():
    \"\"\"渲染 ERP 仪表板\"\"\"
    st.title("📊 ERP 系统仪表盘")
    
    # 基本指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("库存产品数", "125")
    with col2:
        st.metric("库存总值", "¥245,750.00")
    with col3:
        st.metric("低库存产品", "12", delta="-3")
    with col4:
        st.metric("库存周转率", "5.67", delta="0.21")
    
    # 库存状态概览
    st.subheader("📦 库存状态概览")
    
    # 创建模拟数据
    status_data = pd.DataFrame({
        "状态": ["正常库存", "低库存", "缺货"],
        "数量": [89, 27, 9]
    })
    
    # 使用streamlit的图表
    st.bar_chart(status_data.set_index("状态"))
    
    # 低库存产品表格
    st.subheader("⚠️ 需要补货的产品")
    
    # 创建模拟数据
    low_stock_data = []
    for i in range(5):
        low_stock_data.append({
            "产品ID": f"prod_{1000+i}",
            "产品名称": f"测试产品 {i+1}",
            "SKU": f"SKU-{100+i}",
            "当前库存": random.randint(1, 10),
            "再订购点": 15,
            "状态": "低库存" if i > 0 else "缺货"
        })
    
    st.dataframe(pd.DataFrame(low_stock_data))
""",
    "ui/erp/inventory_view.py": """
import streamlit as st
import pandas as pd
import random
from datetime import datetime

def render_inventory_view():
    \"\"\"渲染库存管理视图\"\"\"
    st.title("📦 库存管理")
    
    # 创建选项卡
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 库存列表", 
        "➕ 新增产品", 
        "🔄 库存调整", 
        "📊 库存报告"
    ])
    
    # 库存列表选项卡
    with tab1:
        st.header("库存列表")
        
        # 创建模拟数据
        inventory_data = []
        for i in range(10):
            inventory_data.append({
                "产品ID": f"prod_{1000+i}",
                "产品名称": f"测试产品 {i+1}",
                "SKU": f"SKU-{100+i}",
                "类别": random.choice(["电子产品", "家居用品", "办公用品", "厨房用品", "运动器材"]),
                "当前库存": random.randint(0, 100),
                "再订购点": 15,
                "成本价": f"¥{random.randint(50, 500):.2f}",
                "零售价": f"¥{random.randint(100, 1000):.2f}",
                "状态": random.choice(["正常", "低库存", "缺货"])
            })
        
        st.dataframe(pd.DataFrame(inventory_data))
    
    # 新增产品选项卡
    with tab2:
        st.header("添加新产品")
        
        with st.form("add_product_form"):
            name = st.text_input("产品名称", max_chars=100)
            
            col1, col2 = st.columns(2)
            with col1:
                sku = st.text_input("SKU")
                category = st.text_input("类别")
                cost_price = st.number_input("成本价", min_value=0.0, format="%.2f")
            
            with col2:
                barcode = st.text_input("条形码")
                stock_quantity = st.number_input("初始库存数量", min_value=0, value=0)
                retail_price = st.number_input("零售价", min_value=0.0, format="%.2f")
            
            submitted = st.form_submit_button("添加产品")
            if submitted:
                st.success("产品添加成功！")
""",
    "ui/integration/sync_dashboard.py": """
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

def render_sync_dashboard():
    \"\"\"渲染同步仪表板\"\"\"
    st.title("🔄 SaaS-ERP 同步中心")
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["📊 同步概览", "🔄 执行同步", "📜 同步日志"])
    
    # 同步概览选项卡
    with tab1:
        st.header("同步状态概览")
        
        # 显示统计数据
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总同步次数", "127")
        with col2:
            st.metric("成功", "115")
        with col3:
            st.metric("部分成功", "8")
        with col4:
            st.metric("失败", "4")
        
        # 同步类型分布
        st.subheader("同步类型分布")
        
        # 创建模拟数据
        sync_types = pd.DataFrame({
            "类型": ["产品同步到店铺", "库存更新", "订单同步到ERP"],
            "数量": [45, 67, 15]
        })
        
        st.bar_chart(sync_types.set_index("类型"))
        
        # 最近同步活动
        st.subheader("最近同步活动")
        
        # 创建模拟数据
        recent_data = []
        for i in range(5):
            days_ago = random.randint(0, 7)
            status = random.choice(["✅ success", "⚠️ partial", "❌ error"])
            sync_type = random.choice(["产品同步到店铺", "库存更新", "订单同步到ERP"])
            
            recent_data.append({
                "时间": (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M"),
                "类型": sync_type,
                "状态": status,
                "消息": f"{'成功' if '✅' in status else '部分成功' if '⚠️' in status else '失败'}同步{random.randint(1, 10)}个项目"
            })
        
        st.dataframe(pd.DataFrame(recent_data))
    
    # 执行同步选项卡
    with tab2:
        st.header("执行同步操作")
        
        sync_operation = st.selectbox(
            "选择同步操作",
            ["产品同步到店铺", "更新店铺库存", "订单同步到ERP"]
        )
        
        if sync_operation == "产品同步到店铺":
            st.write("选择要同步的产品和目标店铺")
            
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("选择产品", ["测试产品 1 (SKU: SKU-101)", "测试产品 2 (SKU: SKU-102)"])
            with col2:
                st.selectbox("选择目标店铺", ["示例店铺 (Shopify)"])
            
            if st.button("执行同步"):
                with st.spinner("正在同步产品到店铺..."):
                    # 模拟处理
                    import time
                    time.sleep(1)
                    st.success("✅ 产品已成功同步到店铺！")
        
        elif sync_operation == "更新店铺库存":
            st.selectbox("选择要更新库存的产品", 
                ["测试产品 1 (SKU: SKU-101, 库存: 45)", "测试产品 2 (SKU: SKU-102, 库存: 18)"])
            
            if st.button("更新所有店铺库存"):
                with st.spinner("正在更新店铺产品库存..."):
                    # 模拟处理
                    import time
                    time.sleep(1)
                    st.success("✅ 库存已成功同步到所有店铺！")
"""
}

# 创建UI文件
for file_path, content in ui_files.items():
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("UI文件已创建")

# 创建配置文件
config_files = {
    "config/saas_config.json": json.dumps({
        "version": "1.0.0",
        "platforms": [
            {
                "name": "Amazon",
                "api_version": "v2",
                "require_mws": True,
                "auth_fields": ["seller_id", "auth_token", "access_key", "secret_key"],
                "features": ["listings", "orders", "reports", "inventory"]
            },
            {
                "name": "Shopify",
                "api_version": "2023-07",
                "require_mws": False,
                "auth_fields": ["shop_url", "api_key", "api_password", "access_token"],
                "features": ["products", "orders", "customers", "inventory"]
            }
        ],
        "sync_settings": {
            "auto_sync_interval_minutes": 60,
            "retry_failed_sync_count": 3,
            "max_products_per_sync": 100
        }
    }, indent=2),
    
    "config/erp_config.json": json.dumps({
        "version": "1.0.0",
        "inventory_settings": {
            "default_reorder_point": 10,
            "enable_auto_purchase": True,
            "low_stock_threshold_percent": 20,
            "stock_count_schedule": "monthly"
        },
        "supplier_settings": {
            "default_payment_terms": "net_30",
            "enable_auto_reorder": True,
            "supplier_rating_enabled": True
        }
    }, indent=2),
    
    "config/integration_config.json": json.dumps({
        "version": "1.0.0",
        "auto_sync_enabled": True,
        "sync_interval_minutes": 60,
        "notification_email": "",
        "last_sync_time": datetime.now().isoformat(),
        "system_info": {
            "platform": os.name,
            "python_version": "3.8+"
        }
    }, indent=2)
}

# 创建配置文件
for file_path, content in config_files.items():
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("配置文件已创建")
print("SaaS-ERP 集成系统设置完成！")