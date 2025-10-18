import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt
import io
import base64
import os
import re
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
from docx import Document
import csv

# 订单数据管理器
class OrderManager:
    def __init__(self, use_real_data=False, data_source=None):
        self.use_real_data = use_real_data
        self.data_source = data_source
        
        # 初始化数据
        if use_real_data and data_source:
            self.orders = self._load_from_file(data_source)
        else:
            # 模拟订单数据
            self.orders = self._generate_mock_data()
    
    def _extract_text_from_image(self, image_file):
        """从图片中提取文本"""
        try:
            img = Image.open(image_file)
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            return text
        except Exception as e:
            st.error(f"图片解析错误: {str(e)}")
            return ""
    
    def _extract_text_from_pdf(self, pdf_file):
        """从PDF文件中提取文本"""
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"PDF解析错误: {str(e)}")
            return ""
    
    def _extract_text_from_docx(self, docx_file):
        """从Word文件中提取文本"""
        try:
            doc = Document(docx_file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            st.error(f"Word解析错误: {str(e)}")
            return ""
    
    def _parse_text_data(self, text):
        """解析文本数据提取订单信息"""
        orders = []
        
        # 尝试用正则表达式识别订单数据行
        lines = text.strip().split('\n')
        
        # 尝试不同的订单数据格式匹配
        order_pattern = re.compile(r'(ORD\d+).*?([^,]+).*?([^,]+).*?([^,]+).*?(\d+\.\d{2})', re.DOTALL)
        
        statuses = ['待处理', '已确认', '已发货', '已完成', '已取消', '退款中']
        payment_methods = ['支付宝', '微信支付', '银行转账', '信用卡']
        shipping_methods = ['快递', '自提', '物流', '同城配送']
        
        for line in lines:
            match = order_pattern.search(line)
            if match:
                order_id, customer_id, customer_name, order_date_str, order_amount = match.groups()
                try:
                    order_amount = float(order_amount)
                    # 尝试解析日期
                    try:
                        order_date = pd.to_datetime(order_date_str)
                    except:
                        order_date = datetime.now()
                    
                    # 生成订单详情
                    status = random.choice(statuses)
                    
                    # 根据状态设置相关日期
                    if status in ['已确认', '已发货', '已完成', '已取消', '退款中']:
                        confirm_date = order_date + timedelta(hours=random.randint(1, 24))
                    else:
                        confirm_date = None
                    
                    if status in ['已发货', '已完成']:
                        ship_date = confirm_date + timedelta(hours=random.randint(2, 48))
                    else:
                        ship_date = None
                    
                    if status == '已完成':
                        complete_date = ship_date + timedelta(days=random.randint(1, 7))
                    else:
                        complete_date = None
                    
                    # 订单详情
                    order_items = []
                    item_count = random.randint(1, 3)
                    total_quantity = 0
                    
                    for j in range(item_count):
                        product_id = f'PROD{random.randint(1, 200):04d}'
                        product_name = f'产品{random.randint(1, 200)}'
                        quantity = random.randint(1, 5)
                        unit_price = round(order_amount / (quantity * item_count), 2)
                        total_quantity += quantity
                        
                        order_item = {
                            'product_id': product_id,
                            'product_name': product_name,
                            'quantity': quantity,
                            'unit_price': unit_price,
                            'subtotal': round(quantity * unit_price, 2)
                        }
                        order_items.append(order_item)
                    
                    order = {
                        'order_id': order_id.strip(),
                        'customer_id': customer_id.strip(),
                        'customer_name': customer_name.strip(),
                        'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': status,
                        'order_amount': order_amount,
                        'payment_method': random.choice(payment_methods),
                        'shipping_method': random.choice(shipping_methods),
                        'shipping_address': f'地址{random.randint(1, 50)}',
                        'contact_phone': f'138{random.randint(10000000, 99999999)}',
                        'total_quantity': total_quantity,
                        'confirm_date': confirm_date.strftime('%Y-%m-%d %H:%M:%S') if confirm_date else None,
                        'ship_date': ship_date.strftime('%Y-%m-%d %H:%M:%S') if ship_date else None,
                        'complete_date': complete_date.strftime('%Y-%m-%d %H:%M:%S') if complete_date else None,
                        'tracking_number': f'TR{random.randint(100000000, 999999999)}' if ship_date else None,
                        'order_items': order_items,
                        'remark': random.choice(['', '加急订单', '礼品包装', '需要发票']) if random.random() > 0.7 else ''
                    }
                    orders.append(order)
                except:
                    continue
        
        return orders
    
    def _load_from_file(self, file):
        """从文件加载订单数据"""
        orders = []
        file_extension = os.path.splitext(file.name)[1].lower()
        
        statuses = ['待处理', '已确认', '已发货', '已完成', '已取消', '退款中']
        payment_methods = ['支付宝', '微信支付', '银行转账', '信用卡']
        shipping_methods = ['快递', '自提', '物流', '同城配送']
        
        try:
            if file_extension in ['.csv', '.xlsx', '.xls']:
                # 处理CSV和Excel文件
                if file_extension == '.csv':
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # 确保必要的列存在，否则使用默认值
                required_columns = ['order_id', 'customer_id', 'customer_name', 'order_date', 'order_amount']
                
                # 转换列名格式
                df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
                
                # 映射列名
                column_mapping = {}
                for req_col in required_columns:
                    for actual_col in df.columns:
                        if req_col in actual_col:
                            column_mapping[req_col] = actual_col
                            break
                
                # 转换为标准格式
                for _, row in df.iterrows():
                    try:
                        # 生成订单ID
                        order_id = str(row.get(column_mapping.get('order_id', 'order_id'), f'ORD{len(orders)+1:06d}'))
                        
                        # 解析日期
                        try:
                            order_date_str = row.get(column_mapping.get('order_date', 'order_date'), datetime.now())
                            order_date = pd.to_datetime(order_date_str)
                        except:
                            order_date = datetime.now()
                        
                        # 生成订单
                        status = str(row.get('status', random.choice(statuses)))
                        
                        # 根据状态设置相关日期
                        if status in ['已确认', '已发货', '已完成', '已取消', '退款中']:
                            confirm_date = order_date + timedelta(hours=random.randint(1, 24))
                        else:
                            confirm_date = None
                        
                        if status in ['已发货', '已完成']:
                            ship_date = confirm_date + timedelta(hours=random.randint(2, 48))
                        else:
                            ship_date = None
                        
                        if status == '已完成':
                            complete_date = ship_date + timedelta(days=random.randint(1, 7))
                        else:
                            complete_date = None
                        
                        # 订单详情
                        order_items = []
                        item_count = random.randint(1, 3)
                        total_quantity = 0
                        order_amount = float(row.get(column_mapping.get('order_amount', 'order_amount'), random.uniform(50, 10000)))
                        
                        for j in range(item_count):
                            product_id = f'PROD{random.randint(1, 200):04d}'
                            product_name = f'产品{random.randint(1, 200)}'
                            quantity = random.randint(1, 5)
                            unit_price = round(order_amount / (quantity * item_count), 2)
                            total_quantity += quantity
                            
                            order_item = {
                                'product_id': product_id,
                                'product_name': product_name,
                                'quantity': quantity,
                                'unit_price': unit_price,
                                'subtotal': round(quantity * unit_price, 2)
                            }
                            order_items.append(order_item)
                        
                        order = {
                            'order_id': order_id,
                            'customer_id': str(row.get(column_mapping.get('customer_id', 'customer_id'), f'CUST{random.randint(1, 100):04d}')),
                            'customer_name': str(row.get(column_mapping.get('customer_name', 'customer_name'), f'客户{random.randint(1, 100)}')),
                            'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'status': status,
                            'order_amount': order_amount,
                            'payment_method': str(row.get('payment_method', random.choice(payment_methods))),
                            'shipping_method': str(row.get('shipping_method', random.choice(shipping_methods))),
                            'shipping_address': str(row.get('shipping_address', f'地址{random.randint(1, 50)}')),
                            'contact_phone': str(row.get('contact_phone', f'138{random.randint(10000000, 99999999)}')),
                            'total_quantity': total_quantity,
                            'confirm_date': confirm_date.strftime('%Y-%m-%d %H:%M:%S') if confirm_date else None,
                            'ship_date': ship_date.strftime('%Y-%m-%d %H:%M:%S') if ship_date else None,
                            'complete_date': complete_date.strftime('%Y-%m-%d %H:%M:%S') if complete_date else None,
                            'tracking_number': str(row.get('tracking_number', f'TR{random.randint(100000000, 999999999)}') if ship_date else None),
                            'order_items': order_items,
                            'remark': str(row.get('remark', random.choice(['', '加急订单', '礼品包装', '需要发票'])) if random.random() > 0.7 else '')
                        }
                        orders.append(order)
                    except Exception as e:
                        continue
            elif file_extension == '.txt':
                # 处理文本文件
                text = file.getvalue().decode('utf-8')
                orders = self._parse_text_data(text)
            elif file_extension == '.pdf':
                # 处理PDF文件
                text = self._extract_text_from_pdf(file)
                orders = self._parse_text_data(text)
            elif file_extension == '.docx':
                # 处理Word文件
                text = self._extract_text_from_docx(file)
                orders = self._parse_text_data(text)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp']:
                # 处理图片文件
                text = self._extract_text_from_image(file)
                orders = self._parse_text_data(text)
            else:
                st.error(f"不支持的文件格式: {file_extension}")
        except Exception as e:
            st.error(f"文件解析错误: {str(e)}")
        
        # 如果解析失败，返回模拟数据
        if not orders:
            st.info("未从文件中解析到订单数据，使用模拟数据")
            orders = self._generate_mock_data()
        
        return orders
    
    def _generate_mock_data(self):
        # 生成模拟订单数据
        orders = []
        statuses = ['待处理', '已确认', '已发货', '已完成', '已取消', '退款中']
        payment_methods = ['支付宝', '微信支付', '银行转账', '信用卡']
        shipping_methods = ['快递', '自提', '物流', '同城配送']
        
        # 生成300个订单
        for i in range(300):
            order_id = f'ORD{i+1:06d}'
            customer_id = f'CUST{random.randint(1, 100):04d}'
            customer_name = f'客户{random.randint(1, 100)}'
            
            # 随机生成订单日期（过去3个月内）
            order_date = datetime.now() - timedelta(days=random.randint(0, 90))
            
            # 随机生成订单金额
            order_amount = round(random.uniform(50, 10000), 2)
            
            # 随机生成订单状态
            status = random.choice(statuses)
            
            # 根据状态设置相关日期
            if status in ['已确认', '已发货', '已完成', '已取消', '退款中']:
                confirm_date = order_date + timedelta(hours=random.randint(1, 24))
            else:
                confirm_date = None
            
            if status in ['已发货', '已完成']:
                ship_date = confirm_date + timedelta(hours=random.randint(2, 48))
            else:
                ship_date = None
            
            if status == '已完成':
                complete_date = ship_date + timedelta(days=random.randint(1, 7))
            else:
                complete_date = None
            
            # 订单详情
            order_items = []
            item_count = random.randint(1, 5)
            total_quantity = 0
            
            for j in range(item_count):
                product_id = f'PROD{random.randint(1, 200):04d}'
                product_name = f'产品{random.randint(1, 200)}'
                quantity = random.randint(1, 10)
                unit_price = round(random.uniform(10, 2000), 2)
                total_quantity += quantity
                
                order_item = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': round(quantity * unit_price, 2)
                }
                order_items.append(order_item)
            
            order = {
                'order_id': order_id,
                'customer_id': customer_id,
                'customer_name': customer_name,
                'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                'status': status,
                'order_amount': order_amount,
                'payment_method': random.choice(payment_methods),
                'shipping_method': random.choice(shipping_methods),
                'shipping_address': f'地址{random.randint(1, 50)}',
                'contact_phone': f'138{random.randint(10000000, 99999999)}',
                'total_quantity': total_quantity,
                'confirm_date': confirm_date.strftime('%Y-%m-%d %H:%M:%S') if confirm_date else None,
                'ship_date': ship_date.strftime('%Y-%m-%d %H:%M:%S') if ship_date else None,
                'complete_date': complete_date.strftime('%Y-%m-%d %H:%M:%S') if complete_date else None,
                'tracking_number': f'TR{random.randint(100000000, 999999999)}' if ship_date else None,
                'order_items': order_items,
                'remark': random.choice(['', '加急订单', '礼品包装', '需要发票']) if random.random() > 0.7 else ''
            }
            orders.append(order)
        
        return orders
    
    def get_order_summary(self):
        # 获取订单摘要统计信息
        df = pd.DataFrame(self.orders)
        
        # 计算订单总数
        total_orders = len(df)
        
        # 计算订单总金额
        total_amount = df['order_amount'].sum()
        
        # 计算不同状态的订单数量
        status_counts = df['status'].value_counts()
        
        # 计算今日订单数和金额
        today = datetime.now().date()
        df['order_date_date'] = pd.to_datetime(df['order_date']).dt.date
        today_orders = df[df['order_date_date'] == today]
        today_order_count = len(today_orders)
        today_order_amount = today_orders['order_amount'].sum()
        
        # 计算本月订单数和金额
        this_month = datetime.now().strftime('%Y-%m')
        df['order_month'] = pd.to_datetime(df['order_date']).dt.strftime('%Y-%m')
        month_orders = df[df['order_month'] == this_month]
        month_order_count = len(month_orders)
        month_order_amount = month_orders['order_amount'].sum()
        
        return {
            'total_orders': total_orders,
            'total_amount': round(total_amount, 2),
            'status_counts': status_counts.to_dict(),
            'today_order_count': today_order_count,
            'today_order_amount': round(today_order_amount, 2),
            'month_order_count': month_order_count,
            'month_order_amount': round(month_order_amount, 2)
        }
    
    def search_orders(self, search_term=None, status=None, start_date=None, end_date=None, 
                     min_amount=None, max_amount=None, payment_method=None):
        # 搜索和筛选订单
        df = pd.DataFrame(self.orders)
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # 应用搜索条件
        if search_term:
            mask = df.apply(lambda row: search_term.lower() in str(row['order_id']).lower() or 
                                        search_term.lower() in str(row['customer_name']).lower() or
                                        search_term.lower() in str(row['customer_id']).lower(), axis=1)
            df = df[mask]
        
        if status and status != '全部':
            df = df[df['status'] == status]
        
        if start_date:
            df = df[df['order_date'] >= pd.to_datetime(start_date)]
        
        if end_date:
            df = df[df['order_date'] <= pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)]
        
        if min_amount is not None:
            df = df[df['order_amount'] >= min_amount]
        
        if max_amount is not None:
            df = df[df['order_amount'] <= max_amount]
        
        if payment_method and payment_method != '全部':
            df = df[df['payment_method'] == payment_method]
        
        # 按订单日期降序排序
        df = df.sort_values(by='order_date', ascending=False)
        
        return df
    
    def get_pending_orders(self):
        # 获取待处理订单
        df = pd.DataFrame(self.orders)
        pending_df = df[df['status'].isin(['待处理', '已确认'])]
        pending_df['order_date'] = pd.to_datetime(pending_df['order_date'])
        pending_df = pending_df.sort_values(by='order_date', ascending=True)
        return pending_df
    
    def export_orders_to_csv(self, orders_df):
        # 导出订单数据到CSV（只导出主要字段）
        export_df = orders_df[['order_id', 'customer_id', 'customer_name', 'order_date', 'status', 
                              'order_amount', 'payment_method', 'shipping_method', 'total_quantity']]
        
        csv_buffer = io.StringIO()
        export_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_string = csv_buffer.getvalue()
        
        # 生成base64编码的下载链接
        b64 = base64.b64encode(csv_string.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="orders.csv">下载CSV文件</a>'
        
        return href

# 渲染订单管理页面
def render_order_management():
    st.title("订单管理")
    
    # 侧边栏：数据管理选项
    with st.sidebar:
        st.subheader("数据管理选项")
        
        # 仅保留数据来源选择，详细上传功能移至主界面
        data_source = st.radio(
            "数据来源",
            ["模拟数据", "上传文件"],
            index=0
        )
        use_real_data = data_source == "上传文件"
    
    # 主界面文件上传区域
    st.subheader("📁 上传订单数据")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 支持多种文件格式上传
        supported_formats = ['.xlsx', '.xls', '.csv', '.txt', '.pdf', '.docx']
        # 检查是否有OCR支持
        try:
            import easyocr
            HAS_OCR_SUPPORT = True
            supported_formats.extend(['.png', '.jpg', '.jpeg'])
        except ImportError:
            HAS_OCR_SUPPORT = False
        
        uploaded_file = st.file_uploader(
            "上传订单数据文件",
            type=[fmt[1:] for fmt in supported_formats],
            help="支持Excel、CSV、文本、PDF、Word和图片文件"
        )
    
    with col2:
        st.write(" ")  # 占位，使按钮垂直居中
        if st.button("📥 导入数据", use_container_width=True):
            if uploaded_file:
                try:
                    # 创建新订单管理器实例并加载数据
                    new_order_manager = OrderManager(use_real_data=True, data_source=uploaded_file)
                    st.session_state.order_manager = new_order_manager
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.success(f"✅ 成功导入数据: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ 导入失败: {str(e)}")
        
        if st.button("🔄 重置为模拟数据", use_container_width=True):
            st.session_state.order_manager = OrderManager(use_real_data=False)
            if 'uploaded_file_name' in st.session_state:
                del st.session_state['uploaded_file_name']
            st.success("已重置为模拟数据")
    
    # 显示支持的文件格式信息
    supported_formats_text = ", ".join([fmt.upper() for fmt in supported_formats])
    st.caption(f"支持格式: {supported_formats_text}")
    
    # 初始化或更新订单管理器
    if 'order_manager' not in st.session_state:
        st.session_state.order_manager = OrderManager(use_real_data=False)
    
    order_manager = st.session_state.order_manager
    
    # 显示当前数据来源
    if 'uploaded_file_name' in st.session_state:
        st.info(f"当前使用真实数据: {st.session_state.uploaded_file_name}")
    else:
        st.info("当前使用模拟数据")
    
    # 添加手动添加订单功能
    with st.expander("手动添加订单", expanded=False):
        with st.form("add_order_form"):
            st.subheader("添加新订单")
            col1, col2 = st.columns(2)
            
            with col1:
                order_id = st.text_input("订单ID", value=f'ORD{len(order_manager.orders)+1:06d}')
                customer_id = st.text_input("客户ID", value=f'CUST{random.randint(1, 100):04d}')
                customer_name = st.text_input("客户名称", value=f'客户{random.randint(1, 100)}')
                order_date = st.date_input("订单日期", value=datetime.now())
            
            with col2:
                order_amount = st.number_input("订单金额", min_value=0.0, step=0.01, value=random.uniform(50, 10000))
                status = st.selectbox("订单状态", ['待处理', '已确认', '已发货', '已完成', '已取消', '退款中'])
                payment_method = st.selectbox("支付方式", ['支付宝', '微信支付', '银行转账', '信用卡'])
                shipping_method = st.selectbox("配送方式", ['快递', '自提', '物流', '同城配送'])
            
            shipping_address = st.text_input("配送地址", value=f'地址{random.randint(1, 50)}')
            contact_phone = st.text_input("联系电话", value=f'138{random.randint(10000000, 99999999)}')
            remark = st.text_input("备注")
            
            submitted = st.form_submit_button("添加订单")
            
            if submitted:
                # 订单详情
                order_items = []
                item_count = random.randint(1, 3)
                total_quantity = 0
                
                for j in range(item_count):
                    product_id = f'PROD{random.randint(1, 200):04d}'
                    product_name = f'产品{random.randint(1, 200)}'
                    quantity = random.randint(1, 5)
                    unit_price = round(order_amount / (quantity * item_count), 2)
                    total_quantity += quantity
                    
                    order_item = {
                        'product_id': product_id,
                        'product_name': product_name,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'subtotal': round(quantity * unit_price, 2)
                    }
                    order_items.append(order_item)
                
                # 根据状态设置相关日期
                if status in ['已确认', '已发货', '已完成', '已取消', '退款中']:
                    confirm_date = order_date + timedelta(hours=random.randint(1, 24))
                else:
                    confirm_date = None
                
                if status in ['已发货', '已完成']:
                    ship_date = confirm_date + timedelta(hours=random.randint(2, 48)) if confirm_date else None
                else:
                    ship_date = None
                
                if status == '已完成':
                    complete_date = ship_date + timedelta(days=random.randint(1, 7)) if ship_date else None
                else:
                    complete_date = None
                
                new_order = {
                    'order_id': order_id,
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': status,
                    'order_amount': order_amount,
                    'payment_method': payment_method,
                    'shipping_method': shipping_method,
                    'shipping_address': shipping_address,
                    'contact_phone': contact_phone,
                    'total_quantity': total_quantity,
                    'confirm_date': confirm_date.strftime('%Y-%m-%d %H:%M:%S') if confirm_date else None,
                    'ship_date': ship_date.strftime('%Y-%m-%d %H:%M:%S') if ship_date else None,
                    'complete_date': complete_date.strftime('%Y-%m-%d %H:%M:%S') if complete_date else None,
                    'tracking_number': f'TR{random.randint(100000000, 999999999)}' if ship_date else None,
                    'order_items': order_items,
                    'remark': remark
                }
                order_manager.orders.append(new_order)
                st.success(f"订单 '{order_id}' 已添加成功")
    
    # 修复date_input的placeholder参数问题
    # 移除start_date和end_date的placeholder参数
    
    # 获取订单摘要
    summary = order_manager.get_order_summary()
    
    # 显示统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("订单总数", summary['total_orders'])
    
    with col2:
        st.metric("订单总金额(元)", summary['total_amount'])
    
    with col3:
        st.metric("本月订单数", summary['month_order_count'])
    
    with col4:
        st.metric("本月订单金额(元)", summary['month_order_amount'])
    
    st.divider()
    
    # 待处理订单部分
    st.subheader("待处理订单")
    pending_df = order_manager.get_pending_orders()
    
    if not pending_df.empty:
        st.warning(f"当前有 {len(pending_df)} 个订单需要处理！")
        # 格式化日期
        pending_df['order_date'] = pending_df['order_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(pending_df[['order_id', 'customer_name', 'order_date', 'status', 'order_amount']], 
                    width='stretch', hide_index=True)
    else:
        st.success("暂无待处理订单")
    
    st.divider()
    
    # 订单搜索和筛选
    st.subheader("订单查询")
    
    # 搜索和筛选表单
    search_term = st.text_input("搜索关键词 (订单号/客户名称/客户ID)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = st.selectbox("订单状态", ['全部', '待处理', '已确认', '已发货', '已完成', '已取消', '退款中'])
    
    with col2:
        payment_method = st.selectbox("支付方式", ['全部', '支付宝', '微信支付', '银行转账', '信用卡'])
    
    with col3:
        start_date = st.date_input("开始日期", value=None, format="YYYY-MM-DD")
    
    # 日期和金额范围筛选
    end_date_col, min_amount_col, max_amount_col = st.columns(3)
    
    with end_date_col:
        end_date = st.date_input("结束日期", value=None, format="YYYY-MM-DD")
    
    with min_amount_col:
        min_amount = st.number_input("最小金额", min_value=0.0, step=0.01, value=None)
    
    with max_amount_col:
        max_amount = st.number_input("最大金额", min_value=0.0, step=0.01, value=None)
    
    # 搜索按钮
    search_button = st.button("搜索")
    
    # 执行搜索
    if search_button or search_term or status != '全部' or payment_method != '全部' or start_date or end_date or \
       min_amount is not None or max_amount is not None:
        orders_df = order_manager.search_orders(
            search_term=search_term,
            status=status,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            payment_method=payment_method
        )
    else:
        # 默认显示最近50个订单
        orders_df = pd.DataFrame(order_manager.orders)
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        orders_df = orders_df.sort_values(by='order_date', ascending=False).head(50)
    
    # 显示订单表格
    if not orders_df.empty:
        st.subheader(f"订单列表 (共 {len(orders_df)} 个)")
        
        # 格式化日期
        orders_df['order_date'] = orders_df['order_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 显示表格（只显示主要字段）
        display_columns = ['order_id', 'customer_id', 'customer_name', 'order_date', 'status', 
                          'order_amount', 'payment_method', 'shipping_method', 'total_quantity']
        st.dataframe(orders_df[display_columns], width='stretch', hide_index=True)
        
        # 导出按钮
        csv_href = order_manager.export_orders_to_csv(orders_df)
        st.markdown(csv_href, unsafe_allow_html=True)
    else:
        st.info("没有找到符合条件的订单")
    
    st.divider()
    
    # 订单状态分析图表
    st.subheader("订单状态分析")
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 饼图：订单状态分布
    status_counts = pd.Series(summary['status_counts'])
    ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.set_title('订单状态分布')
    
    # 柱状图：每日订单趋势（最近7天）
    df = pd.DataFrame(order_manager.orders)
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['order_date_only'] = df['order_date'].dt.date
    
    # 最近7天的数据
    recent_days = []
    for i in range(6, -1, -1):
        recent_days.append((datetime.now() - timedelta(days=i)).date())
    
    # 按日期统计订单数
    daily_orders = df.groupby('order_date_only').size().reindex(recent_days, fill_value=0)
    
    ax2.bar(range(len(daily_orders)), daily_orders.values)
    ax2.set_title('最近7天订单趋势')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('订单数量')
    ax2.set_xticks(range(len(daily_orders)))
    ax2.set_xticklabels([d.strftime('%m-%d') for d in daily_orders.index], rotation=45)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 调整布局
    plt.tight_layout()
    
    # 显示图表
    st.pyplot(fig)