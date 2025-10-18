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

# 产品数据管理器
class ProductManager:
    def __init__(self, use_real_data=False, data_source=None):
        self.use_real_data = use_real_data
        self.data_source = data_source
        
        # 初始化数据
        if use_real_data and data_source:
            self.products = self._load_from_file(data_source)
        else:
            # 模拟产品数据
            self.products = self._generate_mock_data()
    
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
        """解析文本数据提取产品信息"""
        products = []
        
        # 尝试用正则表达式识别产品数据行
        lines = text.strip().split('\n')
        
        # 尝试不同的产品数据格式匹配
        product_pattern = re.compile(r'(PROD\d+).*?([^,]+).*?([^,]+).*?([^,]+).*?(\d+\.\d{2}).*?(\d+\.\d{2})', re.DOTALL)
        
        for line in lines:
            match = product_pattern.search(line)
            if match:
                product_id, product_name, category, brand, price, cost = match.groups()
                try:
                    price = float(price)
                    cost = float(cost)
                    product = {
                        'product_id': product_id.strip(),
                        'product_name': product_name.strip(),
                        'category': category.strip(),
                        'brand': brand.strip(),
                        'description': f'{brand.strip()} {product_name.strip()} - {category.strip()}',
                        'price': price,
                        'cost': cost,
                        'profit_margin': round(((price - cost) / price) * 100, 2),
                        'status': random.choice(['在售', '缺货', '下架', '即将上线']),
                        'created_date': datetime.now().strftime('%Y-%m-%d'),
                        'last_updated': datetime.now().strftime('%Y-%m-%d'),
                        'supplier': f'供应商{random.randint(1, 15)}',
                        'weight': round(random.uniform(0.1, 50), 2),
                        'dimensions': f'{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)}',
                        'barcode': f'{random.randint(1000000000, 9999999999)}',
                        'is_featured': random.choice([True, False]),
                        'warranty_days': random.choice([0, 30, 90, 180, 365])
                    }
                    products.append(product)
                except:
                    continue
        
        return products
    
    def _load_from_file(self, file):
        """从文件加载产品数据"""
        products = []
        file_extension = os.path.splitext(file.name)[1].lower()
        
        try:
            pass  # 占位语句，等待后续代码补充
            if file_extension in ['.csv', '.xlsx', '.xls']:
                # 处理CSV和Excel文件
                if file_extension == '.csv':
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # 确保必要的列存在，否则使用默认值
                required_columns = ['product_id', 'product_name', 'category', 'brand', 'price', 'cost']
                
                # 如果没有足够的列，尝试解析
                if len(df.columns) >= 6:
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
                            product = {
                                'product_id': str(row.get(column_mapping.get('product_id', 'product_id'), f'PROD{len(products)+1:04d}')),
                                'product_name': str(row.get(column_mapping.get('product_name', 'product_name'), f'产品{len(products)+1}')),
                                'category': str(row.get(column_mapping.get('category', 'category'), '未分类')),
                                'brand': str(row.get(column_mapping.get('brand', 'brand'), '未知品牌')),
                                'description': str(row.get('description', f'{str(row.get(column_mapping.get("brand", "brand"), "未知品牌"))} {str(row.get(column_mapping.get("product_name", "product_name"), f"产品{len(products)+1}"))}')),
                                'price': float(row.get(column_mapping.get('price', 'price'), 0)),
                                'cost': float(row.get(column_mapping.get('cost', 'cost'), 0)),
                                'profit_margin': round(((float(row.get(column_mapping.get('price', 'price'), 0)) - float(row.get(column_mapping.get('cost', 'cost'), 0))) / max(1, float(row.get(column_mapping.get('price', 'price'), 1))) * 100), 2),
                                'status': str(row.get('status', random.choice(['在售', '缺货', '下架', '即将上线']))),
                                'created_date': str(row.get('created_date', datetime.now().strftime('%Y-%m-%d'))),
                                'last_updated': str(row.get('last_updated', datetime.now().strftime('%Y-%m-%d'))),
                                'supplier': str(row.get('supplier', f'供应商{random.randint(1, 15)}')),
                                'weight': float(row.get('weight', round(random.uniform(0.1, 50), 2))),
                                'dimensions': str(row.get('dimensions', f'{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)}')),
                                'barcode': str(row.get('barcode', f'{random.randint(1000000000, 9999999999)}')),
                                'is_featured': bool(row.get('is_featured', random.choice([True, False]))),
                                'warranty_days': int(row.get('warranty_days', random.choice([0, 30, 90, 180, 365])))
                            }
                            products.append(product)
                        except:
                            continue
            elif file_extension == '.txt':
                # 处理文本文件
                text = file.getvalue().decode('utf-8')
                products = self._parse_text_data(text)
            elif file_extension == '.pdf':
                # 处理PDF文件
                text = self._extract_text_from_pdf(file)
                products = self._parse_text_data(text)
            elif file_extension == '.docx':
                # 处理Word文件
                text = self._extract_text_from_docx(file)
                products = self._parse_text_data(text)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp']:
                # 处理图片文件
                text = self._extract_text_from_image(file)
                products = self._parse_text_data(text)
            else:
                st.error(f"不支持的文件格式: {file_extension}")
        except Exception as e:
            st.error(f"文件解析错误: {str(e)}")
        
        # 如果解析失败，返回模拟数据
        if not products:
            st.info("未从文件中解析到产品数据，使用模拟数据")
            products = self._generate_mock_data()
        
        return products
    
    def _generate_mock_data(self):
        # 生成模拟产品数据
        products = []
        categories = ['电子设备', '办公用品', '生活用品', '服装鞋帽', '食品饮料']
        brands = ['品牌A', '品牌B', '品牌C', '品牌D', '品牌E']
        statuses = ['在售', '缺货', '下架', '即将上线']
        
        # 生成200个产品
        for i in range(200):
            product_id = f'PROD{i+1:04d}'
            product_name = f'产品{i+1}'
            category = random.choice(categories)
            brand = random.choice(brands)
            price = round(random.uniform(10, 5000), 2)
            cost = round(price * random.uniform(0.4, 0.8), 2)
            
            # 随机生成库存状态
            status = random.choice(statuses)
            
            product = {
                'product_id': product_id,
                'product_name': product_name,
                'category': category,
                'brand': brand,
                'description': f'{brand} {product_name} - {category}',
                'price': price,
                'cost': cost,
                'profit_margin': round(((price - cost) / price) * 100, 2),
                'status': status,
                'created_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
                'last_updated': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
                'supplier': f'供应商{random.randint(1, 15)}',
                'weight': round(random.uniform(0.1, 50), 2),
                'dimensions': f'{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)}',
                'barcode': f'{random.randint(1000000000, 9999999999)}',
                'is_featured': random.choice([True, False]),
                'warranty_days': random.choice([0, 30, 90, 180, 365])
            }
            products.append(product)
        
        return products
    
    def get_product_summary(self):
        # 获取产品摘要统计信息
        df = pd.DataFrame(self.products)
        
        # 计算产品总数
        total_products = len(df)
        
        # 计算不同状态的产品数量
        status_counts = df['status'].value_counts()
        
        # 计算分类统计
        category_summary = df.groupby('category').agg({
            'product_id': 'count',
            'price': 'mean',
            'profit_margin': 'mean'
        }).rename(columns={'product_id': 'product_count'}).reset_index()
        
        # 计算品牌统计
        brand_summary = df.groupby('brand').agg({
            'product_id': 'count',
            'price': 'mean'
        }).rename(columns={'product_id': 'product_count'}).reset_index()
        
        # 计算平均利润率
        avg_profit_margin = df['profit_margin'].mean()
        
        return {
            'total_products': total_products,
            'status_counts': status_counts.to_dict(),
            'category_summary': category_summary,
            'brand_summary': brand_summary,
            'avg_profit_margin': round(avg_profit_margin, 2)
        }
    
    def search_products(self, search_term=None, category=None, brand=None, status=None, 
                       min_price=None, max_price=None, min_profit=None):
        # 搜索和筛选产品
        df = pd.DataFrame(self.products)
        
        # 应用搜索条件
        if search_term:
            mask = df.apply(lambda row: search_term.lower() in str(row['product_name']).lower() or 
                                        search_term.lower() in str(row['product_id']).lower() or
                                        search_term.lower() in str(row['description']).lower(), axis=1)
            df = df[mask]
        
        if category and category != '全部':
            df = df[df['category'] == category]
        
        if brand and brand != '全部':
            df = df[df['brand'] == brand]
        
        if status and status != '全部':
            df = df[df['status'] == status]
        
        if min_price is not None:
            df = df[df['price'] >= min_price]
        
        if max_price is not None:
            df = df[df['price'] <= max_price]
        
        if min_profit is not None:
            df = df[df['profit_margin'] >= min_profit]
        
        # 按产品ID排序
        df = df.sort_values(by='product_id', ascending=True)
        
        return df
    
    def get_featured_products(self):
        # 获取精选产品
        df = pd.DataFrame(self.products)
        featured_df = df[df['is_featured'] == True]
        return featured_df
    
    def export_products_to_csv(self, products_df):
        # 导出产品数据到CSV
        csv_buffer = io.StringIO()
        products_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_string = csv_buffer.getvalue()
        
        # 生成base64编码的下载链接
        b64 = base64.b64encode(csv_string.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="products.csv">下载CSV文件</a>'
        
        return href

# 渲染产品管理页面
def render_product_management():
    st.title("产品管理")
    
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
    st.subheader("📁 上传产品数据")
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
            "上传产品数据文件",
            type=[fmt[1:] for fmt in supported_formats],
            help="支持Excel、CSV、文本、PDF、Word和图片文件"
        )
    
    with col2:
        st.write(" ")  # 占位，使按钮垂直居中
        if st.button("📥 导入数据", use_container_width=True):
            if uploaded_file:
                try:
                    # 创建新产品管理器实例并加载数据
                    new_product_manager = ProductManager(use_real_data=True, data_source=uploaded_file)
                    st.session_state.product_manager = new_product_manager
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.success(f"✅ 成功导入数据: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ 导入失败: {str(e)}")
        
        if st.button("🔄 重置为模拟数据", use_container_width=True):
            st.session_state.product_manager = ProductManager(use_real_data=False)
            if 'uploaded_file_name' in st.session_state:
                del st.session_state['uploaded_file_name']
            st.success("已重置为模拟数据")
    
    # 显示支持的文件格式信息
    supported_formats_text = ", ".join([fmt.upper() for fmt in supported_formats])
    st.caption(f"支持格式: {supported_formats_text}")
    
    # 初始化或更新产品管理器
    if 'product_manager' not in st.session_state:
        st.session_state.product_manager = ProductManager(use_real_data=False)
    
    product_manager = st.session_state.product_manager
    
    # 显示当前数据来源
    if 'uploaded_file_name' in st.session_state:
        st.info(f"当前使用真实数据: {st.session_state.uploaded_file_name}")
    else:
        st.info("当前使用模拟数据")
    
    # 添加手动添加产品功能
    with st.expander("手动添加产品", expanded=False):
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_id = st.text_input("产品ID", value=f'PROD{len(product_manager.products)+1:04d}')
                product_name = st.text_input("产品名称", value=f'产品{len(product_manager.products)+1}')
                category = st.selectbox("分类", ['电子设备', '办公用品', '生活用品', '服装鞋帽', '食品饮料'])
                brand = st.text_input("品牌", value=f'品牌{random.randint(1, 5)}')
            
            with col2:
                price = st.number_input("价格", min_value=0.0, step=0.01, value=100.0)
                cost = st.number_input("成本", min_value=0.0, step=0.01, value=60.0)
                status = st.selectbox("状态", ['在售', '缺货', '下架', '即将上线'])
                is_featured = st.checkbox("精选产品")
            
            description = st.text_area("描述", value=f'{brand} {product_name} - {category}')
            
            submitted = st.form_submit_button("添加产品")
            
            if submitted:
                new_product = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'category': category,
                    'brand': brand,
                    'description': description,
                    'price': price,
                    'cost': cost,
                    'profit_margin': round(((price - cost) / price) * 100, 2),
                    'status': status,
                    'created_date': datetime.now().strftime('%Y-%m-%d'),
                    'last_updated': datetime.now().strftime('%Y-%m-%d'),
                    'supplier': f'供应商{random.randint(1, 15)}',
                    'weight': round(random.uniform(0.1, 50), 2),
                    'dimensions': f'{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)}',
                    'barcode': f'{random.randint(1000000000, 9999999999)}',
                    'is_featured': is_featured,
                    'warranty_days': random.choice([0, 30, 90, 180, 365])
                }
                product_manager.products.append(new_product)
                st.success(f"产品 '{product_name}' 已添加成功")
    
    # 获取产品摘要
    summary = product_manager.get_product_summary()
    
    # 显示统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("产品总数", summary['total_products'])
    
    with col2:
        st.metric("在售产品数", summary['status_counts'].get('在售', 0))
    
    with col3:
        st.metric("平均利润率(%)", summary['avg_profit_margin'])
    
    with col4:
        st.metric("缺货产品数", summary['status_counts'].get('缺货', 0))
    
    st.divider()
    
    # 产品搜索和筛选
    st.subheader("产品查询")
    
    # 搜索和筛选表单
    search_term = st.text_input("搜索关键词")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category = st.selectbox("产品分类", ['全部'] + list(pd.DataFrame(product_manager.products)['category'].unique()))
    
    with col2:
        brand = st.selectbox("品牌", ['全部'] + list(pd.DataFrame(product_manager.products)['brand'].unique()))
    
    with col3:
        status = st.selectbox("状态", ['全部', '在售', '缺货', '下架', '即将上线'])
    
    # 价格和利润率范围筛选
    price_col1, price_col2, profit_col = st.columns(3)
    
    with price_col1:
        min_price = st.number_input("最低价格", min_value=0.0, step=0.01, value=None, placeholder="最低价格")
    
    with price_col2:
        max_price = st.number_input("最高价格", min_value=0.0, step=0.01, value=None, placeholder="最高价格")
    
    with profit_col:
        min_profit = st.number_input("最低利润率(%)", min_value=0.0, step=0.01, value=None, placeholder="最低利润率")
    
    # 搜索按钮
    search_button = st.button("搜索")
    
    # 精选产品部分
    st.subheader("精选产品")
    featured_df = product_manager.get_featured_products()
    
    if not featured_df.empty:
        st.dataframe(featured_df[['product_id', 'product_name', 'category', 'brand', 'price', 'status']], 
                    width='stretch', hide_index=True)
    else:
        st.info("暂无精选产品")
    
    st.divider()
    
    # 执行搜索
    if search_button or search_term or category != '全部' or brand != '全部' or status != '全部' or \
       min_price is not None or max_price is not None or min_profit is not None:
        products_df = product_manager.search_products(
            search_term=search_term,
            category=category,
            brand=brand,
            status=status,
            min_price=min_price,
            max_price=max_price,
            min_profit=min_profit
        )
    else:
        # 默认显示所有产品
        products_df = pd.DataFrame(product_manager.products)
        products_df = products_df.sort_values(by='product_id', ascending=True)
    
    # 显示产品表格
    if not products_df.empty:
        st.subheader(f"产品列表 (共 {len(products_df)} 项)")
        
        # 显示表格
        st.dataframe(products_df, width='stretch', hide_index=True)
        
        # 导出按钮
        csv_href = product_manager.export_products_to_csv(products_df)
        st.markdown(csv_href, unsafe_allow_html=True)
    else:
        st.info("没有找到符合条件的产品")
    
    st.divider()
    
    # 产品分析图表
    st.subheader("产品分析")
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 饼图：产品状态分布
    status_counts = pd.Series(summary['status_counts'])
    ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.set_title('产品状态分布')
    
    # 柱状图：各分类产品数量
    category_counts = summary['category_summary']
    ax2.bar(category_counts['category'], category_counts['product_count'])
    ax2.set_title('各分类产品数量')
    ax2.set_xlabel('产品分类')
    ax2.set_ylabel('产品数量')
    ax2.tick_params(axis='x', rotation=45)
    
    # 调整布局
    plt.tight_layout()
    
    # 显示图表
    st.pyplot(fig)