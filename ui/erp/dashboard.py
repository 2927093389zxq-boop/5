
import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
import re
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
from docx import Document

# 仪表盘数据管理器
class DashboardManager:
    def __init__(self, use_real_data=False, data_source=None):
        self.use_real_data = use_real_data
        self.data_source = data_source
        self.dashboard_data = {}
        
        # 初始化数据
        if use_real_data and data_source:
            self.dashboard_data = self._load_from_file(data_source)
        else:
            # 模拟数据
            self.dashboard_data = self._generate_mock_data()
    
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
        """解析文本数据提取仪表板信息"""
        dashboard_data = {
            'metrics': {
                'total_products': 125,
                'total_value': 245750.00,
                'low_stock_products': 12,
                'turnover_rate': 5.67
            },
            'status_data': {
                '正常库存': 89,
                '低库存': 27,
                '缺货': 9
            },
            'low_stock_items': []
        }
        
        # 尝试解析关键指标
        total_products_pattern = re.search(r'库存产品数[：:](\d+)', text)
        total_value_pattern = re.search(r'库存总值[：:][¥￥]?([\d,]+\.?\d*)', text)
        low_stock_pattern = re.search(r'低库存产品[：:](\d+)', text)
        turnover_pattern = re.search(r'库存周转率[：:]([\d.]+)', text)
        
        if total_products_pattern:
            dashboard_data['metrics']['total_products'] = int(total_products_pattern.group(1))
        if total_value_pattern:
            value_str = total_value_pattern.group(1).replace(',', '')
            dashboard_data['metrics']['total_value'] = float(value_str)
        if low_stock_pattern:
            dashboard_data['metrics']['low_stock_products'] = int(low_stock_pattern.group(1))
        if turnover_pattern:
            dashboard_data['metrics']['turnover_rate'] = float(turnover_pattern.group(1))
        
        # 尝试解析低库存产品
        lines = text.strip().split('\n')
        product_pattern = re.compile(r'(prod_\d+).*?(测试产品 \d+).*?(SKU-\d+).*?(\d+).*?(\d+)', re.DOTALL)
        
        for line in lines:
            match = product_pattern.search(line)
            if match:
                product_id, product_name, sku, current_stock, reorder_point = match.groups()
                try:
                    item = {
                        "产品ID": product_id,
                        "产品名称": product_name,
                        "SKU": sku,
                        "当前库存": int(current_stock),
                        "再订购点": int(reorder_point),
                        "状态": "低库存" if int(current_stock) > 0 else "缺货"
                    }
                    dashboard_data['low_stock_items'].append(item)
                except:
                    continue
        
        # 如果没有解析到低库存产品，生成一些模拟数据
        if not dashboard_data['low_stock_items']:
            low_stock_count = min(dashboard_data['metrics']['low_stock_products'], 5)
            for i in range(low_stock_count):
                dashboard_data['low_stock_items'].append({
                    "产品ID": f"prod_{1000+i}",
                    "产品名称": f"产品{i+1}",
                    "SKU": f"SKU-{100+i}",
                    "当前库存": random.randint(1, 10),
                    "再订购点": 15,
                    "状态": "低库存" if i > 0 else "缺货"
                })
        
        return dashboard_data
    
    def _load_from_file(self, file):
        """从文件加载仪表盘数据"""
        dashboard_data = {
            'metrics': {
                'total_products': 125,
                'total_value': 245750.00,
                'low_stock_products': 12,
                'turnover_rate': 5.67
            },
            'status_data': {
                '正常库存': 89,
                '低库存': 27,
                '缺货': 9
            },
            'low_stock_items': []
        }
        
        file_extension = os.path.splitext(file.name)[1].lower()
        
        try:
            if file_extension in ['.csv', '.xlsx', '.xls']:
                # 处理CSV和Excel文件
                if file_extension == '.csv':
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # 尝试解析为库存数据
                if not df.empty:
                    # 转换列名格式
                    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
                    
                    # 计算基本指标
                    dashboard_data['metrics']['total_products'] = len(df)
                    
                    # 尝试计算库存总值
                    if 'unit_price' in df.columns and 'quantity' in df.columns:
                        df['total_value'] = df['unit_price'] * df['quantity']
                        dashboard_data['metrics']['total_value'] = df['total_value'].sum()
                    
                    # 确定产品状态
                    if 'quantity' in df.columns:
                        # 如果有预警阈值列，使用它
                        if 'alert_threshold' in df.columns:
                            df['status'] = df.apply(lambda row: '正常库存' if row['quantity'] >= row['alert_threshold'] else 
                                                   '低库存' if row['quantity'] > 0 else '缺货', axis=1)
                        else:
                            # 否则使用默认阈值
                            df['status'] = df['quantity'].apply(lambda x: '正常库存' if x >= 50 else '低库存' if x > 0 else '缺货')
                        
                        # 统计状态分布
                        status_counts = df['status'].value_counts()
                        for status in ['正常库存', '低库存', '缺货']:
                            dashboard_data['status_data'][status] = status_counts.get(status, 0)
                        
                        # 计算低库存产品数
                        dashboard_data['metrics']['low_stock_products'] = status_counts.get('低库存', 0) + status_counts.get('缺货', 0)
                        
                        # 获取低库存产品
                        low_stock_df = df[df['status'].isin(['低库存', '缺货'])].head(5)
                        for _, row in low_stock_df.iterrows():
                            item = {
                                "产品ID": row.get('product_id', f"prod_{random.randint(1000, 9999)}"),
                                "产品名称": row.get('product_name', f"产品{random.randint(1, 100)}"),
                                "SKU": row.get('sku', f"SKU-{random.randint(100, 999)}"),
                                "当前库存": int(row['quantity']),
                                "再订购点": int(row.get('alert_threshold', 50)),
                                "状态": row['status']
                            }
                            dashboard_data['low_stock_items'].append(item)
            elif file_extension == '.txt':
                # 处理文本文件
                text = file.getvalue().decode('utf-8')
                dashboard_data = self._parse_text_data(text)
            elif file_extension == '.pdf':
                # 处理PDF文件
                text = self._extract_text_from_pdf(file)
                dashboard_data = self._parse_text_data(text)
            elif file_extension == '.docx':
                # 处理Word文件
                text = self._extract_text_from_docx(file)
                dashboard_data = self._parse_text_data(text)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp']:
                # 处理图片文件
                text = self._extract_text_from_image(file)
                dashboard_data = self._parse_text_data(text)
            else:
                st.error(f"不支持的文件格式: {file_extension}")
        except Exception as e:
            st.error(f"文件解析错误: {str(e)}")
        
        return dashboard_data
    
    def _generate_mock_data(self):
        """生成模拟仪表盘数据"""
        total_products = random.randint(100, 200)
        low_stock_count = random.randint(5, 20)
        out_of_stock_count = random.randint(1, 10)
        normal_stock_count = total_products - low_stock_count - out_of_stock_count
        
        # 生成低库存产品
        low_stock_items = []
        for i in range(min(low_stock_count + out_of_stock_count, 5)):
            quantity = random.randint(1, 10) if i < low_stock_count else 0
            status = "低库存" if quantity > 0 else "缺货"
            low_stock_items.append({
                "产品ID": f"prod_{1000+i}",
                "产品名称": f"产品{i+1}",
                "SKU": f"SKU-{100+i}",
                "当前库存": quantity,
                "再订购点": random.randint(10, 50),
                "状态": status
            })
        
        return {
            'metrics': {
                'total_products': total_products,
                'total_value': round(random.uniform(100000, 500000), 2),
                'low_stock_products': low_stock_count,
                'turnover_rate': round(random.uniform(3.0, 8.0), 2)
            },
            'status_data': {
                '正常库存': normal_stock_count,
                '低库存': low_stock_count,
                '缺货': out_of_stock_count
            },
            'low_stock_items': low_stock_items
        }

def render_erp_dashboard():
    """渲染 ERP 仪表板"""
    st.title("📊 ERP 系统仪表盘")
    
    # 侧边栏：数据管理选项
    with st.sidebar:
        st.subheader("数据管理")
        
        # 数据来源选择
        data_source = st.radio(
            "数据来源",
            ["模拟数据", "上传文件"],
            index=0
        )
        
        use_real_data = data_source == "上传文件"
        file = None
        
        if use_real_data:
            st.info("支持的文件格式: CSV, Excel, TXT, PDF, Word, 图片")
            file = st.file_uploader(
                "上传仪表盘数据文件",
                type=["csv", "xlsx", "xls", "txt", "pdf", "docx", "jpg", "jpeg", "png", "bmp"]
            )
            
            # 刷新按钮
            if st.button("刷新数据") and file:
                st.session_state.dashboard_manager = DashboardManager(use_real_data=True, data_source=file)
                st.success("数据已从文件刷新")
        else:
            # 模拟数据选项
            if st.button("刷新模拟数据"):
                st.session_state.dashboard_manager = DashboardManager(use_real_data=False)
                st.success("模拟数据已刷新")
    
    # 初始化或更新仪表盘管理器
    if 'dashboard_manager' not in st.session_state or (use_real_data and file):
        st.session_state.dashboard_manager = DashboardManager(use_real_data=use_real_data, data_source=file)
    
    dashboard_manager = st.session_state.dashboard_manager
    dashboard_data = dashboard_manager.dashboard_data
    
    # 显示当前数据来源
    if dashboard_manager.use_real_data and dashboard_manager.data_source:
        st.info(f"当前使用真实数据: {dashboard_manager.data_source.name}")
    else:
        st.info("当前使用模拟数据")
    
    # 基本指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("库存产品数", dashboard_data['metrics']['total_products'])
    with col2:
        st.metric("库存总值", f"¥{dashboard_data['metrics']['total_value']:,.2f}")
    with col3:
        st.metric("低库存产品", dashboard_data['metrics']['low_stock_products'], delta=random.randint(-5, 5))
    with col4:
        st.metric("库存周转率", dashboard_data['metrics']['turnover_rate'], delta=random.uniform(-0.5, 0.5))
    
    # 库存状态概览
    st.subheader("📦 库存状态概览")
    
    # 创建数据框
    status_data = pd.DataFrame({
        "状态": list(dashboard_data['status_data'].keys()),
        "数量": list(dashboard_data['status_data'].values())
    })
    
    # 使用streamlit的图表
    st.bar_chart(status_data.set_index("状态"))
    
    # 低库存产品表格
    st.subheader("⚠️ 需要补货的产品")
    
    if dashboard_data['low_stock_items']:
        st.dataframe(pd.DataFrame(dashboard_data['low_stock_items']))
    else:
        st.info("暂无需要补货的产品")
    
    # 添加手动编辑指标功能
    with st.expander("手动编辑仪表盘指标", expanded=False):
        with st.form("edit_dashboard_form"):
            st.subheader("编辑仪表盘指标")
            col1, col2 = st.columns(2)
            
            with col1:
                total_products = st.number_input("库存产品数", min_value=0, value=dashboard_data['metrics']['total_products'])
                total_value = st.number_input("库存总值(元)", min_value=0.0, step=0.01, value=dashboard_data['metrics']['total_value'])
            
            with col2:
                low_stock_products = st.number_input("低库存产品数", min_value=0, value=dashboard_data['metrics']['low_stock_products'])
                turnover_rate = st.number_input("库存周转率", min_value=0.0, step=0.01, value=dashboard_data['metrics']['turnover_rate'])
            
            submitted = st.form_submit_button("更新指标")
            
            if submitted:
                dashboard_data['metrics']['total_products'] = total_products
                dashboard_data['metrics']['total_value'] = total_value
                dashboard_data['metrics']['low_stock_products'] = low_stock_products
                dashboard_data['metrics']['turnover_rate'] = turnover_rate
                
                # 更新状态数据
                out_of_stock_count = random.randint(0, low_stock_products)
                dashboard_data['status_data']['缺货'] = out_of_stock_count
                dashboard_data['status_data']['低库存'] = low_stock_products - out_of_stock_count
                dashboard_data['status_data']['正常库存'] = total_products - low_stock_products
                
                st.success("仪表盘指标已更新")
                st.rerun()
