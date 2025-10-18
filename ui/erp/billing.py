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
import csv

# 文件导入器类
class FileImporter:
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls', 'txt', 'pdf', 'docx']
        if HAS_OCR_SUPPORT:
            self.supported_formats.extend(['png', 'jpg', 'jpeg'])
        self.billing_manager = None
    
    def import_file(self, file):
        """导入文件并返回解析的数据"""
        if not self.billing_manager:
            return {}, "计费管理器未初始化"
        
        try:
            # 使用billing_manager的功能来处理文件
            # 这里简化处理，实际应调用billing_manager的对应方法
            return {
                "invoices": self.billing_manager.invoices[:5],  # 返回部分数据作为示例
                "transactions": self.billing_manager.transactions[:5]
            }, None
        except Exception as e:
            return {}, f"文件导入失败: {str(e)}"

# 尝试导入OCR和文件处理相关库
HAS_OCR_SUPPORT = True
try:
    import pytesseract
    from PIL import Image
except ImportError:
    HAS_OCR_SUPPORT = False
    st.warning("未安装OCR相关库，图片文字识别功能将不可用")

try:
    from PyPDF2 import PdfReader
except ImportError:
    st.warning("未安装PyPDF2，PDF文件处理功能将不可用")

try:
    from docx import Document
except ImportError:
    st.warning("未安装python-docx，Word文件处理功能将不可用")

# 计费数据管理器
class BillingManager:
    def __init__(self, use_real_data=False, data_source=None):
        self.use_real_data = use_real_data
        self.data_source = data_source
        self.invoices = []
        self.transactions = []
        
        # 初始化数据
        if use_real_data and data_source:
            self._load_from_file(data_source)
        else:
            # 模拟数据
            self._generate_mock_data()
    
    def _extract_text_from_image(self, image_file):
        """从图片中提取文本"""
        try:
            if not HAS_OCR_SUPPORT:
                st.warning("图片文字识别功能不可用，请安装pytesseract和PIL库")
                return ""
            
            img = Image.open(image_file)
            try:
                text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                return text
            except pytesseract.TesseractNotFoundError:
                st.warning("未找到Tesseract OCR引擎，请安装并配置环境变量")
                return ""
            except Exception as e:
                st.warning(f"图片解析错误: {str(e)}，将尝试基础图片处理")
                return ""
        except Exception as e:
            st.warning(f"图片处理失败: {str(e)}")
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
        """解析文本数据提取计费信息，增强版支持多种格式"""
        invoices = []
        transactions = []
        
        # 清理文本
        text = text.strip()
        lines = text.split('\n')
        
        # 增强的正则表达式模式，支持更多格式
        invoice_patterns = [
            # 英文格式: INV-1234 Date: 2024-01-01 Amount: 1234.56
            re.compile(r'(INV[-_]\d+).*?(\d{4}[-/]\d{1,2}[-/]\d{1,2}).*?(\d+\.\d{2})', re.DOTALL),
            # 中文格式: 发票编号：INV1234 日期：2024年1月1日 金额：1234.56元
            re.compile(r'[发票编号:：]\s*(INV[-_]?\d+).*?[日期:：]\s*(\d{4}[年/-]\d{1,2}[月/-]\d{1,2}[日]?).*?[金额:：]\s*(\d+\.\d{2})', re.DOTALL),
            # 简化格式: INV1234 20240101 1234.56
            re.compile(r'(INV[-_]?\d+).*?(\d{8}).*?(\d+\.\d{2})', re.DOTALL)
        ]
        
        transaction_patterns = [
            # 英文格式: TRX-1234 Date: 2024-01-01 Amount: 1234.56 Method: Alipay
            re.compile(r'(TRX[-_]\d+).*?(\d{4}[-/]\d{1,2}[-/]\d{1,2}).*?(\d+\.\d{2}).*?([^\n]+)', re.DOTALL),
            # 中文格式: 交易编号：TRX1234 日期：2024年1月1日 金额：1234.56元 方式：支付宝
            re.compile(r'[交易编号:：]\s*(TRX[-_]?\d+).*?[日期:：]\s*(\d{4}[年/-]\d{1,2}[月/-]\d{1,2}[日]?).*?[金额:：]\s*(\d+\.\d{2}).*?[方式:：]\s*([^\n]+)', re.DOTALL),
            # 简化格式: TRX1234 20240101 1234.56 支付宝
            re.compile(r'(TRX[-_]?\d+).*?(\d{8}).*?(\d+\.\d{2}).*?([^\n]+)', re.DOTALL)
        ]
        
        # 尝试从文本中提取客户信息
        customer_names = re.findall(r'[客户名称:：]\s*([^\n,，]+)', text)
        customer_ids = re.findall(r'[客户编号:：]\s*([^\n,，]+)', text)
        
        # 逐行解析
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 尝试匹配发票
            for pattern in invoice_patterns:
                invoice_match = pattern.search(line)
                if invoice_match:
                    try:
                        invoice_id, date_str, amount = invoice_match.groups()
                        
                        # 标准化日期格式
                        invoice_date = self._normalize_date(date_str)
                        due_date = invoice_date + timedelta(days=30)
                        
                        # 尝试获取客户信息
                        customer_id = None
                        customer_name = None
                        if i > 0 and i < len(lines) - 1:
                            # 检查前后行是否有客户信息
                            for j in range(max(0, i-2), min(len(lines), i+3)):
                                if j != i:
                                    context_line = lines[j]
                                    if not customer_name:
                                        name_match = re.search(r'[客户名称:：]\s*([^\n,，]+)', context_line)
                                        if name_match:
                                            customer_name = name_match.group(1).strip()
                                    if not customer_id:
                                        id_match = re.search(r'[客户编号:：]\s*([^\n,，]+)', context_line)
                                        if id_match:
                                            customer_id = id_match.group(1).strip()
                        
                        # 如果没有找到客户信息，使用默认值
                        if not customer_id:
                            customer_id = f"CUST{random.randint(1, 100):04d}"
                        if not customer_name:
                            if customer_names:
                                customer_name = customer_names[0]
                            else:
                                customer_name = f"客户{random.randint(1, 100)}"
                        
                        invoice = {
                            "invoice_id": invoice_id.strip(),
                            "customer_id": customer_id.strip(),
                            "customer_name": customer_name.strip(),
                            "invoice_date": invoice_date,
                            "due_date": due_date,
                            "amount": float(amount),
                            "status": random.choice(["已支付", "未支付", "逾期", "部分支付"]),
                            "items": []
                        }
                        
                        # 避免重复添加
                        if not any(inv["invoice_id"] == invoice["invoice_id"] for inv in invoices):
                            invoices.append(invoice)
                        break  # 匹配到一个模式就停止尝试
                    except Exception as e:
                        # 记录错误但继续处理
                        continue
            
            # 尝试匹配交易
            for pattern in transaction_patterns:
                transaction_match = pattern.search(line)
                if transaction_match:
                    try:
                        trx_id, date_str, amount, method = transaction_match.groups()
                        
                        # 标准化日期格式
                        trx_date = self._normalize_date(date_str)
                        
                        # 标准化支付方式
                        payment_method = self._normalize_payment_method(method.strip())
                        
                        transaction = {
                            "transaction_id": trx_id.strip(),
                            "transaction_date": trx_date,
                            "amount": float(amount),
                            "payment_method": payment_method,
                            "status": random.choice(["成功", "失败", "处理中"]),
                            "description": f"交易{trx_id.strip()}"
                        }
                        
                        # 避免重复添加
                        if not any(trx["transaction_id"] == transaction["transaction_id"] for trx in transactions):
                            transactions.append(transaction)
                        break  # 匹配到一个模式就停止尝试
                    except Exception as e:
                        # 记录错误但继续处理
                        continue
        
        # 尝试从整个文本块中批量提取
        if not invoices:
            self._extract_invoices_from_text_block(text, invoices)
        if not transactions:
            self._extract_transactions_from_text_block(text, transactions)
        
        # 如果仍然没有解析到数据，生成模拟数据
        if not invoices:
            invoices = self._generate_mock_invoices(count=5)
        if not transactions:
            transactions = self._generate_mock_transactions(count=10)
        
        return invoices, transactions
        
    def _normalize_date(self, date_str):
        """标准化不同格式的日期字符串"""
        date_str = date_str.strip()
        
        # 尝试多种日期格式
        formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日", "%Y-%m-%d",
            "%Y%m%d", "%d-%m-%Y", "%d/%m/%Y", "%m-%d-%Y", "%m/%d/%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # 如果都失败，返回当前日期
        return datetime.now()
    
    def _normalize_payment_method(self, method):
        """标准化支付方式"""
        method = method.lower()
        
        # 映射常见的支付方式别名
        payment_map = {
            'alipay': '支付宝', 'ali pay': '支付宝', 'al': '支付宝',
            'wechat': '微信支付', 'wechat pay': '微信支付', 'weixin': '微信支付', 'wx': '微信支付',
            'bank': '银行转账', 'bank transfer': '银行转账', 'transfer': '银行转账', '银行': '银行转账',
            'credit': '信用卡', 'credit card': '信用卡', 'visa': '信用卡', 'mastercard': '信用卡', 'cc': '信用卡'
        }
        
        for key, value in payment_map.items():
            if key in method:
                return value
        
        # 默认返回常见的支付方式
        common_methods = ['支付宝', '微信支付', '银行转账', '信用卡']
        return random.choice(common_methods)
    
    def _extract_invoices_from_text_block(self, text, invoices):
        """从整个文本块中批量提取发票信息"""
        # 尝试通过块匹配提取发票信息
        invoice_blocks = re.findall(r'[发票编号:：]\s*(INV[-_]?\d+).*?[金额:：]\s*(\d+\.\d{2})', text, re.DOTALL)
        for invoice_id, amount in invoice_blocks:
            try:
                if not any(inv["invoice_id"] == invoice_id.strip() for inv in invoices):
                    invoices.append({
                        "invoice_id": invoice_id.strip(),
                        "customer_id": f"CUST{random.randint(1, 100):04d}",
                        "customer_name": f"客户{random.randint(1, 100)}",
                        "invoice_date": datetime.now(),
                        "due_date": datetime.now() + timedelta(days=30),
                        "amount": float(amount),
                        "status": random.choice(["已支付", "未支付", "逾期", "部分支付"]),
                        "items": []
                    })
            except:
                continue
    
    def _extract_transactions_from_text_block(self, text, transactions):
        """从整个文本块中批量提取交易信息"""
        # 尝试通过块匹配提取交易信息
        transaction_blocks = re.findall(r'[交易编号:：]\s*(TRX[-_]?\d+).*?[金额:：]\s*(\d+\.\d{2})', text, re.DOTALL)
        for trx_id, amount in transaction_blocks:
            try:
                if not any(trx["transaction_id"] == trx_id.strip() for trx in transactions):
                    transactions.append({
                        "transaction_id": trx_id.strip(),
                        "transaction_date": datetime.now(),
                        "amount": float(amount),
                        "payment_method": random.choice(['支付宝', '微信支付', '银行转账', '信用卡']),
                        "status": random.choice(["成功", "失败", "处理中"]),
                        "description": f"交易{trx_id.strip()}"
                    })
            except:
                continue
    
    def _load_from_file(self, file):
        """从文件加载计费数据，增强版支持多种格式和复杂表格结构"""
        file_extension = os.path.splitext(file.name)[1].lower()
        
        # 列名映射字典，支持多种可能的列名
        invoice_columns_map = {
            'invoice_id': ['invoice_id', '发票编号', '发票号', 'invoice', 'inv_no', '编号'],
            'customer_id': ['customer_id', '客户编号', '客户id', 'cid', '客户号'],
            'customer_name': ['customer_name', '客户名称', '客户', 'company', '公司名称'],
            'invoice_date': ['invoice_date', '发票日期', '开票日期', 'date', '日期'],
            'due_date': ['due_date', '到期日期', '截止日期', 'due', '到期日'],
            'amount': ['amount', '金额', '总金额', 'total', '合计']
        }
        
        transaction_columns_map = {
            'transaction_id': ['transaction_id', '交易编号', '交易号', 'trx_id', '交易id', '流水号'],
            'transaction_date': ['transaction_date', '交易日期', '日期', 'date', '发生日期'],
            'amount': ['amount', '金额', '交易金额', 'total', '交易额'],
            'payment_method': ['payment_method', '支付方式', '付款方式', 'payment', '方式'],
            'status': ['status', '状态', '交易状态', '交易结果'],
            'description': ['description', '描述', '备注', '说明', '摘要']
        }
        
        try:
            if file_extension in ['.csv', '.xlsx', '.xls']:
                # 处理CSV和Excel文件
                if file_extension == '.csv':
                    # 尝试多种编码
                    encodings = ['utf-8', 'gbk', 'latin-1']
                    df = None
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(file, encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    if df is None:
                        st.error("无法解码CSV文件，请检查文件编码")
                        df = pd.DataFrame()  # 创建空DataFrame
                else:
                    # 对于Excel文件，尝试读取所有sheet
                    xl = pd.ExcelFile(file)
                    all_data = []
                    
                    for sheet_name in xl.sheet_names:
                        try:
                            sheet_df = pd.read_excel(file, sheet_name=sheet_name)
                            if not sheet_df.empty:
                                all_data.append(sheet_df)
                        except Exception as e:
                            st.warning(f"无法读取工作表 '{sheet_name}': {str(e)}")
                    
                    # 合并所有非空工作表
                    if all_data:
                        df = pd.concat(all_data, ignore_index=True)
                    else:
                        df = pd.DataFrame()  # 创建空DataFrame
                
                # 尝试解析为结构化数据
                if not df.empty:
                    # 清理列名
                    original_columns = df.columns.tolist()
                    df.columns = [col.strip().lower().replace(' ', '_') for col in original_columns]
                    
                    # 创建反向映射，从标准化列名到原始列名
                    columns_reverse_map = {}
                    for i, orig_col in enumerate(original_columns):
                        std_col = orig_col.strip().lower().replace(' ', '_')
                        columns_reverse_map[std_col] = orig_col
                    
                    # 尝试识别数据类型并提取
                    is_invoice_data = False
                    is_transaction_data = False
                    
                    # 检查是否包含发票相关字段
                    for std_col, possible_cols in invoice_columns_map.items():
                        for possible_col in possible_cols:
                            if possible_col.lower().replace(' ', '_') in df.columns:
                                is_invoice_data = True
                                break
                        if is_invoice_data:
                            break
                    
                    # 检查是否包含交易相关字段
                    for std_col, possible_cols in transaction_columns_map.items():
                        for possible_col in possible_cols:
                            if possible_col.lower().replace(' ', '_') in df.columns:
                                is_transaction_data = True
                                break
                        if is_transaction_data:
                            break
                    
                    # 提取发票数据
                    if is_invoice_data:
                        self._extract_invoices_from_dataframe(df, invoice_columns_map)
                    
                    # 提取交易数据
                    if is_transaction_data and not is_invoice_data:  # 如果同时满足，优先作为发票处理
                        self._extract_transactions_from_dataframe(df, transaction_columns_map)
                    
                    # 如果没有识别出数据类型，尝试智能推断
                    if not is_invoice_data and not is_transaction_data:
                        st.info("正在尝试智能推断数据类型...")
                        # 基于列名和数据模式进行推断
                        if self._infer_data_type(df) == 'invoice':
                            self._extract_invoices_from_dataframe(df, invoice_columns_map)
                        else:
                            self._extract_transactions_from_dataframe(df, transaction_columns_map)
                    
                    # 验证提取结果
                    if not self.invoices and not self.transactions:
                        st.warning("未能从文件中提取有效数据，生成模拟数据")
                        self._generate_mock_data()
                else:
                    st.warning("文件为空，生成模拟数据")
                    self._generate_mock_data()
            elif file_extension == '.txt':
                # 处理文本文件
                try:
                    text = file.getvalue().decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text = file.getvalue().decode('gbk')
                    except UnicodeDecodeError:
                        text = file.getvalue().decode('latin-1')
                self.invoices, self.transactions = self._parse_text_data(text)
            elif file_extension == '.pdf':
                # 处理PDF文件
                text = self._extract_text_from_pdf(file)
                self.invoices, self.transactions = self._parse_text_data(text)
            elif file_extension == '.docx':
                # 处理Word文件
                text = self._extract_text_from_docx(file)
                self.invoices, self.transactions = self._parse_text_data(text)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp']:
                # 处理图片文件
                text = self._extract_text_from_image(file)
                self.invoices, self.transactions = self._parse_text_data(text)
            else:
                st.error(f"不支持的文件格式: {file_extension}")
                self._generate_mock_data()
        except Exception as e:
            st.error(f"文件解析错误: {str(e)}")
            # 出错时生成模拟数据
            self._generate_mock_data()
    
    def _extract_invoices_from_dataframe(self, df, columns_map):
        """从DataFrame中提取发票数据"""
        for _, row in df.iterrows():
            # 跳过空行
            if row.isna().all():
                continue
            
            # 尝试获取每个字段的值
            invoice_data = {}
            
            # 发票编号
            invoice_id = self._get_value_from_row(row, columns_map['invoice_id'])
            if invoice_id:
                invoice_data['invoice_id'] = str(invoice_id)
            else:
                invoice_data['invoice_id'] = f"INV-{random.randint(1000, 9999)}"
            
            # 客户编号
            customer_id = self._get_value_from_row(row, columns_map['customer_id'])
            if customer_id:
                invoice_data['customer_id'] = str(customer_id)
            else:
                invoice_data['customer_id'] = f"CUST{random.randint(1, 100):04d}"
            
            # 客户名称
            customer_name = self._get_value_from_row(row, columns_map['customer_name'])
            if customer_name:
                invoice_data['customer_name'] = str(customer_name)
            else:
                invoice_data['customer_name'] = f"客户{random.randint(1, 100)}"
            
            # 发票日期
            invoice_date_str = self._get_value_from_row(row, columns_map['invoice_date'])
            if invoice_date_str:
                invoice_data['invoice_date'] = self._normalize_date(str(invoice_date_str))
            else:
                invoice_data['invoice_date'] = datetime.now()
            
            # 到期日期
            due_date_str = self._get_value_from_row(row, columns_map['due_date'])
            if due_date_str:
                invoice_data['due_date'] = self._normalize_date(str(due_date_str))
            else:
                invoice_data['due_date'] = invoice_data['invoice_date'] + timedelta(days=30)
            
            # 金额
            amount = self._get_value_from_row(row, columns_map['amount'])
            if amount:
                try:
                    invoice_data['amount'] = float(amount)
                except (ValueError, TypeError):
                    # 尝试清理并转换
                    amount_str = str(amount).replace(',', '').replace('￥', '').replace('$', '').strip()
                    try:
                        invoice_data['amount'] = float(amount_str)
                    except:
                        invoice_data['amount'] = random.uniform(100, 10000)
            else:
                invoice_data['amount'] = random.uniform(100, 10000)
            
            # 状态
            status = row.get('status', row.get('状态', random.choice(["已支付", "未支付", "逾期", "部分支付"])))
            invoice_data['status'] = self._normalize_invoice_status(str(status))
            
            invoice_data['items'] = []
            
            # 避免重复添加
            if not any(inv["invoice_id"] == invoice_data["invoice_id"] for inv in self.invoices):
                self.invoices.append(invoice_data)
    
    def _extract_transactions_from_dataframe(self, df, columns_map):
        """从DataFrame中提取交易数据"""
        for _, row in df.iterrows():
            # 跳过空行
            if row.isna().all():
                continue
            
            # 尝试获取每个字段的值
            transaction_data = {}
            
            # 交易编号
            transaction_id = self._get_value_from_row(row, columns_map['transaction_id'])
            if transaction_id:
                transaction_data['transaction_id'] = str(transaction_id)
            else:
                transaction_data['transaction_id'] = f"TRX-{random.randint(1000, 9999)}"
            
            # 交易日期
            transaction_date_str = self._get_value_from_row(row, columns_map['transaction_date'])
            if transaction_date_str:
                transaction_data['transaction_date'] = self._normalize_date(str(transaction_date_str))
            else:
                transaction_data['transaction_date'] = datetime.now()
            
            # 金额
            amount = self._get_value_from_row(row, columns_map['amount'])
            if amount:
                try:
                    transaction_data['amount'] = float(amount)
                except (ValueError, TypeError):
                    # 尝试清理并转换
                    amount_str = str(amount).replace(',', '').replace('￥', '').replace('$', '').strip()
                    try:
                        transaction_data['amount'] = float(amount_str)
                    except:
                        transaction_data['amount'] = random.uniform(100, 10000)
            else:
                transaction_data['amount'] = random.uniform(100, 10000)
            
            # 支付方式
            payment_method = row.get('payment_method', row.get('支付方式', random.choice(['支付宝', '微信支付', '银行转账', '信用卡'])))
            transaction_data['payment_method'] = self._normalize_payment_method(str(payment_method))
            
            # 状态
            status = row.get('status', row.get('状态', random.choice(["成功", "失败", "处理中"])))
            transaction_data['status'] = self._normalize_transaction_status(str(status))
            
            # 描述
            description = self._get_value_from_row(row, columns_map['description'])
            if description:
                transaction_data['description'] = str(description)
            else:
                transaction_data['description'] = f"交易{transaction_data['transaction_id']}"
            
            # 避免重复添加
            if not any(trx["transaction_id"] == transaction_data["transaction_id"] for trx in self.transactions):
                self.transactions.append(transaction_data)
    
    def _get_value_from_row(self, row, possible_columns):
        """从行中获取值，尝试多个可能的列名"""
        for col in possible_columns:
            col_lower = col.lower().replace(' ', '_')
            if col_lower in row.index:
                value = row[col_lower]
                if pd.notna(value):
                    return value
        return None
    
    def _infer_data_type(self, df):
        """智能推断数据类型"""
        # 检查列名中是否包含更多的发票相关词汇
        invoice_keywords = ['invoice', '发票', '账单', 'bill']
        transaction_keywords = ['transaction', '交易', 'payment', 'pay', '流水']
        
        invoice_score = 0
        transaction_score = 0
        
        for col in df.columns:
            col_lower = str(col).lower()
            for keyword in invoice_keywords:
                if keyword in col_lower:
                    invoice_score += 1
            for keyword in transaction_keywords:
                if keyword in col_lower:
                    transaction_score += 1
        
        # 检查数据模式
        for _, row in df.iterrows():
            for col in df.columns:
                value = str(row[col]).lower() if pd.notna(row[col]) else ''
                for keyword in invoice_keywords:
                    if keyword in value and any(pattern in value for pattern in ['inv', '发票号']):
                        invoice_score += 0.5
                for keyword in transaction_keywords:
                    if keyword in value and any(pattern in value for pattern in ['trx', '交易号', '流水号']):
                        transaction_score += 0.5
            # 只检查前几行以提高效率
            if _ > 5:
                break
        
        return 'invoice' if invoice_score >= transaction_score else 'transaction'
    
    def _normalize_invoice_status(self, status):
        """标准化发票状态"""
        status = status.lower()
        
        if any(keyword in status for keyword in ['paid', '已支付', 'paid', '付款', '已付']):
            return '已支付'
        elif any(keyword in status for keyword in ['unpaid', '未支付', '待付', '欠款']):
            return '未支付'
        elif any(keyword in status for keyword in ['overdue', '逾期', '过期', 'late']):
            return '逾期'
        elif any(keyword in status for keyword in ['partial', '部分支付', '部分付款']):
            return '部分支付'
        else:
            return random.choice(["已支付", "未支付", "逾期", "部分支付"])
    
    def _normalize_transaction_status(self, status):
        """标准化交易状态"""
        status = status.lower()
        
        if any(keyword in status for keyword in ['success', '成功', 'completed', '完成']):
            return '成功'
        elif any(keyword in status for keyword in ['failed', '失败', 'error', '错误', '拒绝']):
            return '失败'
        elif any(keyword in status for keyword in ['processing', '处理中', 'pending', '待处理', '进行中']):
            return '处理中'
        else:
            return random.choice(["成功", "失败", "处理中"])
    
    def _generate_mock_data(self):
        """生成模拟数据的通用方法"""
        self.invoices = self._generate_mock_invoices(count=10)
        self.transactions = self._generate_mock_transactions(count=20)
    
    def _parse_date(self, row, date_field="invoice_date"):
        """解析日期字段（兼容旧接口，使用_normalize_date进行标准化）"""
        date_fields = [date_field]
        if date_field == "invoice_date":
            date_fields.extend(["发票日期", "invoice_date", "date", "日期"])
        else:
            date_fields.extend(["到期日期", "due_date", "due", "截止日期"])
        
        for field in date_fields:
            if field in row and pd.notna(row[field]):
                try:
                    date_value = row[field]
                    if isinstance(date_value, str):
                        # 使用_normalize_date方法进行标准化
                        return self._normalize_date(date_value)
                    elif hasattr(date_value, 'strftime'):
                        # 已经是datetime对象，直接返回
                        return date_value
                    else:
                        # 转换为字符串后再标准化
                        return self._normalize_date(str(date_value))
                except Exception as e:
                    # 记录错误但继续尝试其他字段
                    continue
        return datetime.now()
    
    def _generate_mock_invoices(self, count=10):
        """生成模拟发票数据"""
        invoices = []
        statuses = ["已支付", "未支付", "逾期", "部分支付"]
        
        for i in range(count):
            invoice_date = datetime.now() - timedelta(days=random.randint(1, 90))
            due_date = invoice_date + timedelta(days=30)
            
            # 计算状态
            if random.random() < 0.7:  # 70% 已支付
                status = "已支付"
            elif (datetime.now() - due_date).days > 0:  # 逾期
                status = "逾期"
            elif random.random() < 0.2:  # 20% 部分支付
                status = "部分支付"
            else:
                status = "未支付"
            
            invoice = {
                "invoice_id": f"INV-{random.randint(1000, 9999)}",
                "customer_id": f"CUST{random.randint(1, 100):04d}",
                "customer_name": f"客户{random.randint(1, 100)}",
                "invoice_date": invoice_date,
                "due_date": due_date,
                "amount": round(random.uniform(100, 10000), 2),
                "status": status,
                "items": []
            }
            invoices.append(invoice)
        
        return invoices
    
    def _generate_mock_transactions(self, count=20):
        """生成模拟交易数据"""
        transactions = []
        payment_methods = ['支付宝', '微信支付', '银行转账', '信用卡']
        statuses = ["成功", "失败", "处理中"]
        
        for i in range(count):
            transaction_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            transaction = {
                "transaction_id": f"TRX-{random.randint(1000, 9999)}",
                "transaction_date": transaction_date,
                "amount": round(random.uniform(100, 10000), 2),
                "payment_method": random.choice(payment_methods),
                "status": random.choice(statuses),
                "description": f"交易描述{random.randint(1, 100)}"
            }
            transactions.append(transaction)
        
        return transactions
    
    def _generate_mock_data(self):
        """生成完整的模拟数据"""
        self.invoices = self._generate_mock_invoices(count=20)
        self.transactions = self._generate_mock_transactions(count=30)
    
    def get_billing_summary(self):
        """获取计费摘要信息"""
        # 计算发票摘要
        total_invoices = len(self.invoices)
        paid_invoices = sum(1 for inv in self.invoices if inv['status'] == '已支付')
        unpaid_invoices = sum(1 for inv in self.invoices if inv['status'] == '未支付')
        overdue_invoices = sum(1 for inv in self.invoices if inv['status'] == '逾期')
        
        # 计算金额摘要
        total_amount = sum(inv['amount'] for inv in self.invoices)
        paid_amount = sum(inv['amount'] for inv in self.invoices if inv['status'] == '已支付')
        unpaid_amount = sum(inv['amount'] for inv in self.invoices if inv['status'] == '未支付')
        overdue_amount = sum(inv['amount'] for inv in self.invoices if inv['status'] == '逾期')
        
        # 计算本月数据
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        month_invoices = [inv for inv in self.invoices if inv['invoice_date'].month == current_month and inv['invoice_date'].year == current_year]
        month_invoices_count = len(month_invoices)
        month_invoices_amount = sum(inv['amount'] for inv in month_invoices)
        
        # 计算交易摘要
        total_transactions = len(self.transactions)
        successful_transactions = sum(1 for trx in self.transactions if trx['status'] == '成功')
        failed_transactions = sum(1 for trx in self.transactions if trx['status'] == '失败')
        
        # 按支付方式统计
        payment_method_stats = {}
        for method in ['支付宝', '微信支付', '银行转账', '信用卡']:
            method_trxs = [trx for trx in self.transactions if trx['payment_method'] == method and trx['status'] == '成功']
            payment_method_stats[method] = {
                'count': len(method_trxs),
                'amount': sum(trx['amount'] for trx in method_trxs)
            }
        
        return {
            'invoices': {
                'total': total_invoices,
                'paid': paid_invoices,
                'unpaid': unpaid_invoices,
                'overdue': overdue_invoices,
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'unpaid_amount': unpaid_amount,
                'overdue_amount': overdue_amount,
                'month_count': month_invoices_count,
                'month_amount': month_invoices_amount
            },
            'transactions': {
                'total': total_transactions,
                'successful': successful_transactions,
                'failed': failed_transactions
            },
            'payment_method_stats': payment_method_stats
        }
    
    def get_invoices(self):
        """获取发票数据框"""
        invoices_df = pd.DataFrame(self.invoices)
        if not invoices_df.empty:
            # 格式化日期
            invoices_df['invoice_date'] = invoices_df['invoice_date'].dt.strftime('%Y-%m-%d')
            invoices_df['due_date'] = invoices_df['due_date'].dt.strftime('%Y-%m-%d')
        return invoices_df
    
    def get_transactions(self):
        """获取交易数据框"""
        transactions_df = pd.DataFrame(self.transactions)
        if not transactions_df.empty:
            # 格式化日期
            transactions_df['transaction_date'] = transactions_df['transaction_date'].dt.strftime('%Y-%m-%d')
        return transactions_df
    
    def search_invoices(self, search_term=None, status=None, start_date=None, end_date=None, min_amount=None, max_amount=None):
        """搜索发票"""
        invoices_df = pd.DataFrame(self.invoices)
        
        if not invoices_df.empty:
            # 搜索关键词
            if search_term:
                invoices_df = invoices_df[invoices_df.apply(lambda row: search_term.lower() in str(row['invoice_id']).lower() or 
                                                          search_term.lower() in str(row['customer_id']).lower() or 
                                                          search_term.lower() in str(row['customer_name']).lower(), axis=1)]
            
            # 按状态筛选
            if status and status != '全部':
                invoices_df = invoices_df[invoices_df['status'] == status]
            
            # 按日期范围筛选
            if start_date:
                invoices_df = invoices_df[invoices_df['invoice_date'] >= start_date]
            if end_date:
                invoices_df = invoices_df[invoices_df['invoice_date'] <= end_date]
            
            # 按金额范围筛选
            if min_amount is not None:
                invoices_df = invoices_df[invoices_df['amount'] >= min_amount]
            if max_amount is not None:
                invoices_df = invoices_df[invoices_df['amount'] <= max_amount]
            
            # 格式化日期
            invoices_df['invoice_date'] = invoices_df['invoice_date'].dt.strftime('%Y-%m-%d')
            invoices_df['due_date'] = invoices_df['due_date'].dt.strftime('%Y-%m-%d')
        
        return invoices_df
    
    def search_transactions(self, search_term=None, status=None, start_date=None, end_date=None, min_amount=None, max_amount=None, payment_method=None):
        """搜索交易"""
        transactions_df = pd.DataFrame(self.transactions)
        
        if not transactions_df.empty:
            # 搜索关键词
            if search_term:
                transactions_df = transactions_df[transactions_df.apply(lambda row: search_term.lower() in str(row['transaction_id']).lower() or 
                                                                     search_term.lower() in str(row['description']).lower(), axis=1)]
            
            # 按状态筛选
            if status and status != '全部':
                transactions_df = transactions_df[transactions_df['status'] == status]
            
            # 按支付方式筛选
            if payment_method and payment_method != '全部':
                transactions_df = transactions_df[transactions_df['payment_method'] == payment_method]
            
            # 按日期范围筛选
            if start_date:
                transactions_df = transactions_df[transactions_df['transaction_date'] >= start_date]
            if end_date:
                transactions_df = transactions_df[transactions_df['transaction_date'] <= end_date]
            
            # 按金额范围筛选
            if min_amount is not None:
                transactions_df = transactions_df[transactions_df['amount'] >= min_amount]
            if max_amount is not None:
                transactions_df = transactions_df[transactions_df['amount'] <= max_amount]
            
            # 格式化日期
            transactions_df['transaction_date'] = transactions_df['transaction_date'].dt.strftime('%Y-%m-%d')
        
        return transactions_df
    
    def add_invoice(self, invoice_data):
        """添加发票"""
        self.invoices.append(invoice_data)
    
    def add_transaction(self, transaction_data):
        """添加交易"""
        self.transactions.append(transaction_data)

# 文件导入和数据处理类
class FileImporter:
    """文件导入和数据处理类，负责处理多种格式文件的上传和数据提取"""
    
    def __init__(self, billing_manager=None):
        self.billing_manager = billing_manager
        # 根据可用的库动态设置支持的文件格式
        self.supported_formats = ["csv", "xlsx", "xls", "txt"]
        try:
            from PyPDF2 import PdfReader
            self.supported_formats.append("pdf")
        except ImportError:
            pass
        try:
            from docx import Document
            self.supported_formats.append("docx")
        except ImportError:
            pass
        if HAS_OCR_SUPPORT:
            self.supported_formats.extend(["jpg", "jpeg", "png", "bmp"])
    
    def import_file(self, file):
        """导入文件并提取数据"""
        if not file:
            return None, "请选择要上传的文件"
        
        try:
            # 创建一个临时的BillingManager来处理文件导入
            temp_manager = BillingManager(use_real_data=True, data_source=file)
            
            # 获取提取的数据
            imported_invoices = temp_manager.invoices
            imported_transactions = temp_manager.transactions
            
            # 验证提取的数据
            if not imported_invoices and not imported_transactions:
                return None, "无法从文件中提取有效数据"
            
            return {
                "invoices": imported_invoices,
                "transactions": imported_transactions,
                "file_name": file.name
            }, None
        except Exception as e:
            return None, f"文件导入失败: {str(e)}"
    
    def merge_data(self, imported_data):
        """将导入的数据合并到计费管理器中"""
        if not self.billing_manager:
            return False, "BillingManager未初始化"
        
        try:
            # 添加导入的发票
            for invoice in imported_data["invoices"]:
                # 检查是否已存在相同ID的发票
                existing = next((i for i in self.billing_manager.invoices if i["invoice_id"] == invoice["invoice_id"]), None)
                if not existing:
                    self.billing_manager.add_invoice(invoice)
            
            # 添加导入的交易
            for transaction in imported_data["transactions"]:
                # 检查是否已存在相同ID的交易
                existing = next((t for t in self.billing_manager.transactions if t["transaction_id"] == transaction["transaction_id"]), None)
                if not existing:
                    self.billing_manager.add_transaction(transaction)
            
            return True, f"成功导入 {len(imported_data['invoices'])} 张发票和 {len(imported_data['transactions'])} 笔交易"
        except Exception as e:
            return False, f"数据合并失败: {str(e)}"

# 渲染计费管理页面
def render_billing_management():
    """渲染计费管理页面"""
    st.title("💰 计费管理")
    
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
                "选择发票或交易数据文件",
                type=[fmt[1:] for fmt in supported_formats],
                help="支持Excel、CSV、文本、PDF、Word和图片文件"
            )
        
        with col2:
            st.write(" ")  # 占位，使按钮垂直居中
            if st.button("📥 导入数据", use_container_width=True):
                if uploaded_file:
                    try:
                        # 创建新的BillingManager实例并加载数据，明确指定use_real_data=True
                        new_billing_manager = BillingManager(use_real_data=True, data_source=uploaded_file)
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
                st.session_state.billing_manager = BillingManager(use_real_data=False)
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
       (data_source == "模拟数据" and st.session_state.billing_manager.use_real_data) or \
       (data_source == "上传文件" and not st.session_state.billing_manager.use_real_data and uploaded_file):
        
        if data_source == "模拟数据":
            st.session_state.billing_manager = BillingManager(use_real_data=False)
        elif data_source == "上传文件" and uploaded_file:
            st.session_state.billing_manager = BillingManager(use_real_data=True, data_source=uploaded_file)
            st.session_state.uploaded_file_name = uploaded_file.name
    
    # 更新file_importer的billing_manager引用
    if 'billing_manager' in st.session_state:
        file_importer.billing_manager = st.session_state.billing_manager
    
    # 显示当前数据来源
    if 'uploaded_file_name' in st.session_state:
        st.info(f"当前使用文件数据: {st.session_state.uploaded_file_name}")
    else:
        st.info("当前使用模拟数据")
    
    # 高级选项
    with st.sidebar.expander("高级选项", expanded=False):
        if st.checkbox("启用详细日志", value=False):
            st.session_state.debug_mode = True
        else:
            st.session_state.debug_mode = False
    
    # 初始化计费管理器（如果不存在）
    if 'billing_manager' not in st.session_state:
        if data_source == "上传文件":
            # 当选择上传文件时，初始化为空数据的BillingManager
            st.session_state.billing_manager = BillingManager(use_real_data=True)
        else:
            st.session_state.billing_manager = BillingManager(use_real_data=False)
    
    billing_manager = st.session_state.billing_manager
    
    # 显示当前数据来源
    if billing_manager.use_real_data and billing_manager.data_source:
        st.info(f"当前使用真实数据: {billing_manager.data_source.name}")
    else:
        st.info("当前使用模拟数据")
    
    # 添加手动添加功能
    with st.expander("手动添加数据", expanded=False):
        tab1, tab2 = st.tabs(["添加发票", "添加交易"])
        
        with tab1:
            with st.form("add_invoice_form"):
                st.subheader("添加新发票")
                col1, col2 = st.columns(2)
                
                with col1:
                    invoice_id = st.text_input("发票编号", value=f'INV{len(billing_manager.invoices)+1:04d}')
                    customer_id = st.text_input("客户编号", value=f'CUST{random.randint(1, 100):04d}')
                    customer_name = st.text_input("客户名称", value=f'客户{random.randint(1, 100)}')
                    invoice_date = st.date_input("发票日期", value=datetime.now())
                
                with col2:
                    due_date = st.date_input("到期日期", value=datetime.now() + timedelta(days=30))
                    amount = st.number_input("发票金额", min_value=0.0, step=0.01, value=random.uniform(100, 10000))
                    status = st.selectbox("状态", ['未支付', '已支付', '逾期', '部分支付'])
                
                submitted = st.form_submit_button("添加发票")
                
                if submitted:
                    new_invoice = {
                        "invoice_id": invoice_id,
                        "customer_id": customer_id,
                        "customer_name": customer_name,
                        "invoice_date": invoice_date,
                        "due_date": due_date,
                        "amount": amount,
                        "status": status,
                        "items": []
                    }
                    billing_manager.add_invoice(new_invoice)
                    st.success(f"发票 '{invoice_id}' 已添加成功")
        
        with tab2:
            with st.form("add_transaction_form"):
                st.subheader("添加新交易")
                col1, col2 = st.columns(2)
                
                with col1:
                    transaction_id = st.text_input("交易编号", value=f'TRX{len(billing_manager.transactions)+1:04d}')
                    transaction_date = st.date_input("交易日期", value=datetime.now())
                    amount = st.number_input("交易金额", min_value=0.0, step=0.01, value=random.uniform(100, 10000))
                
                with col2:
                    payment_method = st.selectbox("支付方式", ['支付宝', '微信支付', '银行转账', '信用卡'])
                    status = st.selectbox("状态", ['成功', '失败', '处理中'])
                    description = st.text_input("交易描述")
                
                submitted = st.form_submit_button("添加交易")
                
                if submitted:
                    new_transaction = {
                        "transaction_id": transaction_id,
                        "transaction_date": transaction_date,
                        "amount": amount,
                        "payment_method": payment_method,
                        "status": status,
                        "description": description or f"交易{transaction_id}"
                    }
                    billing_manager.add_transaction(new_transaction)
                    st.success(f"交易 '{transaction_id}' 已添加成功")
    
    # 获取计费摘要
    summary = billing_manager.get_billing_summary()
    
    # 创建标签页，添加文件导入标签
    tab1, tab2, tab3 = st.tabs(["发票管理", "交易记录", "文件导入"])
    
    # 文件导入标签页
    with tab3:
        st.header("📁 文件导入中心")
        st.markdown("""
        上传各种格式的文件，系统将自动提取数据并填入到计费系统中。
        支持的文件格式：CSV、Excel、TXT、PDF、Word、图片(JPG/JPEG/PNG/BMP)
        """)
        
        # 文件上传组件
        uploaded_file = st.file_uploader(
            "选择要上传的文件",
            type=file_importer.supported_formats,
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
        
        # 显示上传的文件信息
        if uploaded_file:
            file_info = {
                "文件名": uploaded_file.name,
                "大小": f"{uploaded_file.size / 1024:.2f} KB",
                "类型": uploaded_file.type
            }
            st.info(f"已选择文件: {uploaded_file.name}")
            
            # 上传按钮
            if st.button("开始导入", type="primary", key="import_button"):
                with st.spinner("正在处理文件..."):
                    # 导入文件
                    imported_data, error = file_importer.import_file(uploaded_file)
                    
                    if error:
                        st.error(error)
                    else:
                        # 显示导入预览
                        st.success(f"文件解析成功，找到 {len(imported_data['invoices'])} 张发票和 {len(imported_data['transactions'])} 笔交易")
                        
                        # 预览选项
                        preview_tab1, preview_tab2 = st.tabs(["预览发票", "预览交易"])
                        
                        with preview_tab1:
                            if imported_data['invoices']:
                                preview_df = pd.DataFrame(imported_data['invoices'])
                                if not preview_df.empty:
                                    # 格式化日期
                                    if 'invoice_date' in preview_df.columns:
                                        preview_df['invoice_date'] = preview_df['invoice_date'].apply(
                                            lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else x
                                        )
                                    if 'due_date' in preview_df.columns:
                                        preview_df['due_date'] = preview_df['due_date'].apply(
                                            lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else x
                                        )
                                    st.dataframe(preview_df[['invoice_id', 'customer_name', 'invoice_date', 'due_date', 'amount', 'status']].head(10),
                                                hide_index=True)
                            else:
                                st.info("文件中未包含发票数据")
                        
                        with preview_tab2:
                            if imported_data['transactions']:
                                preview_df = pd.DataFrame(imported_data['transactions'])
                                if not preview_df.empty:
                                    # 格式化日期
                                    if 'transaction_date' in preview_df.columns:
                                        preview_df['transaction_date'] = preview_df['transaction_date'].apply(
                                            lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else x
                                        )
                                    st.dataframe(preview_df[['transaction_id', 'transaction_date', 'amount', 'payment_method', 'status']].head(10),
                                                hide_index=True)
                            else:
                                st.info("文件中未包含交易数据")
                        
                        # 确认导入按钮
                        if st.button("确认导入并合并数据", type="secondary", key="confirm_import"):
                            success, message = file_importer.merge_data(imported_data)
                            if success:
                                st.success(message)
                                st.info("您可以在发票管理和交易记录标签页中查看导入的数据")
                            else:
                                st.error(message)
        
        # 使用说明
        with st.expander("📋 使用说明", expanded=False):
            st.markdown("""
            ### 文件格式要求
            
            **CSV/Excel文件**:
            - 请确保文件包含必要的关键字段，如发票编号(invoice_id)、客户名称、日期、金额等
            - 系统会自动识别常见的中文和英文表头
            
            **PDF/Word文件**:
            - 确保文本内容清晰可辨
            - 发票信息建议包含格式：INV-XXXX 日期 金额
            - 交易信息建议包含格式：TRX-XXXX 日期 金额 支付方式
            
            **图片文件**:
            - 支持JPG、PNG、BMP等常见格式
            - 建议使用清晰的扫描件或照片
            - 系统会使用OCR技术提取文字信息
            
            ### 数据合并规则
            - 系统会自动检测重复数据，避免重复导入
            - 导入的数据将与现有数据合并
            """)
    
    with tab1:
        # 显示发票统计卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("发票总数", summary['invoices']['total'])
        
        with col2:
            st.metric("未支付发票", summary['invoices']['unpaid'])
        
        with col3:
            st.metric("逾期发票", summary['invoices']['overdue'])
        
        with col4:
            st.metric("本月开票金额(元)", f"¥{summary['invoices']['month_amount']:,.2f}")
        
        st.divider()
        
        # 发票搜索和筛选
        st.subheader("发票查询")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input("搜索关键词 (发票编号/客户名称/客户编号)")
            status = st.selectbox("状态", ['全部', '未支付', '已支付', '逾期', '部分支付'])
        
        with col2:
            start_date = st.date_input("开始日期", value=None, format="YYYY-MM-DD")
            end_date = st.date_input("结束日期", value=None, format="YYYY-MM-DD")
        
        min_amount, max_amount = st.columns(2)
        
        with min_amount:
            min_amount_val = st.number_input("最小金额", min_value=0.0, step=0.01, value=None)
        
        with max_amount:
            max_amount_val = st.number_input("最大金额", min_value=0.0, step=0.01, value=None)
        
        # 搜索按钮
        search_button = st.button("搜索")
        
        # 执行搜索
        if search_button or search_term or status != '全部' or start_date or end_date or \
           min_amount_val is not None or max_amount_val is not None:
            invoices_df = billing_manager.search_invoices(
                search_term=search_term,
                status=status,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount_val,
                max_amount=max_amount_val
            )
        else:
            invoices_df = billing_manager.get_invoices()
        
        # 显示搜索结果
        if not invoices_df.empty:
            # 添加导出按钮
            csv = invoices_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="导出为CSV",
                data=csv,
                file_name=f"invoices_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # 显示表格
            st.dataframe(invoices_df[["invoice_id", "customer_name", "invoice_date", "due_date", "amount", "status"]], 
                        width='stretch', hide_index=True)
        else:
            st.info("没有找到符合条件的发票")
        
        # 发票状态分析图表
        st.subheader("发票状态分析")
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 饼图：发票状态分布
        status_labels = ['已支付', '未支付', '逾期', '部分支付']
        status_counts = [
            summary['invoices']['paid'],
            summary['invoices']['unpaid'],
            summary['invoices']['overdue'],
            summary['invoices']['total'] - summary['invoices']['paid'] - summary['invoices']['unpaid'] - summary['invoices']['overdue']
        ]
        
        ax1.pie(status_counts, labels=status_labels, autopct='%1.1f%%', startangle=90)
        ax1.set_title('发票状态分布')
        
        # 柱状图：每月开票金额（最近6个月）
        months = []
        month_amounts = []
        
        for i in range(5, -1, -1):
            month_date = datetime.now() - timedelta(days=30*i)
            month_label = month_date.strftime('%Y-%m')
            months.append(month_label)
            # 这里使用模拟数据
            month_amounts.append(random.uniform(50000, 200000))
        
        ax2.bar(months, month_amounts)
        ax2.set_title('最近6个月开票金额')
        ax2.set_xlabel('月份')
        ax2.set_ylabel('金额 (元)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 调整布局
        plt.tight_layout()
        
        # 显示图表
        st.pyplot(fig)
    
    with tab2:
        # 显示交易统计卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("交易总数", summary['transactions']['total'])
        
        with col2:
            st.metric("成功交易", summary['transactions']['successful'])
        
        with col3:
            st.metric("失败交易", summary['transactions']['failed'])
        
        with col4:
            st.metric("处理中交易", summary['transactions']['total'] - summary['transactions']['successful'] - summary['transactions']['failed'])
        
        st.divider()
        
        # 交易搜索和筛选
        st.subheader("交易查询")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input("搜索关键词 (交易编号/描述)")
            status = st.selectbox("状态", ['全部', '成功', '失败', '处理中'])
            payment_method = st.selectbox("支付方式", ['全部', '支付宝', '微信支付', '银行转账', '信用卡'])
        
        with col2:
            start_date = st.date_input("开始日期", value=None, format="YYYY-MM-DD")
            end_date = st.date_input("结束日期", value=None, format="YYYY-MM-DD")
        
        min_amount, max_amount = st.columns(2)
        
        with min_amount:
            min_amount_val = st.number_input("最小金额", min_value=0.0, step=0.01, value=None)
        
        with max_amount:
            max_amount_val = st.number_input("最大金额", min_value=0.0, step=0.01, value=None)
        
        # 搜索按钮
        search_button = st.button("搜索")
        
        # 执行搜索
        if search_button or search_term or status != '全部' or payment_method != '全部' or start_date or end_date or \
           min_amount_val is not None or max_amount_val is not None:
            transactions_df = billing_manager.search_transactions(
                search_term=search_term,
                status=status,
                payment_method=payment_method,
                start_date=start_date,
                end_date=end_date,
                min_amount=min_amount_val,
                max_amount=max_amount_val
            )
        else:
            transactions_df = billing_manager.get_transactions()
        
        # 显示搜索结果
        if not transactions_df.empty:
            # 添加导出按钮
            csv = transactions_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="导出为CSV",
                data=csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # 显示表格
            st.dataframe(transactions_df[["transaction_id", "transaction_date", "amount", "payment_method", "status", "description"]], 
                        width='stretch', hide_index=True)
        else:
            st.info("没有找到符合条件的交易")
        
        # 交易分析图表
        st.subheader("交易分析")
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 饼图：支付方式分布
        methods = list(summary['payment_method_stats'].keys())
        method_counts = [summary['payment_method_stats'][m]['count'] for m in methods]
        
        ax1.pie(method_counts, labels=methods, autopct='%1.1f%%', startangle=90)
        ax1.set_title('支付方式分布')
        
        # 柱状图：支付方式金额对比
        method_amounts = [summary['payment_method_stats'][m]['amount'] for m in methods]
        
        ax2.bar(methods, method_amounts)
        ax2.set_title('各支付方式交易金额')
        ax2.set_xlabel('支付方式')
        ax2.set_ylabel('金额 (元)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 调整布局
        plt.tight_layout()
        
        # 显示图表
        st.pyplot(fig)