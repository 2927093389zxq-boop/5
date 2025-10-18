import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt
import io
import base64

# 尝试导入OCR支持
HAS_OCR_SUPPORT = False
try:
    import pytesseract
    from PIL import Image
    HAS_OCR_SUPPORT = True
except ImportError:
    pass

# 导入文件导入器类
class FileImporter:
    """文件导入器类，用于处理不同格式的文件上传和数据解析"""
    def __init__(self):
        self.billing_manager = None
    
    def import_file(self, uploaded_file):
        """导入并解析上传的文件"""
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        try:
            # 处理Excel文件
            if file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
                return self._process_dataframe(df)
            
            # 处理CSV文件
            elif file_extension == 'csv':
                # 尝试不同编码
                encodings = ['utf-8', 'gbk', 'latin1']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(uploaded_file, encoding=encoding)
                        return self._process_dataframe(df)
                    except UnicodeDecodeError:
                        continue
                raise ValueError("无法解析CSV文件编码")
            
            # 处理文本文件
            elif file_extension == 'txt':
                # 尝试不同编码读取TXT文件
                encodings = ['utf-8', 'gbk', 'latin1']
                content = None
                for encoding in encodings:
                    try:
                        uploaded_file.seek(0)
                        content = uploaded_file.read().decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    raise ValueError("无法解析TXT文件编码")
                
                # 简单的TXT解析逻辑，假设制表符分隔
                lines = content.strip().split('\n')
                headers = [h.strip() for h in lines[0].split('\t')]
                data = []
                for line in lines[1:]:
                    if line.strip():
                        values = [v.strip() for v in line.split('\t')]
                        if len(values) == len(headers):
                            data.append(dict(zip(headers, values)))
                
                df = pd.DataFrame(data)
                return self._process_dataframe(df)
            
            # 处理PDF文件
            elif file_extension == 'pdf':
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                    # 简单解析PDF文本内容
                    # 这里需要根据实际PDF格式定制解析逻辑
                    st.info(f"已从PDF提取文本内容，长度: {len(text)} 字符")
                    st.code(text[:1000] + "..." if len(text) > 1000 else text)
                    
                    # 返回示例数据结构
                    return {"transactions": [], "message": "PDF解析功能需要根据实际格式定制"}
                except ImportError:
                    raise ImportError("需要安装PyPDF2库来处理PDF文件")
            
            # 处理Word文档
            elif file_extension == 'docx':
                try:
                    from docx import Document
                    doc = Document(uploaded_file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                    
                    # 简单解析Word文本内容
                    # 这里需要根据实际Word格式定制解析逻辑
                    st.info(f"已从Word文档提取文本内容，长度: {len(text)} 字符")
                    st.code(text[:1000] + "..." if len(text) > 1000 else text)
                    
                    # 返回示例数据结构
                    return {"transactions": [], "message": "Word文档解析功能需要根据实际格式定制"}
                except ImportError:
                    raise ImportError("需要安装python-docx库来处理Word文档")
            
            # 处理图片文件（OCR）
            elif file_extension in ['png', 'jpg', 'jpeg'] and HAS_OCR_SUPPORT:
                try:
                    image = Image.open(uploaded_file)
                    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                    
                    # 简单解析OCR结果
                    st.info(f"已从图片提取文本内容，长度: {len(text)} 字符")
                    st.code(text[:1000] + "..." if len(text) > 1000 else text)
                    
                    # 返回示例数据结构
                    return {"transactions": [], "message": "OCR结果解析功能需要根据实际需求定制"}
                except Exception as e:
                    raise Exception(f"OCR处理失败: {str(e)}")
            
            else:
                raise ValueError(f"不支持的文件格式: {file_extension}")
        
        except Exception as e:
            raise Exception(f"文件导入失败: {str(e)}")
    
    def _process_dataframe(self, df):
        """处理DataFrame数据，转换为交易记录格式"""
        # 检查是否包含必要的列
        required_columns = ['transaction_id', 'customer_id', 'amount', 'transaction_date']
        available_columns = set(df.columns)
        
        # 如果缺少关键列，尝试映射相似列名
        column_mapping = {
            'transaction_id': ['transaction_id', '交易ID', '交易编号', '订单ID'],
            'customer_id': ['customer_id', '客户ID', '客户编号', '用户ID'],
            'amount': ['amount', '金额', '交易金额', '订单金额'],
            'transaction_date': ['transaction_date', '交易日期', '日期', '交易时间'],
            'status': ['status', '状态', '交易状态'],
            'payment_method': ['payment_method', '支付方式', '付款方式'],
            'product_type': ['product_type', '产品类型', '产品', '服务类型']
        }
        
        # 映射列名
        actual_columns = {}
        for key, possible_names in column_mapping.items():
            for name in possible_names:
                if name in available_columns:
                    actual_columns[key] = name
                    break
        
        # 确保有必要的列
        if not all(key in actual_columns for key in required_columns):
            missing = [key for key in required_columns if key not in actual_columns]
            raise ValueError(f"CSV文件缺少必要的列: {missing}")
        
        # 转换数据
        transactions = []
        for _, row in df.iterrows():
            transaction = {
                'transaction_id': str(row[actual_columns['transaction_id']]),
                'customer_id': str(row[actual_columns['customer_id']]),
                'amount': float(row[actual_columns['amount']]) if pd.notna(row[actual_columns['amount']]) else 0.0,
                'currency': 'CNY',  # 默认为人民币
                'transaction_date': str(row[actual_columns['transaction_date']])
            }
            
            # 添加可选字段
            for key in ['status', 'payment_method', 'product_type']:
                if key in actual_columns and pd.notna(row[actual_columns[key]]):
                    transaction[key] = str(row[actual_columns[key]])
            
            transactions.append(transaction)
        
        return {"transactions": transactions}
    
    def merge_imported_data(self, imported_data):
        """将导入的数据合并到当前的计费管理器中"""
        if not self.billing_manager:
            return False, "BillingManager未初始化"
        
        try:
            # 添加导入的交易
            for transaction in imported_data["transactions"]:
                # 检查是否已存在相同ID的交易
                existing = next((t for t in self.billing_manager.transactions if t["transaction_id"] == transaction["transaction_id"]), None)
                if not existing:
                    self.billing_manager.transactions.append(transaction)
            
            return True, f"成功导入 {len(imported_data['transactions'])} 笔交易"
        except Exception as e:
            return False, f"数据合并失败: {str(e)}"

# 模拟计费数据管理器
class BillingManager:
    def __init__(self, use_real_data=False, data_source=None):
        self.use_real_data = use_real_data
        self.data_source = data_source
        
        # 根据数据来源决定是否生成模拟数据
        if use_real_data:
            # 使用真实数据时，初始化为空列表
            self.transactions = []
            self.customers = []
        else:
            # 模拟计费数据
            self.transactions = self._generate_mock_data()
            self.customers = self._generate_mock_customers()
    
    def _generate_mock_customers(self):
        # 生成模拟客户数据
        customer_names = [f"客户{i}" for i in range(1, 31)]
        customers = []
        for i, name in enumerate(customer_names):
            customers.append({
                'customer_id': f'CUST{i+1:03d}',
                'customer_name': name,
                'contact_email': f'contact{i+1}@example.com',
                'registration_date': (datetime.now() - timedelta(days=random.randint(10, 365))).strftime('%Y-%m-%d')
            })
        return customers
    
    def _generate_mock_data(self):
        # 生成模拟交易数据
        transactions = []
        statuses = ['成功', '失败', '处理中', '已退款']
        payment_methods = ['支付宝', '微信支付', '银行转账', '信用卡']
        products = ['基础版', '专业版', '企业版', '高级版']
        
        # 生成过去90天的数据
        for i in range(500):
            date = datetime.now() - timedelta(days=random.randint(0, 90))
            transaction = {
                'transaction_id': f'TX{i+1:05d}',
                'customer_id': f'CUST{random.randint(1, 30):03d}',
                'amount': round(random.uniform(100, 10000), 2),
                'currency': 'CNY',
                'transaction_date': date.strftime('%Y-%m-%d %H:%M:%S'),
                'status': random.choice(statuses),
                'payment_method': random.choice(payment_methods),
                'product_type': random.choice(products),
                'invoice_number': f'INV{date.strftime("%Y%m")}{i+1:05d}',
                'description': f'订阅 {random.choice(products)} 服务'
            }
            transactions.append(transaction)
        
        return transactions
    
    def get_billing_summary(self):
        # 获取计费摘要统计信息
        df = pd.DataFrame(self.transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # 计算总交易量
        total_transactions = len(df)
        
        # 计算总交易额
        total_amount = df[df['status'] == '成功']['amount'].sum()
        
        # 计算今日交易额
        today = datetime.now().date()
        today_amount = df[(df['transaction_date'].dt.date == today) & 
                         (df['status'] == '成功')]['amount'].sum()
        
        # 计算本月交易额
        this_month = datetime.now().strftime('%Y-%m')
        month_amount = df[(df['transaction_date'].dt.strftime('%Y-%m') == this_month) & 
                         (df['status'] == '成功')]['amount'].sum()
        
        # 计算失败交易数
        failed_transactions = len(df[df['status'] == '失败'])
        
        return {
            'total_transactions': total_transactions,
            'total_amount': round(total_amount, 2),
            'today_amount': round(today_amount, 2),
            'month_amount': round(month_amount, 2),
            'failed_transactions': failed_transactions
        }
    
    def search_transactions(self, search_term=None, status=None, start_date=None, end_date=None, 
                           min_amount=None, max_amount=None, product_type=None):
        # 搜索和筛选交易记录
        df = pd.DataFrame(self.transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # 应用搜索条件
        if search_term:
            mask = df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
            df = df[mask]
        
        if status and status != '全部':
            df = df[df['status'] == status]
        
        if start_date:
            df = df[df['transaction_date'] >= pd.to_datetime(start_date)]
        
        if end_date:
            df = df[df['transaction_date'] <= pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)]
        
        if min_amount is not None:
            df = df[df['amount'] >= min_amount]
        
        if max_amount is not None:
            df = df[df['amount'] <= max_amount]
        
        if product_type and product_type != '全部':
            df = df[df['product_type'] == product_type]
        
        # 按交易日期降序排序
        df = df.sort_values(by='transaction_date', ascending=False)
        
        return df
    
    def get_monthly_revenue_trend(self, months=6):
        # 获取月度收入趋势
        df = pd.DataFrame(self.transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['month'] = df['transaction_date'].dt.strftime('%Y-%m')
        
        # 过滤成功的交易
        success_df = df[df['status'] == '成功']
        
        # 按月份分组计算收入
        monthly_revenue = success_df.groupby('month')['amount'].sum().reset_index()
        
        # 确保有最近几个月的数据
        current_date = datetime.now()
        months_list = []
        
        for i in range(months-1, -1, -1):
            month_date = current_date - timedelta(days=current_date.day)
            month_date = month_date - timedelta(days=i*30)
            months_list.append(month_date.strftime('%Y-%m'))
        
        # 创建完整的月份数据框
        full_months_df = pd.DataFrame({'month': months_list})
        full_months_df = pd.merge(full_months_df, monthly_revenue, on='month', how='left').fillna(0)
        
        return full_months_df
    
    def export_transactions_to_csv(self, transactions_df):
        # 导出交易记录到CSV
        csv_buffer = io.StringIO()
        transactions_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_string = csv_buffer.getvalue()
        
        # 生成base64编码的下载链接
        b64 = base64.b64encode(csv_string.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="transactions.csv">下载CSV文件</a>'
        
        return href

# 渲染计费管理页面
def render_billing_management():
    st.title("计费管理")
    
    # 初始化文件导入器
    if 'file_importer' not in st.session_state:
        st.session_state.file_importer = FileImporter()
    file_importer = st.session_state.file_importer
    
    # 侧边栏：数据管理选项
    with st.sidebar:
        st.subheader("数据管理")
        
        # 数据来源选择
        data_source = st.radio(
            "选择数据来源",
            ["模拟数据", "上传文件"],
            key="billing_data_source"
        )
    
    # 主界面文件上传区域（当选择上传文件时显示）
    uploaded_file = None
    if data_source == "上传文件":
        st.subheader("📁 上传计费数据文件")
        
        # 支持多种文件格式上传
        supported_formats = ['.xlsx', '.xls', '.csv', '.txt', '.pdf', '.docx']
        if HAS_OCR_SUPPORT:
            supported_formats.extend(['.png', '.jpg', '.jpeg'])
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "选择交易数据文件",
                type=[fmt[1:] for fmt in supported_formats],
                help="支持Excel、CSV、文本、PDF、Word和图片文件"
            )
        
        with col2:
            st.write(" ")  # 占位，使按钮垂直居中
            if st.button("📥 导入数据", use_container_width=True):
                if uploaded_file:
                    try:
                        # 导入文件数据
                        imported_data = file_importer.import_file(uploaded_file)
                        # 创建新的BillingManager实例，指定使用真实数据
                        new_billing_manager = BillingManager(use_real_data=True)
                        # 直接设置为导入的数据，确保清空原有模拟数据
                        new_billing_manager.transactions = imported_data.get("transactions", [])
                        st.session_state.billing_manager = new_billing_manager
                        # 将billing_manager关联到file_importer
                        file_importer.billing_manager = new_billing_manager
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.success(f"✅ 成功导入数据: {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"❌ 导入失败: {str(e)}")
        
        with col3:
            st.write(" ")  # 占位，使按钮垂直居中
            if st.button("🔄 重置为模拟数据", use_container_width=True):
                st.session_state.billing_manager = BillingManager()
                # 更新file_importer的billing_manager引用
                file_importer.billing_manager = st.session_state.billing_manager
                if 'uploaded_file_name' in st.session_state:
                    del st.session_state['uploaded_file_name']
                st.success("已重置为模拟数据")
        
        # 显示支持的文件格式信息
        supported_formats_text = ", ".join([fmt.upper() for fmt in supported_formats])
        st.caption(f"支持格式: {supported_formats_text}")
        if HAS_OCR_SUPPORT:
            st.caption("🖼️ 支持OCR功能，可从图片中提取文字")
    
    # 初始化计费管理器（如果不存在或数据来源变更）
    if 'billing_manager' not in st.session_state or \
       (data_source == "模拟数据" and hasattr(st.session_state.billing_manager, 'use_real_data') and st.session_state.billing_manager.use_real_data) or \
       (data_source == "上传文件" and uploaded_file):
        
        if data_source == "模拟数据":
            st.session_state.billing_manager = BillingManager()
        elif data_source == "上传文件":
            # 确保上传文件模式下初始化为空数据
            if 'billing_manager' not in st.session_state:
                st.session_state.billing_manager = BillingManager(use_real_data=True)
    
    billing_manager = st.session_state.billing_manager
    
    # 获取计费摘要
    summary = billing_manager.get_billing_summary()
    
    # 显示统计卡片
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("总交易笔数", summary['total_transactions'])
    
    with col2:
        st.metric("总交易额(元)", summary['total_amount'])
    
    with col3:
        st.metric("今日交易额(元)", summary['today_amount'])
    
    with col4:
        st.metric("本月交易额(元)", summary['month_amount'])
    
    with col5:
        st.metric("失败交易数", summary['failed_transactions'])
    
    st.divider()
    
    # 交易记录搜索和筛选
    st.subheader("交易记录查询")
    
    # 搜索和筛选表单
    search_term = st.text_input("搜索关键词")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = st.selectbox("交易状态", ['全部', '成功', '失败', '处理中', '已退款'])
    
    with col2:
        product_type = st.selectbox("产品类型", ['全部', '基础版', '专业版', '企业版', '高级版'])
    
    with col3:
        start_date = st.date_input("开始日期", value=None, format="YYYY-MM-DD")
    
    with col4:
        end_date = st.date_input("结束日期", value=None, format="YYYY-MM-DD")
    
    # 金额范围筛选
    min_max_col1, min_max_col2 = st.columns(2)
    
    with min_max_col1:
        min_amount = st.number_input("最小金额", min_value=0.0, step=0.01, value=None, placeholder="最小金额")
    
    with min_max_col2:
        max_amount = st.number_input("最大金额", min_value=0.0, step=0.01, value=None, placeholder="最大金额")
    
    # 搜索按钮
    search_button = st.button("搜索")
    
    # 执行搜索
    if search_button or search_term or status != '全部' or product_type != '全部' or start_date or end_date or min_amount is not None or max_amount is not None:
        transactions_df = billing_manager.search_transactions(
            search_term=search_term,
            status=status,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            product_type=product_type
        )
    else:
        # 默认显示最近50条交易记录
        transactions_df = pd.DataFrame(billing_manager.transactions)
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        transactions_df = transactions_df.sort_values(by='transaction_date', ascending=False).head(50)
    
    # 显示交易记录表格
    if not transactions_df.empty:
        st.subheader(f"交易记录 (共 {len(transactions_df)} 条)")
        
        # 格式化交易日期
        transactions_df['transaction_date'] = transactions_df['transaction_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 显示表格
        st.dataframe(transactions_df, width='stretch', hide_index=True)
        
        # 导出按钮
        csv_href = billing_manager.export_transactions_to_csv(transactions_df)
        st.markdown(csv_href, unsafe_allow_html=True)
    else:
        st.info("没有找到符合条件的交易记录")
    
    st.divider()
    
    # 显示收入趋势图表
    st.subheader("收入趋势")
    trend_df = billing_manager.get_monthly_revenue_trend(months=6)
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(trend_df['month'], trend_df['amount'], marker='o', linestyle='-', color='#1f77b4')
    ax.set_title('近6个月收入趋势')
    ax.set_xlabel('月份')
    ax.set_ylabel('收入金额 (元)')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 格式化y轴为货币格式
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f'{x:.0f}'))
    
    # 调整布局
    plt.tight_layout()
    
    # 显示图表
    st.pyplot(fig)