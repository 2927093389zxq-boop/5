import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import time
import re

# 美化的消息显示函数
def show_success_message(message):
    """显示美化的成功消息"""
    st.success(message, icon="✅")

def show_error_message(message):
    """显示美化的错误消息"""
    st.error(message, icon="❌")

def show_warning_message(message):
    """显示美化的警告消息"""
    st.warning(message, icon="⚠️")

def show_info_message(message):
    """显示美化的信息消息"""
    st.info(message, icon="ℹ️")

# 美化的数据框显示函数
def create_beautiful_dataframe(df, title=None, height=400):
    """创建美观的数据框显示"""
    if title:
        st.markdown(f"### {title}")
    
    # 使用Streamlit的dataframe函数，设置一些美化参数
    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True,
        column_config=None
    )

# 美化的图表样式函数
def style_plot(fig, title=None, x_label=None, y_label=None):
    """美化matplotlib图表样式"""
    # 设置整体样式
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # 设置标题
    if title:
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
    
    # 获取所有子图
    ax_list = fig.get_axes()
    
    # 美化每个子图
    for ax in ax_list:
        # 设置标签
        if x_label and ax.get_xlabel() == '':
            ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
        if y_label and ax.get_ylabel() == '':
            ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
        
        # 设置刻度标签
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.tick_params(axis='both', which='minor', labelsize=8)
        
        # 设置网格线样式
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 设置图例
        if ax.get_legend():
            ax.legend(fontsize=10, framealpha=0.7)

# 格式化数字显示函数
def format_number(value, decimal_places=2):
    """格式化数字，添加千分位分隔符"""
    if isinstance(value, (int, float)):
        return f"{value:,.{decimal_places}f}"
    return value

# 格式化货币显示函数
def format_currency(value, currency="¥"):
    """格式化货币显示"""
    if isinstance(value, (int, float)):
        return f"{currency}{value:,.2f}"
    return value

# 加载状态指示器函数
def show_loading_indicator(message="加载中...", duration=1.5):
    """显示加载状态指示器"""
    with st.spinner(message):
        time.sleep(duration)

# 高级指标卡片函数
def create_metric_card(title, value, icon=None, color=None, border_radius=10, 
                     box_shadow=True, subtext=None, animate=False):
    """创建美观的指标卡片"""
    # 创建自定义HTML和CSS样式
    shadow_style = "box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);" if box_shadow else ""
    animation_style = "transition: all 0.3s ease;" if animate else ""
    
    card_style = f"""
    <style>
    .metric-card {{
        background-color: white;
        border-radius: {border_radius}px;
        padding: 20px;
        {shadow_style}
        {animation_style}
        border-left: 5px solid {color if color else '#2196F3'};
        margin-bottom: 16px;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }}
    .metric-title {{
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 8px;
        color: #666;
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: bold;
        color: {color if color else '#2196F3'};
        margin-bottom: 4px;
    }}
    .metric-icon {{
        font-size: 32px;
        margin-right: 12px;
        vertical-align: middle;
    }}
    .metric-subtext {{
        font-size: 12px;
        color: #999;
    }}
    </style>
    """
    
    # 显示卡片
    st.markdown(card_style, unsafe_allow_html=True)
    
    icon_html = f"<span class='metric-icon'>{icon}</span>" if icon else ""
    subtext_html = f"<div class='metric-subtext'>{subtext}</div>" if subtext else ""
    
    card_html = f"""
    <div class='metric-card'>
        <div class='metric-title'>{title}</div>
        <div class='metric-value'>{icon_html}{value}</div>
        {subtext_html}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# 美化的卡片显示函数
def create_card(title, content, icon=None, color=None):
    """创建美观的卡片显示"""
    # 创建自定义HTML和CSS样式
    card_style = f"""
    <style>
    .custom-card {{
        background-color: white;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 16px;
        border-left: 5px solid {color if color else '#2196F3'};
    }}
    .card-title {{
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
        color: #333;
    }}
    .card-content {{
        font-size: 24px;
        font-weight: bold;
        color: {color if color else '#2196F3'};
    }}
    .card-icon {{
        font-size: 32px;
        margin-right: 8px;
        vertical-align: middle;
    }}
    </style>
    """
    
    # 显示卡片
    st.markdown(card_style, unsafe_allow_html=True)
    
    icon_html = f"<span class='card-icon'>{icon}</span>" if icon else ""
    
    card_html = f"""
    <div class='custom-card'>
        <div class='card-title'>{title}</div>
        <div class='card-content'>{icon_html}{content}</div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# 美化的过滤器显示函数
def create_filter_section(title, filters):
    """创建美观的过滤器区域"""
    with st.expander(title, expanded=True):
        cols = st.columns(len(filters))
        results = {}
        
        for i, (filter_name, filter_config) in enumerate(filters.items()):
            with cols[i % len(cols)]:
                filter_type = filter_config.get('type', 'selectbox')
                label = filter_config.get('label', filter_name)
                options = filter_config.get('options', [])
                default = filter_config.get('default', options[0] if options else None)
                placeholder = filter_config.get('placeholder', '请选择')
                
                if filter_type == 'selectbox':
                    results[filter_name] = st.selectbox(label, options, key=filter_name)
                elif filter_type == 'multiselect':
                    results[filter_name] = st.multiselect(label, options, default=default, key=filter_name)
                elif filter_type == 'text_input':
                    results[filter_name] = st.text_input(label, placeholder=placeholder, key=filter_name)
                elif filter_type == 'slider':
                    min_val = filter_config.get('min', 0)
                    max_val = filter_config.get('max', 100)
                    step = filter_config.get('step', 1)
                    results[filter_name] = st.slider(label, min_val, max_val, default, step, key=filter_name)
        
        return results

# 美化的分页组件
def create_pagination(total_items, items_per_page=10, page_key="page"):
    """创建美观的分页组件"""
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    if total_pages <= 1:
        return 0
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        current_page = st.select_slider(
            "页码",
            options=list(range(1, total_pages + 1)),
            value=1,
            key=page_key
        )
    
    return current_page - 1

# 导出数据函数
def export_data(df, filename_prefix="data", formats=["csv", "excel"]):
    """提供数据导出功能"""
    if df.empty:
        show_warning_message("没有数据可供导出")
        return
    
    col_buttons = st.columns(len(formats))
    
    for i, format_type in enumerate(formats):
        with col_buttons[i]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type == "csv":
                csv_data = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📄 导出CSV",
                    data=csv_data,
                    file_name=f"{filename_prefix}_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            elif format_type == "excel":
                excel_data = df.to_excel(index=False, engine='xlsxwriter')
                st.download_button(
                    label="📊 导出Excel",
                    data=excel_data,
                    file_name=f"{filename_prefix}_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

# 自定义的成功/失败指示器函数
def show_status_indicator(success=True, message=None):
    """显示自定义的成功/失败指示器"""
    if success:
        show_success_message(message or "操作成功完成")
    else:
        show_error_message(message or "操作执行失败")

# 确认对话框函数
def show_confirmation_dialog(title, message):
    """显示确认对话框"""
    st.warning(message)
    return st.button("确认操作", type="primary")

# 获取当前时间戳函数
def get_timestamp(format="%Y-%m-%d %H:%M:%S"):
    """获取当前时间戳"""
    return datetime.now().strftime(format)

# 验证输入函数
def validate_input(value, input_type="text", min_length=None, max_length=None, regex=None):
    """验证用户输入"""
    if value is None or value == "":
        return False, "输入不能为空"
    
    if min_length is not None and len(str(value)) < min_length:
        return False, f"输入长度不能小于{min_length}个字符"
    
    if max_length is not None and len(str(value)) > max_length:
        return False, f"输入长度不能大于{max_length}个字符"
    
    if regex and not re.match(regex, str(value)):
        return False, "输入格式不正确"
    
    if input_type == "number" and not str(value).isdigit():
        return False, "请输入有效的数字"
    
    return True, ""

# 美化的表单组件
def create_beautiful_form(title, fields, submit_label="提交"):
    """创建美观的表单组件"""
    with st.form(key=title):
        st.markdown(f"### {title}")
        
        form_data = {}
        
        for field_name, field_config in fields.items():
            field_type = field_config.get('type', 'text')
            label = field_config.get('label', field_name)
            placeholder = field_config.get('placeholder', '')
            default = field_config.get('default', '')
            help_text = field_config.get('help', '')
            
            if field_type == 'text':
                form_data[field_name] = st.text_input(label, default, placeholder=placeholder, help=help_text)
            elif field_type == 'number':
                min_value = field_config.get('min', 0)
                max_value = field_config.get('max', 1000000)
                step = field_config.get('step', 1)
                form_data[field_name] = st.number_input(label, min_value, max_value, default, step, help=help_text)
            elif field_type == 'select':
                options = field_config.get('options', [])
                form_data[field_name] = st.selectbox(label, options, help=help_text)
            elif field_type == 'date':
                form_data[field_name] = st.date_input(label, help=help_text)
            elif field_type == 'textarea':
                height = field_config.get('height', 100)
                form_data[field_name] = st.text_area(label, default, height=height, help=help_text)
        
        submit = st.form_submit_button(submit_label, type="primary", use_container_width=True)
        
        if submit:
            # 验证表单数据
            valid = True
            errors = {}
            
            for field_name, field_config in fields.items():
                required = field_config.get('required', False)
                validation = field_config.get('validation', {})
                
                if required and (field_name not in form_data or not form_data[field_name]):
                    valid = False
                    errors[field_name] = "此字段为必填项"
                elif field_name in form_data and form_data[field_name]:
                    valid_input, error_msg = validate_input(
                        form_data[field_name],
                        field_config.get('type', 'text'),
                        validation.get('min_length'),
                        validation.get('max_length'),
                        validation.get('regex')
                    )
                    if not valid_input:
                        valid = False
                        errors[field_name] = error_msg
            
            if valid:
                return True, form_data
            else:
                show_error_message("表单验证失败，请检查输入")
                for field_name, error in errors.items():
                    st.markdown(f"- **{field_name}**: {error}")
                return False, form_data
        
        return False, form_data