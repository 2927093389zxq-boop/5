import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 设置matplotlib中文字体支持
def setup_chinese_fonts():
    """设置matplotlib中文字体支持"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 创建美化的数据卡片
def create_metric_card(title, value, subtitle=None, icon=None, color=None):
    """
    创建美化的数据指标卡片
    
    参数:
    - title: 卡片标题
    - value: 卡片主要值
    - subtitle: 卡片副标题
    - icon: 可选图标
    - color: 可选颜色
    
    返回:
    - Streamlit容器
    """
    card_container = st.container()
    with card_container:
        # 添加图标
        if icon:
            st.markdown(f"**{icon} {title}**")
        else:
            st.markdown(f"**{title}**")
        
        # 添加主要值
        if color:
            st.markdown(f"<span style='font-size: 1.5em; font-weight: bold; color: {color}'>{value}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='font-size: 1.5em; font-weight: bold'>{value}</span>", unsafe_allow_html=True)
        
        # 添加副标题
        if subtitle:
            st.caption(subtitle)
    
    return card_container

# 创建美化的数据框
def create_beautiful_dataframe(df, title=None, columns=None, height=400, hide_index=True):
    """
    创建美化的数据表格展示
    
    参数:
    - df: pandas DataFrame
    - title: 可选标题
    - columns: 要显示的列
    - height: 表格高度
    - hide_index: 是否隐藏索引
    
    返回:
    - Streamlit表格对象
    """
    if title:
        st.subheader(title)
    
    # 选择列
    if columns:
        # 确保所有指定的列都存在于DataFrame中
        available_columns = [col for col in columns if col in df.columns]
        df = df[available_columns]
    
    # 创建美化的数据框
    return st.dataframe(
        df,
        use_container_width=True,
        hide_index=hide_index,
        height=height,
        # 添加样式
        column_config={}
    )

# 创建美化的表单
def create_beautiful_form(title, form_key=None, width=None):
    """
    创建美化的表单容器
    
    参数:
    - title: 表单标题
    - form_key: 表单唯一标识
    - width: 表单宽度
    
    返回:
    - Streamlit表单对象
    """
    if width:
        col = st.columns(width)[0]
        with col:
            st.subheader(title)
            return st.form(form_key)
    else:
        st.subheader(title)
        return st.form(form_key)

# 创建美化的导航菜单
def create_beautiful_navigation(options, default_index=0, label="导航菜单"):
    """
    创建美化的导航菜单
    
    参数:
    - options: 选项列表
    - default_index: 默认选中的索引
    - label: 菜单标签
    
    返回:
    - 选中的选项
    """
    # 使用expander创建折叠式导航
    with st.expander(label, expanded=True):
        return st.radio(
            "",
            options,
            index=default_index,
            horizontal=False
        )

# 创建美化的多标签页
def create_beautiful_tabs(titles, selected_title=None):
    """
    创建美化的多标签页
    
    参数:
    - titles: 标签页标题列表
    - selected_title: 默认选中的标题
    
    返回:
    - 标签页对象
    """
    # 如果指定了选中的标题，找到对应的索引
    index = 0
    if selected_title and selected_title in titles:
        index = titles.index(selected_title)
    
    # 创建标签页
    return st.tabs(titles)

# 设置应用主题样式
def set_page_theme(theme_name=None):
    """
    设置应用主题样式
    
    参数:
    - theme_name: 主题名称，可选值: 'light', 'dark', 'blue', 'green', None
    """
    # 应用自定义CSS
    custom_css = """
    <style>
    /* 全局样式 */
    body {
        font-family: 'Arial', 'Microsoft YaHei', sans-serif;
    }
    
    /* 按钮样式 */
    .stButton > button {
        border-radius: 4px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 4px;
    }
    
    /* 卡片样式 */
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* 数据框样式 */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # 根据主题名称添加特定样式
    if theme_name == 'dark':
        dark_css = """
        <style>
        .stMetric {
            background-color: #2c3e50;
            color: white;
        }
        </style>
        """
        st.markdown(dark_css, unsafe_allow_html=True)
    elif theme_name == 'blue':
        blue_css = """
        <style>
        .stMetric {
            background-color: #e3f2fd;
        }
        .stButton > button {
            background-color: #2196f3;
            color: white;
        }
        </style>
        """
        st.markdown(blue_css, unsafe_allow_html=True)
    elif theme_name == 'green':
        green_css = """
        <style>
        .stMetric {
            background-color: #e8f5e9;
        }
        .stButton > button {
            background-color: #4caf50;
            color: white;
        }
        </style>
        """
        st.markdown(green_css, unsafe_allow_html=True)

# 创建加载动画
def show_loading_spinner(message="正在处理..."):
    """
    显示加载动画
    
    参数:
    - message: 加载消息
    
    返回:
    - Streamlit spinner对象
    """
    return st.spinner(message)

# 创建成功提示
def show_success_message(message, icon="✅"):
    """
    显示成功提示
    
    参数:
    - message: 提示消息
    - icon: 图标
    """
    st.success(f"{icon} {message}")

# 创建错误提示
def show_error_message(message, icon="❌"):
    """
    显示错误提示
    
    参数:
    - message: 提示消息
    - icon: 图标
    """
    st.error(f"{icon} {message}")

# 创建信息提示
def show_info_message(message, icon="ℹ️"):
    """
    显示信息提示
    
    参数:
    - message: 提示消息
    - icon: 图标
    """
    st.info(f"{icon} {message}")

# 创建警告提示
def show_warning_message(message, icon="⚠️"):
    """
    显示警告提示
    
    参数:
    - message: 提示消息
    - icon: 图标
    """
    st.warning(f"{icon} {message}")

# 美化图表样式
def style_plot(fig, title=None, x_label=None, y_label=None, figsize=(10, 6)):
    """
    美化matplotlib图表样式
    
    参数:
    - fig: matplotlib图表对象
    - title: 图表标题
    - x_label: X轴标签
    - y_label: Y轴标签
    - figsize: 图表尺寸
    
    返回:
    - 美化后的图表对象
    """
    # 设置图表尺寸
    fig.set_size_inches(*figsize)
    
    # 获取所有子图
    axs = fig.get_axes()
    
    # 设置每个子图的样式
    for ax in axs:
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 设置轴标签
        if x_label and ax == axs[-1]:  # 只为底部子图设置X轴标签
            ax.set_xlabel(x_label, fontsize=12)
        if y_label:
            ax.set_ylabel(y_label, fontsize=12)
        
        # 美化刻度标签
        ax.tick_params(axis='both', labelsize=10)
    
    # 设置图表标题
    if title:
        fig.suptitle(title, fontsize=16, y=0.98)
    
    # 调整布局
    plt.tight_layout()
    
    return fig