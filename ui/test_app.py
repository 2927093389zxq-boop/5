import streamlit as st

# 简单的测试应用
st.title("测试应用")
st.write("这是一个简单的Streamlit测试应用")

# 添加一些交互元素
name = st.text_input("请输入您的名字")
if name:
    st.write(f"你好，{name}！")

# 添加一个按钮
if st.button("点击我"):
    st.success("按钮被点击了！")