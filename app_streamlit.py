import streamlit as st
import yt_script_v3 as your_script
import threading
import sys

# 从命令行参数获取 YouTube URL
youtube_url = sys.argv[1] if len(sys.argv) > 1 else "默认的 YouTube URL"

# Streamlit 页面设置
st.title('YouTube 直播流处理')

# 全局变量来存储结果
results = []

# 将您的脚本作为一个独立的函数运行
def run_your_script():
    global results
    results = your_script.main(youtube_url, 5, 6000)

# 在 Streamlit 应用中添加一个按钮来启动脚本
if st.button('开始处理'):
    thread = threading.Thread(target=run_your_script)
    thread.start()
    st.text('脚本正在后台运行')

# 显示结果
if st.button('显示结果'):
    st.write(results)
