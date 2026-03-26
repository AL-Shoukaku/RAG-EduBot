import webview
import subprocess
import time
import socket

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_app():
    # 1. 以后台无界面模式(headless)启动 Streamlit
    # 注意：这里假设你的主程序叫 UI.py
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "UI.py", "--server.headless", "true"]
    )

    # 2. 等待 Streamlit 服务器启动 (检测 8501 端口)
    port = 8501
    while not is_port_in_use(port):
        time.sleep(0.5)

    # 3. 创建并打开一个独立的桌面窗口
    window = webview.create_window(
        title='Z.ai RAG 智能助教', 
        url=f'http://localhost:{port}',
        width=1200, 
        height=800,
        confirm_close=True # 关闭时可以弹出确认框，不需要可改为 False
    )

    # 启动窗口，代码会在这里阻塞，直到用户关闭窗口
    webview.start()

    # 4. 当用户点击右上角 X 关闭窗口后，往下执行，杀掉 Streamlit 进程
    streamlit_process.terminate()

if __name__ == '__main__':
    start_app()