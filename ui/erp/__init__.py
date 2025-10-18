# ERP UI 组件初始化

# 导入所有ERP模块
from .dashboard import render_erp_dashboard
from .inventory import render_inventory_management
from .orders import render_order_management
from .products import render_product_management
from .billing import render_billing_management

__all__ = [
    'render_erp_dashboard',
    'render_inventory_management',
    'render_order_management',
    'render_product_management',
    'render_billing_management'
]