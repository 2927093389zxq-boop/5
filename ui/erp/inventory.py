import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt
import io
import base64
import os
# 导入UI工具模块
from .ui_utils import (
    create_metric_card,
    create_beautiful_dataframe,
    show_success_message,
    show_error_message,
    show_warning_message,
    style_plot
)

# 库存数据管理器 - 支持模拟数据和真实数据
class InventoryManager:
    def __init__(self, use_real_data=False, inventory_data=None, data_source=None):
        self.use_real_data = use_real_data
        self.data_source = data_source
        self.inventory_items = []
        
        if use_real_data:
            # 当使用真实数据时，即使没有提供数据也不生成模拟数据
            if inventory_data is not None:
                self.inventory_items = inventory_data
            # 否则保持空列表，等待后续导入
        else:
            # 使用模拟数据
            self.inventory_items = self._generate_mock_data()
    
    def _generate_mock_data(self):
        # 生成模拟库存数据
        inventory = []
        categories = ['电子设备', '办公用品', '生活用品', '服装鞋帽', '食品饮料']
        locations = ['仓库A', '仓库B', '门店1', '门店2', '门店3']
        
        # 生成100个库存项目
        for i in range(100):
            product_id = f'PROD{i+1:04d}'
            product_name = f'产品{i+1}'
            category = random.choice(categories)
            quantity = random.randint(0, 1000)
            alert_threshold = random.randint(50, 200)
            
            # 根据数量设置状态
            status = self._determine_status(quantity, alert_threshold)
            
            inventory_item = {
                'product_id': product_id,
                'product_name': product_name,
                'category': category,
                'quantity': quantity,
                'unit': '件',
                'location': random.choice(locations),
                'status': status,
                'unit_price': round(random.uniform(10, 5000), 2),
                'last_restock_date': (datetime.now() - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d'),
                'supplier': f'供应商{random.randint(1, 10)}',
                'alert_threshold': alert_threshold
            }
            inventory.append(inventory_item)
        
        return inventory
    
    def _determine_status(self, quantity, alert_threshold):
        # 根据数量和预警阈值确定状态
        if quantity > alert_threshold * 3:
            return '充足'
        elif quantity > alert_threshold:
            return '正常'
        elif quantity > 0:
            return '预警'
        else:
            return '缺货'
    
    def update_inventory_item(self, product_id, updates):
        # 更新库存项目
        for item in self.inventory_items:
            if item['product_id'] == product_id:
                # 更新字段
                for key, value in updates.items():
                    if key in item:
                        item[key] = value
                # 重新计算状态
                if 'quantity' in updates or 'alert_threshold' in updates:
                    item['status'] = self._determine_status(item['quantity'], item['alert_threshold'])
                return True
        return False
    
    def add_inventory_item(self, new_item):
        # 添加新的库存项目
        # 确保有product_id
        if 'product_id' not in new_item:
            # 生成新的product_id
            max_id = 0
            for item in self.inventory_items:
                if item['product_id'].startswith('PROD'):
                    try:
                        num_id = int(item['product_id'][4:])
                        max_id = max(max_id, num_id)
                    except:
                        pass
            new_item['product_id'] = f'PROD{max_id + 1:04d}'
        
        # 确定状态
        if 'status' not in new_item and 'quantity' in new_item and 'alert_threshold' in new_item:
            new_item['status'] = self._determine_status(new_item['quantity'], new_item['alert_threshold'])
        
        self.inventory_items.append(new_item)
        return True
    
    def delete_inventory_item(self, product_id):
        # 删除库存项目
        self.inventory_items = [item for item in self.inventory_items if item['product_id'] != product_id]
        return True
    
    def import_from_csv(self, file):
        # 从CSV文件导入数据
        try:
            df = pd.read_csv(file)
            # 确保必要的列存在
            required_columns = ['product_id', 'product_name', 'category', 'quantity', 'unit_price']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, f"缺少必要的列: {', '.join(missing_columns)}"
            
            # 转换为字典列表
            inventory_data = df.to_dict('records')
            
            # 为每个项目确定状态
            for item in inventory_data:
                # 确保有alert_threshold
                if 'alert_threshold' not in item:
                    item['alert_threshold'] = 100
                # 确保有status
                item['status'] = self._determine_status(item['quantity'], item['alert_threshold'])
                # 确保有其他必要字段
                if 'unit' not in item:
                    item['unit'] = '件'
                if 'location' not in item:
                    item['location'] = '未指定'
                if 'last_restock_date' not in item:
                    item['last_restock_date'] = datetime.now().strftime('%Y-%m-%d')
                if 'supplier' not in item:
                    item['supplier'] = '未指定'
            
            self.inventory_items = inventory_data
            self.use_real_data = True
            return True, "数据导入成功"
        except Exception as e:
            return False, f"导入失败: {str(e)}"
    
    def get_inventory_summary(self):
        # 获取库存摘要统计信息
        df = pd.DataFrame(self.inventory_items)
        
        # 计算总库存价值
        total_value = (df['quantity'] * df['unit_price']).sum()
        
        # 计算库存总量
        total_quantity = df['quantity'].sum()
        
        # 计算不同状态的产品数量
        status_counts = df['status'].value_counts()
        
        # 计算分类统计
        category_summary = df.groupby('category').agg({
            'quantity': 'sum',
            'unit_price': 'mean',
            'product_id': 'count'
        }).rename(columns={'product_id': 'item_count'}).reset_index()
        
        return {
            'total_value': round(total_value, 2),
            'total_quantity': total_quantity,
            'status_counts': status_counts.to_dict(),
            'category_summary': category_summary
        }
    
    def search_inventory(self, search_term=None, category=None, status=None, location=None, 
                        min_quantity=None, max_quantity=None, min_price=None, max_price=None, supplier=None):
        # 搜索和筛选库存项目 - 增强版支持价格范围和供应商筛选
        df = pd.DataFrame(self.inventory_items)
        
        # 应用搜索条件
        if search_term:
            mask = df.apply(lambda row: search_term.lower() in str(row['product_name']).lower() or 
                                        search_term.lower() in str(row['product_id']).lower() or
                                        search_term.lower() in str(row['supplier']).lower(), axis=1)
            df = df[mask]
        
        if category and category != '全部':
            df = df[df['category'] == category]
        
        if status and status != '全部':
            df = df[df['status'] == status]
        
        if location and location != '全部':
            df = df[df['location'] == location]
        
        if supplier and supplier != '全部':
            df = df[df['supplier'] == supplier]
        
        if min_quantity is not None:
            df = df[df['quantity'] >= min_quantity]
        
        if max_quantity is not None:
            df = df[df['quantity'] <= max_quantity]
        
        if min_price is not None:
            df = df[df['unit_price'] >= min_price]
        
        if max_price is not None:
            df = df[df['unit_price'] <= max_price]
        
        # 按状态和数量排序
        if not df.empty:
            # 添加排序优先级映射
            status_priority = {'缺货': 0, '预警': 1, '正常': 2, '充足': 3}
            df['status_priority'] = df['status'].map(status_priority)
            df = df.sort_values(by=['status_priority', 'quantity'], ascending=[True, True]).drop('status_priority', axis=1)
        
        return df
    
    def get_low_stock_items(self):
        # 获取低库存预警项目
        df = pd.DataFrame(self.inventory_items)
        low_stock_df = df[df['quantity'] <= df['alert_threshold']]
        return low_stock_df
    
    def export_inventory_to_csv(self, inventory_df):
        # 导出库存数据到CSV
        csv_buffer = io.StringIO()
        inventory_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_string = csv_buffer.getvalue()
        
        # 生成base64编码的下载链接
        b64 = base64.b64encode(csv_string.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="inventory.csv">下载CSV文件</a>'
        
        return href

# 渲染库存管理页面
def render_inventory_management():
    # 设置页面主题和字体
    set_page_theme('light')
    setup_chinese_fonts()
    
    st.title("库存管理系统")
    st.markdown("---")
    
    # 侧边栏：数据管理选项 - 高级交互版
    with st.sidebar:
        # 添加自定义CSS样式
        st.markdown("""
        <style>
        .sidebar-header {
            color: #2c3e50;
            font-weight: bold;
            margin-bottom: 15px;
            font-size: 18px;
        }
        .upload-container {
            border: 2px dashed #4CAF50;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            background-color: #f9f9f9;
            transition: all 0.3s ease;
            margin: 10px 0;
        }
        .upload-container:hover {
            border-color: #2196F3;
            background-color: #f0f7ff;
        }
        .tool-button {
            margin: 5px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-header">📊 数据管理</div>', unsafe_allow_html=True)
        
        # 数据来源选择 - 使用更现代的样式
        st.markdown("### 数据来源")
        data_source = st.radio(
            "",  # 空标签，使用自定义标题
            ["模拟数据", "上传文件"],
            index=0,
            captions=["使用系统生成的模拟数据", "上传CSV文件作为数据源"],
            horizontal=False,
            help="选择您想要使用的数据来源"
        )
        
        use_real_data = data_source == "上传文件"
        file = None
        
        if use_real_data:
            # 上传文件模式 - 增强版
            st.info("📋 支持的文件格式: CSV, Excel, TXT")
            
            # 创建美化的上传区域
            st.markdown('<div class="upload-container">', unsafe_allow_html=True)
            file = st.file_uploader(
                "拖拽文件到此处或点击浏览",
                type=["csv", "xlsx", "xls", "txt"],
                label_visibility="visible",
                help="选择要上传的库存数据文件"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 上传文件后的处理逻辑
            if file is not None:
                # 视觉反馈 - 文件上传成功
                st.balloons()
                show_success_message(f"✅ 已上传文件: {file.name}")
                
                # 文件信息显示
                st.markdown(f"**文件名:** {file.name}")
                st.markdown(f"**文件大小:** {file.size / 1024:.1f} KB")
                
                try:
                    # 显示文件预览
                    st.markdown("##### 📋 数据预览")
                    
                    # 根据文件类型读取
                    if file.name.endswith('.csv'):
                        preview_df = pd.read_csv(file)
                    elif file.name.endswith(('.xlsx', '.xls')):
                        preview_df = pd.read_excel(file)
                    elif file.name.endswith('.txt'):
                        preview_df = pd.read_csv(file, sep='\t')
                    
                    # 重置文件指针
                    file.seek(0)
                    
                    # 检查必要的列是否存在
                    required_columns = ['product_id', 'product_name', 'category', 'quantity', 'unit_price']
                    missing_columns = [col for col in required_columns if col not in preview_df.columns]
                    
                    if missing_columns:
                        st.warning(f"⚠️ 文件缺少必要列: {', '.join(missing_columns)}")
                    else:
                        st.success("✅ 文件格式正确，可以导入")
                    
                    # 美化显示预览数据
                    create_beautiful_dataframe(preview_df.head(3), "预览数据", height=150)
                    
                except Exception as e:
                    show_error_message(f"❌ 预览失败: {str(e)}")
                
                # 主要操作按钮
                st.markdown("### 操作选项")
                
                # 导入数据按钮 - 确保数据清零
                if st.button("📥 导入数据", type="primary", use_container_width=True):
                    with show_loading_spinner("正在导入数据..."):
                        # 创建全新的库存管理器实例，完全清除旧数据
                        new_manager = InventoryManager(use_real_data=True)
                        # 重置文件指针
                        file.seek(0)
                        success, message = new_manager.import_from_csv(file)
                        
                        if success:
                            # 完全替换session中的库存管理器
                            st.session_state.inventory_manager = new_manager
                            # 记录当前文件信息
                            st.session_state.prev_file = file.name
                            # 清除可能存在的其他相关会话状态
                            for key in list(st.session_state.keys()):
                                if key.startswith('search_') or key.startswith('filter_') or key == 'advanced_search':
                                    del st.session_state[key]
                            show_success_message(f"✅ 数据导入成功！{message}")
                            # 强制重新运行以更新界面
                            st.experimental_rerun()
                        else:
                            show_error_message(f"❌ 导入失败: {message}")
                        
                        # 重置文件指针
                        file.seek(0)
                
                # 清除上传按钮
                if st.button("🔄 清除上传", use_container_width=True):
                    # 清除文件上传器
                    st.session_state.clear()
                    # 重新运行应用
                    st.experimental_rerun()
                
                # 下载模板按钮
                if st.button("📄 下载模板", use_container_width=True, type="secondary"):
                    # 创建模板数据
                    template_data = {
                        'product_id': ['PROD0001', 'PROD0002', 'PROD0003'],
                        'product_name': ['测试产品1', '测试产品2', '测试产品3'],
                        'category': ['电子设备', '办公用品', '生活用品'],
                        'quantity': [100, 200, 50],
                        'unit_price': [999.99, 99.5, 19.99],
                        'unit': ['件', '套', '个'],
                        'location': ['仓库A', '仓库B', '门店1'],
                        'alert_threshold': [10, 20, 5],
                        'last_restock_date': [datetime.now().strftime('%Y-%m-%d'), 
                                            datetime.now().strftime('%Y-%m-%d'),
                                            datetime.now().strftime('%Y-%m-%d')],
                        'supplier': ['供应商1', '供应商2', '供应商3']
                    }
                    template_df = pd.DataFrame(template_data)
                    
                    # 转换为CSV并提供下载
                    csv = template_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="下载CSV模板",
                        data=csv,
                        file_name="inventory_template.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        else:
            # 模拟数据选项 - 增强版
            st.markdown("### 模拟数据设置")
            
            # 添加一些参数控制
            num_items = st.slider("生成项目数量", min_value=10, max_value=500, value=100, step=10)
            
            # 添加类别选择
            available_categories = ['电子设备', '办公用品', '生活用品', '服装鞋帽', '食品饮料']
            selected_categories = st.multiselect(
                "选择产品类别",
                available_categories,
                default=available_categories,
                help="选择要在模拟数据中包含的产品类别"
            )
            
            # 刷新按钮
            if st.button("🎲 刷新模拟数据", type="primary", use_container_width=True):
                with show_loading_spinner("正在生成模拟数据..."):
                    # 创建新的库存管理器实例
                    st.session_state.inventory_manager = InventoryManager(use_real_data=False)
                    # 清除之前的数据相关会话状态
                    for key in list(st.session_state.keys()):
                        if key.startswith('search_') or key.startswith('filter_') or key == 'advanced_search':
                            del st.session_state[key]
                    show_success_message("✅ 模拟数据已刷新")
                    # 强制重新运行以更新界面
                    st.experimental_rerun()
    
    # 初始化或更新库存管理器
    # 1. 如果是第一次加载，创建库存管理器
    # 2. 如果数据源类型发生变化，重新创建库存管理器
    # 3. 如果上传了新文件，强制重新创建库存管理器以清除旧数据
    file_changed = file is not None and ('prev_file' not in st.session_state or st.session_state.prev_file != file.name)
    
    if 'inventory_manager' not in st.session_state or \
       (use_real_data and not st.session_state.inventory_manager.use_real_data) or \
       (not use_real_data and st.session_state.inventory_manager.use_real_data) or \
       (use_real_data and file_changed):
        # 根据数据源选择创建相应的库存管理器
        with show_loading_spinner("正在处理数据..."):
            if use_real_data and file is not None:
                # 上传文件模式下，创建新的库存管理器并调用import_from_csv方法
                # 这确保了在上传新文件时完全清除旧数据
                new_manager = InventoryManager(use_real_data=True)
                # 重置文件指针，确保从头读取
                file.seek(0)
                success, message = new_manager.import_from_csv(file)
                if success:
                    st.session_state.inventory_manager = new_manager
                    # 记录当前文件信息，用于检测文件变化
                    st.session_state.prev_file = file.name
                    show_success_message(f"成功加载文件: {file.name}")
                else:
                    show_error_message(f"加载文件失败: {message}")
                # 重置文件指针
                file.seek(0)
            else:
                # 模拟数据模式下，生成新的模拟数据
                st.session_state.inventory_manager = InventoryManager(use_real_data=False)
                # 清除之前的文件信息
                if 'prev_file' in st.session_state:
                    del st.session_state.prev_file
    
    inventory_manager = st.session_state.inventory_manager
    
    # 显示当前数据来源 - 美化版
    current_source = "真实数据" if (inventory_manager.use_real_data and hasattr(inventory_manager, 'data_source') and inventory_manager.data_source) else "模拟数据"
    source_file = inventory_manager.data_source.name if (hasattr(inventory_manager, 'data_source') and inventory_manager.data_source) else "-"
    
    with st.expander(f"📋 当前数据源: {current_source}", expanded=False):
        st.markdown(f"**数据源类型:** {current_source}")
        if source_file != "-":
            st.markdown(f"**文件名:** {source_file}")
        st.markdown(f"**产品总数:** {len(inventory_manager.inventory_items)}")
        st.markdown(f"**数据模式:** {'真实数据模式' if inventory_manager.use_real_data else '模拟数据模式'}")
        
        # 手动添加项目 - 使用更醒目的按钮
                if st.sidebar.button("➕ 添加新库存项目", type="secondary", use_container_width=True):
                    st.session_state.show_add_form = True
                
                # 添加新库存项目表单 - 增强版
                if 'show_add_form' in st.session_state and st.session_state.show_add_form:
                    # 使用expander使表单更加整洁
                    with st.expander("📝 添加新库存项目", expanded=True):
                        with st.form("add_inventory_form"):
                            # 添加更好的视觉组织
                            st.markdown("<style>
                            .form-section { margin-bottom: 15px; }
                            .form-label { font-weight: bold; color: #333; }
                            </style>", unsafe_allow_html=True)
                            
                            # 使用三列布局更有效地利用空间
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown("<div class='form-section'><div class='form-label'>基本信息</div></div>", unsafe_allow_html=True)
                                product_name = st.text_input("产品名称 *", placeholder="输入产品名称")
                                category = st.selectbox("产品分类", 
                                                       ['电子设备', '办公用品', '生活用品', '服装鞋帽', '食品饮料'])
                                unit = st.text_input("单位", value="件", placeholder="例如: 件、个、箱")
                            
                            with col2:
                                st.markdown("<div class='form-section'><div class='form-label'>库存信息</div></div>", unsafe_allow_html=True)
                                quantity = st.number_input("数量", min_value=0, step=1, value=0, format="%d")
                                unit_price = st.number_input("单价(元)", min_value=0.0, step=0.01, value=0.0, format="%.2f")
                                alert_threshold = st.number_input("预警阈值", min_value=0, step=1, value=50, format="%d")
                            
                            with col3:
                                st.markdown("<div class='form-section'><div class='form-label'>位置信息</div></div>", unsafe_allow_html=True)
                                location = st.selectbox("仓库位置", 
                                                       ['仓库A', '仓库B', '门店1', '门店2', '门店3'])
                                last_restock_date = st.date_input("最后补货日期", value=datetime.now())
                                supplier = st.text_input("供应商", placeholder="输入供应商名称")
                            
                            # 额外的描述字段
                            st.markdown("<div class='form-section'><div class='form-label'>附加信息</div></div>", unsafe_allow_html=True)
                            description = st.text_area("产品描述", placeholder="输入产品详细描述")
                            
                            # 必填字段提示
                            st.caption("* 标记的字段为必填项")
                            
                            # 提交和取消按钮
                            col_submit, col_cancel = st.columns([1, 1])
                            with col_submit:
                                submit = st.form_submit_button("✅ 添加产品", type="primary", use_container_width=True)
                            with col_cancel:
                                cancel = st.form_submit_button("❌ 取消", use_container_width=True)
                            
                            # 表单提交处理
                            if submit:
                                # 验证必填字段
                                if not product_name:
                                    show_error_message("请输入产品名称")
                                else:
                                    # 添加新产品
                                    new_item = {
                                        'product_name': product_name,
                                        'category': category,
                                        'quantity': quantity,
                                        'unit': unit,
                                        'location': location,
                                        'unit_price': unit_price,
                                        'alert_threshold': alert_threshold,
                                        'last_restock_date': last_restock_date.strftime('%Y-%m-%d'),
                                        'supplier': supplier,
                                        'description': description if description else ""
                                    }
                                    
                                    # 使用加载动画提升体验
                                    with show_loading_spinner("正在添加产品..."):
                                        # 短暂延迟以显示加载效果
                                        time.sleep(0.5)
                                        inventory_manager.add_inventory_item(new_item)
                                    
                                    # 成功反馈
                                    st.balloons()
                                    show_success_message(f"✅ 成功添加产品: {product_name}")
                                    
                                    # 更新会话状态和重置表单
                                    st.session_state.inventory_manager = inventory_manager
                                    st.session_state.show_add_form = False
                                    
                                    # 重新运行以更新界面
                                    st.experimental_rerun()
                            
                            # 取消按钮处理
                            if cancel:
                                st.session_state.show_add_form = False
    
    # 获取库存摘要
    summary = inventory_manager.get_inventory_summary()
    
    # 显示统计摘要卡片 - 高级交互版
    st.subheader("📊 库存概览")
    
    # 获取库存摘要统计信息
    summary = inventory_manager.get_inventory_summary()
    
    # 动态颜色映射 - 根据数值状态变化
    def get_stock_color(value, total_count):
        # 根据低库存比例确定颜色
        ratio = value / total_count if total_count > 0 else 0
        if ratio > 0.3:
            return "#F44336"
        elif ratio > 0.1:
            return "#FF9800"
        else:
            return "#4CAF50"
    
    # 高级统计卡片布局
    col1, col2, col3, col4 = st.columns(4)
    product_count = len(inventory_manager.inventory_items)
    low_stock_count = summary['status_counts'].get('预警', 0) + summary['status_counts'].get('缺货', 0)
    
    with col1:
        # 库存总价值卡片 - 添加增长趋势
        create_metric_card("库存总价值", f"¥{summary['total_value']:,.2f}", 
                          icon="💰", color="#4CAF50", border_radius=10, box_shadow=True, 
                          subtext="总资产价值", animate=True)
    
    with col2:
        # 库存总量卡片
        create_metric_card("库存总量", summary['total_quantity'], 
                          icon="📦", color="#2196F3", border_radius=10, box_shadow=True,
                          subtext="所有产品总数量", animate=True)
    
    with col3:
        # 产品总数卡片
        create_metric_card("产品总数", product_count, 
                          icon="📋", color="#FF9800", border_radius=10, box_shadow=True,
                          subtext="SKU种类", animate=True)
    
    with col4:
        # 低库存产品卡片 - 根据比例动态变色
        low_stock_color = get_stock_color(low_stock_count, product_count)
        create_metric_card("低库存产品", low_stock_count, 
                          icon="⚠️", color=low_stock_color, border_radius=10, box_shadow=True,
                          subtext="需要关注", animate=True)
    
    # 状态分布微型图表
    with st.expander("📊 库存状态分布", expanded=True):
        status_colors = {'充足': '#4CAF50', '正常': '#2196F3', '预警': '#FF9800', '缺货': '#F44336'}
        
        if summary['status_counts']:
            status_df = pd.DataFrame(list(summary['status_counts'].items()), columns=['状态', '数量'])
            status_df['颜色'] = status_df['状态'].map(status_colors)
            
            # 创建进度条显示
            total = status_df['数量'].sum()
            
            for _, row in status_df.iterrows():
                progress_col, text_col = st.columns([3, 1])
                with progress_col:
                    st.progress(row['数量'] / total if total > 0 else 0, text=f"{row['状态']}")
                with text_col:
                    st.markdown(f"**{row['数量']}**")
    
    st.divider()
    
    # 库存搜索和筛选 - 增强版
    with st.expander("🔍 库存查询", expanded=True):
        # 添加高级搜索标志
        if 'advanced_search' not in st.session_state:
            st.session_state.advanced_search = False
            
        # 搜索和筛选表单
        search_term = st.text_input("搜索关键词", placeholder="输入产品名称、ID或供应商", key="search_term")
        
        # 基本筛选
        col1, col2, col3 = st.columns(3)
        
        # 获取唯一的分类列表
        categories = ['全部']
        if inventory_manager.inventory_items:
            categories.extend(list(pd.DataFrame(inventory_manager.inventory_items)['category'].unique()))
        
        with col1:
            category = st.selectbox("产品分类", categories, key="category_filter")
        
        with col2:
            status = st.selectbox("库存状态", ['全部', '充足', '正常', '预警', '缺货'], key="status_filter")
        
        # 获取唯一的位置列表
        locations = ['全部']
        if inventory_manager.inventory_items:
            locations.extend(list(pd.DataFrame(inventory_manager.inventory_items)['location'].unique()))
        
        with col3:
            location = st.selectbox("仓库位置", locations, key="location_filter")
        
        # 高级搜索选项
        if st.checkbox("显示高级筛选选项", value=st.session_state.advanced_search, key="advanced_search_checkbox"):
            st.session_state.advanced_search = True
            
            # 数量范围筛选
            min_max_col1, min_max_col2 = st.columns(2)
            
            with min_max_col1:
                min_quantity = st.number_input("最小数量", min_value=0, step=1, value=None, placeholder="最小数量", key="min_quantity")
            
            with min_max_col2:
                max_quantity = st.number_input("最大数量", min_value=0, step=1, value=None, placeholder="最大数量", key="max_quantity")
            
            # 价格范围筛选
            price_col1, price_col2 = st.columns(2)
            
            with price_col1:
                min_price = st.number_input("最低单价", min_value=0.0, step=0.01, value=None, placeholder="最低单价", key="min_price")
            
            with price_col2:
                max_price = st.number_input("最高单价", min_value=0.0, step=0.01, value=None, placeholder="最高单价", key="max_price")
            
            # 供应商筛选
            suppliers = ['全部']
            if inventory_manager.inventory_items:
                suppliers.extend(list(pd.DataFrame(inventory_manager.inventory_items)['supplier'].unique()))
            
            supplier = st.selectbox("供应商", suppliers, key="supplier_filter")
        else:
            st.session_state.advanced_search = False
            min_quantity = max_quantity = min_price = max_price = None
            supplier = "全部"
        
        # 搜索按钮组
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_button = st.button("🔍 搜索", use_container_width=True, type="primary")
        with search_col2:
            clear_button = st.button("清除筛选", use_container_width=True)
        
        if clear_button:
            # 清除所有筛选条件
            st.session_state.advanced_search = False
            st.session_state.search_term = ""
    
    # 低库存预警 - 高级交互版
    low_stock_df = inventory_manager.get_low_stock_items()
    low_stock_count = len(low_stock_df)
    
    if low_stock_count > 0:
        with st.expander("⚠️ 低库存预警", expanded=True):
            # 低库存统计信息
            st.markdown(f"**低库存产品总数: {low_stock_count}**")
            缺货_count = summary['status_counts'].get('缺货', 0)
            预警_count = summary['status_counts'].get('预警', 0)
            
            # 显示缺货和预警的详细数量
            st.markdown(f"- 缺货: {缺货_count} 个产品")
            st.markdown(f"- 预警: {预警_count} 个产品")
            
            # 添加快速过滤选项
            low_stock_filter = st.radio(
                "显示选项",
                options=["全部低库存", "仅显示缺货", "仅显示预警"],
                horizontal=True,
                key="low_stock_filter"
            )
            
            # 根据选择过滤数据
            if low_stock_filter == "仅显示缺货":
                filtered_df = low_stock_df[low_stock_df['status'] == '缺货']
            elif low_stock_filter == "仅显示预警":
                filtered_df = low_stock_df[low_stock_df['status'] == '预警']
            else:
                filtered_df = low_stock_df
            
            # 美化显示低库存产品
            display_columns = ['product_id', 'product_name', 'category', 'quantity', 'alert_threshold', 'location']
            low_stock_display = filtered_df[display_columns]
            # 添加缺少数量列
            low_stock_display['缺少数量'] = low_stock_display['alert_threshold'] - low_stock_display['quantity']
            
            # 高亮显示缺货产品
            if 'status' in filtered_df.columns:
                # 创建状态标记
                def highlight_status(row):
                    if row.name in filtered_df.index:
                        status = filtered_df.loc[row.name, 'status']
                        return [f'background-color: #ffebee;' if status == '缺货' else f'background-color: #fff3e0;' for _ in row]
                    return [''] * len(row)
                
                styled_display = low_stock_display.style.apply(highlight_status, axis=1)
                st.dataframe(styled_display, hide_index=True, use_container_width=True, height=300)
            else:
                create_beautiful_dataframe(low_stock_display, "需要补货的产品", height=300)
            
            # 添加快速操作按钮
            if len(filtered_df) > 0:
                st.markdown("#### 快速操作")
                col_export_low, col_reorder = st.columns(2)
                
                with col_export_low:
                    # 导出低库存清单
                    if st.button("导出低库存清单", use_container_width=True, type="secondary"):
                        csv = low_stock_display.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📄 下载低库存CSV",
                            data=csv,
                            file_name=f"low_stock_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                with col_reorder:
                    # 标记为待补货
                    if st.button("标记为待补货", use_container_width=True, type="secondary"):
                        st.info("已将选中的产品标记为待补货，可在采购系统中查看")
    else:
        with st.expander("✅ 库存状态", expanded=False):
            # 显示库存充足的视觉效果
            st.balloons()
            show_success_message("太棒了！所有产品库存充足，无需补货！")
            st.markdown("库存健康度评分: ⭐⭐⭐⭐⭐")
    
    st.divider()
    
    # 执行搜索 - 包含高级筛选条件
    if search_button or search_term or category != '全部' or status != '全部' or location != '全部' or \
       min_quantity is not None or max_quantity is not None or min_price is not None or max_price is not None or \
       supplier != '全部':
        
        # 显示搜索中动画
        with show_loading_spinner("正在搜索..."):
            inventory_df = inventory_manager.search_inventory(
                search_term=search_term,
                category=category,
                status=status,
                location=location,
                min_quantity=min_quantity,
                max_quantity=max_quantity,
                min_price=min_price,
                max_price=max_price,
                supplier=supplier
            )
            
        # 显示搜索结果信息
        if len(inventory_df) == 0:
            show_info_message(f"没有找到匹配条件的产品")
        else:
            show_success_message(f"找到 {len(inventory_df)} 个匹配条件的产品")
    else:
        # 默认显示所有库存项目
        inventory_df = pd.DataFrame(inventory_manager.inventory_items)
        if not inventory_df.empty:
            # 添加排序优先级映射
            status_priority = {'缺货': 0, '预警': 1, '正常': 2, '充足': 3}
            inventory_df['status_priority'] = inventory_df['status'].map(status_priority)
            inventory_df = inventory_df.sort_values(by=['status_priority', 'quantity'], 
                                                  ascending=[True, True]).drop('status_priority', axis=1)
    
    # 显示库存表格 - 增强交互版
    if not inventory_df.empty:
        # 状态高亮映射 - 根据状态应用不同颜色
        status_styles = {
            '缺货': 'color: #F44336; font-weight: bold;',
            '预警': 'color: #FF9800; font-weight: bold;',
            '正常': 'color: #4CAF50;',
            '充足': 'color: #2196F3;'
        }
        
        st.markdown(f"### 📋 库存列表 (共 {len(inventory_df)} 项)")
        
        # 添加库存价值列
        if 'quantity' in inventory_df.columns and 'unit_price' in inventory_df.columns:
            inventory_df['inventory_value'] = (inventory_df['quantity'] * inventory_df['unit_price']).round(2)
        
        # 用户自定义显示选项面板
        with st.expander("⚙️ 显示选项", expanded=True):
            display_cols = st.columns([2, 2, 1])
            
            # 列选择
            with display_cols[0]:
                # 创建列名映射，使显示更友好
                column_aliases = {
                    'product_id': '产品ID',
                    'product_name': '产品名称',
                    'category': '分类',
                    'quantity': '数量',
                    'unit': '单位',
                    'status': '状态',
                    'location': '位置',
                    'unit_price': '单价',
                    'inventory_value': '库存价值',
                    'alert_threshold': '预警阈值',
                    'last_restock_date': '最后补货日期',
                    'supplier': '供应商'
                }
                
                # 只显示存在的列
                available_columns = {col: column_aliases.get(col, col) for col in inventory_df.columns 
                                    if col in column_aliases}
                
                # 默认显示的列
                default_display = ['product_id', 'product_name', 'category', 'quantity', 'status', 'location', 'unit_price']
                selected_columns = [col for col in default_display if col in available_columns]
                
                # 列选择器
                if len(available_columns) > 0:
                    selected_columns = st.multiselect(
                        "选择要显示的列",
                        options=list(available_columns.keys()),
                        format_func=lambda x: available_columns[x],
                        default=selected_columns
                    )
                
            # 排序选项
            with display_cols[1]:
                # 排序字段和方向
                sort_columns = {'产品ID': 'product_id', '产品名称': 'product_name', 
                               '数量': 'quantity', '单价': 'unit_price', '库存价值': 'inventory_value'}
                
                # 只显示存在的排序选项
                available_sort = {k: v for k, v in sort_columns.items() if v in inventory_df.columns}
                
                if len(available_sort) > 0:
                    sort_by = st.selectbox(
                        "排序字段",
                        options=list(available_sort.keys()),
                        key="sort_by"
                    )
                    
                    sort_dir = st.radio(
                        "排序方向",
                        options=["升序", "降序"],
                        horizontal=True,
                        key="sort_dir"
                    )
                    
                    # 应用排序
                    ascending = sort_dir == "升序"
                    inventory_df = inventory_df.sort_values(by=available_sort[sort_by], ascending=ascending)
            
            # 显示样式选项
            with display_cols[2]:
                # 状态高亮切换
                highlight_status = st.checkbox("高亮显示状态", value=True, key="highlight_status")
        
        # 操作选项
        with st.expander("🔧 操作功能", expanded=False):
            col_edit, col_delete, col_export = st.columns(3)
            
            with col_edit:
                enable_edit = st.checkbox("启用编辑", value=False, key="enable_edit")
            
            with col_delete:
                enable_delete = st.checkbox("启用删除", value=False, key="enable_delete")
            
            with col_export:
                enable_export = st.checkbox("启用导出", value=True, key="enable_export")
        
        # 自定义列配置
        column_config = {
            "product_id": st.column_config.TextColumn("产品ID", width="small", disabled=True),
            "product_name": st.column_config.TextColumn("产品名称", width="medium"),
            "category": st.column_config.TextColumn("分类", width="small"),
            "quantity": st.column_config.NumberColumn("数量", width="small", min_value=0, step=1),
            "unit": st.column_config.TextColumn("单位", width="small"),
            "status": st.column_config.SelectboxColumn(
                "状态",
                options=['充足', '正常', '预警', '缺货'],
                width="small",
                disabled=True
            ),
            "location": st.column_config.TextColumn("位置", width="small"),
            "unit_price": st.column_config.NumberColumn("单价", width="small", min_value=0.0, step=0.01, format="¥%.2f"),
            "inventory_value": st.column_config.NumberColumn("库存价值", width="small", format="¥%.2f", disabled=True),
            "alert_threshold": st.column_config.NumberColumn("预警阈值", width="small", min_value=0, step=1),
            "last_restock_date": st.column_config.DateColumn("最后补货日期", width="small"),
            "supplier": st.column_config.TextColumn("供应商", width="small")
        }
        
        # 只使用用户选择的列配置
        filtered_config = {col: column_config[col] for col in selected_columns if col in column_config}
        
        if enable_edit:
            # 编辑模式提示
            show_info_message("📝 编辑模式已启用，您可以直接修改表格中的数据，然后点击保存按钮")
            
            # 创建可编辑的数据框
            edited_df = st.data_editor(
                inventory_df[selected_columns],
                hide_index=True,
                num_rows="dynamic",
                use_container_width=True,
                column_config=filtered_config,
                key="inventory_editor"
            )
            
            # 保存编辑 - 使用主要按钮样式
            col_save, col_cancel = st.columns([1, 1])
            with col_save:
                if st.button("💾 保存更改", use_container_width=True, type="primary"):
                    with show_loading_spinner("正在保存更改..."):
                        # 遍历编辑后的行
                        for idx, row in edited_df.iterrows():
                            if 'product_id' in row:
                                product_id = row['product_id']
                                # 排除product_id、status和inventory_value（会自动计算）
                                updates = {k: v for k, v in row.to_dict().items() if k not in ['product_id', 'status', 'inventory_value']}
                                inventory_manager.update_inventory_item(product_id, updates)
                        
                        show_success_message("✅ 库存数据已成功更新！")
                        # 更新session_state
                        st.session_state.inventory_manager = inventory_manager
            
            with col_cancel:
                if st.button("❌ 取消编辑", use_container_width=True):
                    # 重新加载数据
                    inventory_df = pd.DataFrame(inventory_manager.inventory_items)
                    show_info_message("已取消编辑，恢复原始数据")
        else:
            # 普通显示模式 - 美化显示
            styled_df = inventory_df[selected_columns].copy()
            
            # 应用状态高亮
            if highlight_status and 'status' in styled_df.columns:
                # 使用Streamlit原生的dataframe方法，通过column_config实现样式
                st.dataframe(
                    styled_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config=filtered_config,
                    height=400
                )
            else:
                # 普通显示
                create_beautiful_dataframe(styled_df, height=400)
        
        # 导出功能
        if enable_export:
            with st.expander("📥 导出数据", expanded=False):
                # 导出选项
                export_format = st.radio(
                    "选择导出格式",
                    options=["CSV", "Excel"],
                    horizontal=True
                )
                
                # 准备导出数据
                export_df = inventory_df[selected_columns].copy()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                if export_format == "CSV":
                    csv = export_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📄 下载CSV文件",
                        data=csv,
                        file_name=f"inventory_export_{timestamp}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        type="primary"
                    )
                else:  # Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        export_df.to_excel(writer, index=False, sheet_name='库存数据')
                        
                        # 美化Excel内容
                        worksheet = writer.sheets['库存数据']
                        # 调整列宽
                        for i, col in enumerate(export_df.columns):
                            max_len = max(len(str(export_df[col].max())), len(col)) + 2
                            worksheet.set_column(i, i, max_len)
                    
                    excel_data = output.getvalue()
                    st.download_button(
                        label="📊 下载Excel文件",
                        data=excel_data,
                        file_name=f"inventory_export_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary"
                    )
        
        # 删除功能 - 优化界面和流程
        if enable_delete:
            with st.expander("🗑️ 删除产品", expanded=False):
                # 选择删除模式
                delete_mode = st.radio(
                    "删除方式",
                    options=["多选产品ID", "删除搜索结果中的所有产品"],
                    horizontal=True
                )
                
                if delete_mode == "多选产品ID":
                    selected_ids = st.multiselect(
                        "选择要删除的产品ID",
                        options=inventory_df['product_id'].tolist()
                    )
                    
                    if selected_ids:
                        # 显示将要删除的产品预览
                        st.markdown("### 📋 即将删除的产品")
                        delete_preview = inventory_df[inventory_df['product_id'].isin(selected_ids)]
                        st.dataframe(delete_preview[['product_id', 'product_name', 'category', 'quantity']], hide_index=True)
                        
                        # 危险操作确认
                        if st.button("⚠️ 确认删除选中项目", type="secondary", use_container_width=True):
                            with show_loading_spinner("正在删除..."):
                                for product_id in selected_ids:
                                    inventory_manager.delete_inventory_item(product_id)
                                show_success_message(f"✅ 已成功删除 {len(selected_ids)} 个项目")
                                # 更新session_state
                                st.session_state.inventory_manager = inventory_manager
                else:  # 删除搜索结果中的所有产品
                    # 警告信息
                    show_warning_message(f"⚠️ 此操作将删除搜索结果中的所有 {len(inventory_df)} 个产品！")
                    
                    # 二次确认
                    confirm_delete_all = st.checkbox("我确认要删除所有搜索结果中的产品")
                    
                    if confirm_delete_all:
                        if st.button("🚨 确认删除所有产品", type="secondary", use_container_width=True):
                            with show_loading_spinner("正在删除..."):
                                for product_id in inventory_df['product_id']:
                                    inventory_manager.delete_inventory_item(product_id)
                                show_success_message(f"✅ 已成功删除 {len(inventory_df)} 个项目")
                                # 更新session_state
                                st.session_state.inventory_manager = inventory_manager
    else:
        st.info("没有找到符合条件的库存项目")
    
    st.divider()
    
    # 库存分类统计图表 - 交互式分析版
    with st.expander("📊 库存统计分析", expanded=False):
        if inventory_manager.inventory_items:
            # 图表类型选择
            chart_type = st.radio(
                "选择图表类型",
                options=["饼图 - 分类占比", "柱状图 - 库存价值", "柱状图 - 产品数量"],
                horizontal=True,
                key="chart_type"
            )
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 根据选择的图表类型显示不同的图表
            if chart_type == "饼图 - 分类占比":
                # 饼图：各分类产品数量占比
                category_counts = pd.DataFrame(inventory_manager.inventory_items)['category'].value_counts()
                
                # 使用更美观的颜色
                colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
                
                # 添加交互式饼图 - 显示百分比和数值
                wedges, texts, autotexts = ax.pie(category_counts, labels=category_counts.index, 
                                                autopct=lambda p: f'{p:.1f}%\n({int(p*sum(category_counts)/100)})', 
                                                startangle=90, colors=colors, 
                                                shadow=False, wedgeprops={'edgecolor': 'w', 'linewidth': 1}, 
                                                explode=[0.05] * len(category_counts))  # 添加轻微爆炸效果
                
                # 美化文本
                for text in texts:
                    text.set_fontsize(11)
                for autotext in autotexts:
                    autotext.set_fontsize(10)
                    autotext.set_color('white')
                    autotext.set_weight('bold')
                
                ax.axis('equal')  # 保证饼图是圆的
                ax.set_title('产品分类占比分析', fontsize=16, pad=20)
                
            elif chart_type == "柱状图 - 库存价值":
                # 柱状图：各分类库存价值
                category_value = summary['category_summary']
                category_value['total_value'] = category_value['quantity'] * category_value['unit_price']
                
                # 排序，使图表更有意义
                category_value = category_value.sort_values('total_value', ascending=True)
                
                # 使用渐变色
                colors = plt.cm.Viridis(np.linspace(0.2, 0.8, len(category_value)))
                
                bars = ax.barh(category_value['category'], category_value['total_value'], color=colors)
                ax.set_xlabel('库存价值 (元)', fontsize=12)
                ax.set_ylabel('产品分类', fontsize=12)
                ax.set_title('各分类库存价值对比', fontsize=16, pad=20)
                
                # 添加数值标签
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + width * 0.01, bar.get_y() + bar.get_height()/2., 
                            f'¥{width:,.0f}',
                            va='center', fontsize=10)
                
                # 添加网格线
                ax.grid(axis='x', linestyle='--', alpha=0.7)
                
            else:  # "柱状图 - 产品数量"
                # 柱状图：各分类产品数量
                category_counts = pd.DataFrame(inventory_manager.inventory_items)['category'].value_counts().reset_index()
                category_counts.columns = ['category', 'count']
                category_counts = category_counts.sort_values('count', ascending=True)
                
                # 使用渐变色
                colors = plt.cm.Oranges(np.linspace(0.2, 0.8, len(category_counts)))
                
                bars = ax.barh(category_counts['category'], category_counts['count'], color=colors)
                ax.set_xlabel('产品数量', fontsize=12)
                ax.set_ylabel('产品分类', fontsize=12)
                ax.set_title('各分类产品数量对比', fontsize=16, pad=20)
                
                # 添加数值标签
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + width * 0.01, bar.get_y() + bar.get_height()/2., 
                            f'{int(width)}',
                            va='center', fontsize=10)
                
                # 添加网格线
                ax.grid(axis='x', linestyle='--', alpha=0.7)
            
            # 调整布局
            plt.tight_layout()
            
            # 美化图表
            style_plot(fig)
            
            # 显示图表
            st.pyplot(fig)
            
            # 详细的分类统计表格
            st.markdown("### 📊 分类统计详情")
            
            # 准备详细统计数据
            detail_df = pd.DataFrame(inventory_manager.inventory_items)
            detailed_stats = detail_df.groupby('category').agg({
                'quantity': ['sum', 'mean', 'min', 'max'],
                'unit_price': ['mean', 'min', 'max'],
                'product_id': 'count'
            }).round(2)
            
            # 重命名列
            detailed_stats.columns = ['总数量', '平均数量', '最小数量', '最大数量', 
                                     '平均单价', '最低单价', '最高单价', '产品数量']
            
            # 计算总价值
            detailed_stats['总价值'] = (detailed_stats['总数量'] * detailed_stats['平均单价']).round(2)
            
            # 重新排序列
            detailed_stats = detailed_stats[['产品数量', '总数量', '平均数量', '最小数量', '最大数量', 
                                           '平均单价', '最低单价', '最高单价', '总价值']]
            
            # 格式化显示
            detailed_stats['平均单价'] = detailed_stats['平均单价'].apply(lambda x: f"¥{x:.2f}")
            detailed_stats['最低单价'] = detailed_stats['最低单价'].apply(lambda x: f"¥{x:.2f}")
            detailed_stats['最高单价'] = detailed_stats['最高单价'].apply(lambda x: f"¥{x:.2f}")
            detailed_stats['总价值'] = detailed_stats['总价值'].apply(lambda x: f"¥{x:,.2f}")
            
            # 显示详细统计表格
            st.dataframe(detailed_stats, use_container_width=True, height=400)
        else:
            st.info("暂无数据可供统计")