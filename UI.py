# UI.py
# 彻底修复课程选择+全屏纯色背景+检索折叠+本地历史记录+知识分页与单条删除版
import streamlit as st
import json
import os
import time
from API import RAGChatAPI

# ================= 历史记录持久化配置 =================
HISTORY_FILE = "chat_history.json"

def load_history():
    """从本地 JSON 文件加载历史对话记录"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"读取历史记录失败: {e}")
            return {}
    return {}

def save_history(history_data):
    """将历史对话记录保存到本地 JSON 文件"""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"保存历史记录失败: {e}")

# ================= 全局设置与样式 =================
st.set_page_config(
    page_title="Z.ai RAG 智能助教",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="auto"
)

# 自定义 CSS 
def load_custom_css():
    st.markdown("""
    <style>
    /* ================= 核心背景修改 ================= */
    [data-testid="stAppViewContainer"] {
        background-color: #0f3460 !important;
    }
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    .stApp {
        background-color: #0f3460 !important;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    footer {
        background-color: transparent !important;
    }
    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background-color: #0f3460 !important;
    }
    [data-testid="stBottomBlock"] {
        background-color: #0f3460 !important;
    }
    .stApp > header + div > div:last-child {
        background-image: none !important;
        background-color: #0f3460 !important;
    }

    /* 侧边栏背景颜色同步深色 */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 30, 60, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    .main > div {
        position: relative;
        z-index: 1;
    }

    html, body, [class*="css"] {
        font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
        line-height: 1.6;
    }

    h1 {
        color: white !important;
        font-weight: 700;
        text-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    h2, h3, h4 {
        color: rgba(255,255,255,1) !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }

    /* ================= 单选框卡片样式 ================= */
    div[role="radiogroup"] {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        width: 100%;
        margin: 1rem 0;
    }
    div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.15);
        border-radius: 20px;
        padding: 25px;
        margin: 0;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        cursor: pointer;
        width: 100%;
    }
    div[role="radiogroup"] > label:hover {
        transform: translateY(-5px) scale(1.02);
        background: rgba(255,255,255,0.25);
        box-shadow: 0 12px 32px rgba(0,0,0,0.15);
    }
    div[role="radiogroup"] > label[data-checked="true"] {
        border: 2px solid rgba(255,255,255,0.6);
        background: rgba(255,255,255,0.3);
    }
    div[role="radiogroup"] > label:nth-child(1)::after {
        content: "涵盖进程管理、内存管理、文件系统等核心知识点";
        display: block;
        margin-top: 10px;
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
        font-weight: normal;
    }
    div[role="radiogroup"] > label:nth-child(2)::after {
        content: "涵盖CPU、存储器、总线、指令系统等核心知识点";
        display: block;
        margin-top: 10px;
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
        font-weight: normal;
    }

    /* 按钮美化 - 玻璃态 */
    .stButton>button {
        border-radius: 12px;
        height: 3em;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.2);
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        color: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        background: rgba(255,255,255,0.25);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .stButton>button[type="primary"] {
        background: linear-gradient(135deg, rgba(102,126,234,0.8), rgba(118,75,162,0.8));
        border: none;
    }

    /* 聊天气泡 - 玻璃态 */
    .stChatMessage {
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 10px;
        backdrop-filter: blur(10px);
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* 聊天容器 */
    [data-testid="stVerticalBlock"] > [style*="height: 900px"] {
        border-radius: 20px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255,255,255,0.8);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    /* 输入框 */
    .stChatInput>div>div>input {
        border-radius: 60px;
        border: 1px solid rgba(255,255,255,0.3);
        padding: 0px 10px;
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        color: white !important;
    }
    .stChatInput>div>div>input::placeholder {
        color: rgba(255,255,255,0.7) !important;
    }

    /* 分割线 */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(255,255,255,1), transparent);
        margin: 25px 0;
    }

    /* 全局文本颜色强制调白 */
    p, div, span, label {
        color: rgba(255,255,255,0.95) !important;
    }

    .stAlert {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }

    .caption {
        color: rgba(0,255,255,0.7) !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# ================= RAG 检索结果分页渲染组件 =================
def render_rag_result(content, session_id, msg_idx):
    """渲染支持分页的RAG结果"""
    # 如果传来的是一个列表（多条知识）并且列表不为空
    if isinstance(content, list) and len(content) > 0:
        page_key = f"rag_page_{session_id}_{msg_idx}"
        # 初始化这一条检索记录的当前页码
        if page_key not in st.session_state:
            st.session_state[page_key] = 0
            
        col1, col2, col3 = st.columns([1, 3, 1])
        
        # 回调函数控制翻页
        def update_page(k, delta, m):
            st.session_state[k] = max(0, min(m, st.session_state[k] + delta))

        with col1:
            st.button("◀ 上一个", key=f"prev_{page_key}", 
                      on_click=update_page, args=(page_key, -1, len(content)-1), 
                      disabled=(st.session_state[page_key] == 0), 
                      use_container_width=True)
        with col2:
            st.markdown(f"<div style='text-align: center; font-weight: bold; line-height: 2.5em;'>匹配知识片段 {st.session_state[page_key] + 1} / {len(content)}</div>", unsafe_allow_html=True)
        with col3:
            st.button("下一个 ▶", key=f"next_{page_key}", 
                      on_click=update_page, args=(page_key, 1, len(content)-1), 
                      disabled=(st.session_state[page_key] == len(content)-1), 
                      use_container_width=True)
        
        st.divider()
        st.text(content[st.session_state[page_key]])
    else:
        # 如果由于兼容旧版历史数据传来的是单字符串，直接显示
        st.text(content)

# ================= 状态初始化 =================
if "api" not in st.session_state:
    try:
        st.session_state.api = RAGChatAPI()
        st.session_state.api.check_initialized()
    except Exception as e:
        st.error(f"初始化失败: {e}")
        st.stop()

if "all_sessions" not in st.session_state:
    st.session_state.all_sessions = load_history()

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "course_selected" not in st.session_state:
    st.session_state.course_selected = False


# ================= 左侧历史记录侧边栏 =================
with st.sidebar:
    st.title("💬 历史对话")
    
    if st.button("➕ 新建会话", use_container_width=True, type="primary"):
        st.session_state.current_session_id = None
        st.session_state.course_selected = False
        if "conversation" in st.session_state:
            del st.session_state["conversation"]
        if "display_history" in st.session_state:
            del st.session_state["display_history"]
        st.rerun()
        
    st.divider()
    
    # 渲染历史会话列表
    for session_id, session_data in reversed(list(st.session_state.all_sessions.items())):
        col_btn, col_del = st.columns([5, 1])
        with col_btn:
            button_label = f"📝 {session_data.get('title', '未命名对话')}"
            if st.button(button_label, key=f"btn_{session_id}", use_container_width=True):
                with st.spinner("正在恢复历史会话..."):
                    st.session_state.current_session_id = session_id
                    st.session_state.course_selected = True
                    st.session_state.course_type = session_data["course_type"]
                    st.session_state.course_name = session_data["course_name"]
                    st.session_state.conversation = session_data["conversation"]
                    st.session_state.display_history = session_data["display_history"]
                    st.session_state.api.load_course_db(st.session_state.course_type)
                st.rerun()
        
        with col_del:
            # 单项删除按钮
            if st.button("🗑️", key=f"del_{session_id}", help="删除该对话", use_container_width=True):
                del st.session_state.all_sessions[session_id]
                save_history(st.session_state.all_sessions)
                # 如果删除的刚好是当前正在浏览的会话，就重置回主页
                if st.session_state.current_session_id == session_id:
                    st.session_state.current_session_id = None
                    st.session_state.course_selected = False
                    if "conversation" in st.session_state:
                        del st.session_state["conversation"]
                    if "display_history" in st.session_state:
                        del st.session_state["display_history"]
                st.rerun()

    if st.session_state.all_sessions:
        st.divider()
        if st.button("🚨 清空所有历史", use_container_width=True):
            st.session_state.all_sessions = {}
            save_history({})
            st.session_state.current_session_id = None
            st.session_state.course_selected = False
            st.rerun()


# ================= 1. 课程选择界面 =================
if not st.session_state.course_selected:
    st.title("🎓 Z.ai RAG 智能助教系统")
    st.divider()
    st.subheader("请选择您想要咨询的课程")

    course_choice = st.radio(
        "选择课程科目",
        ("操作系统 (OS)", "计算机组成原理 (CO)"),
        label_visibility="collapsed"
    )

    col_empty, col_button, col_empty2 = st.columns([3, 2, 3])
    with col_button:
        if st.button("🚀 进入助教系统", type="primary", use_container_width=True):
            if "操作系统" in course_choice:
                st.session_state.course_type = "os"
                st.session_state.course_name = "操作系统"
            else:
                st.session_state.course_type = "co"
                st.session_state.course_name = "计算机组成原理"

            try:
                with st.spinner("正在加载课程知识库..."):
                    st.session_state.api.load_course_db(st.session_state.course_type)

                    st.session_state.conversation = [
                        {"role": "system",
                        "content": f"""你是一名AI{st.session_state.course_name}课程助教，负责解答学生关于{st.session_state.course_name}的相关问题，请确保回答的准确性。

                    【核心处理流程与强制规则】
                    第一步：相关性与充足性校验（严格把关）
                    ...
                    第二步：构建教学解答
                    ...
                    第三步：强制标注来源
                    ..."""}
                    ]
                    st.session_state.display_history = [
                        {"role": "system",
                         "content": f"欢迎使用《{st.session_state.course_name}》智能助教！您可以开始提问了。"}
                    ]

                    st.session_state.current_session_id = str(int(time.time()))
                    st.session_state.course_selected = True
                    st.rerun()

            except Exception as e:
                st.error(f"加载课程知识库失败: {e}")

# ================= 2. 对话聊天界面 =================
else:
    col_title, col_btn = st.columns([8, 2])
    with col_title:
        st.title(f"📚 {st.session_state.course_name} 智能助教")
    with col_btn:
        if st.button("🔄 切换课程", use_container_width=True):
            st.session_state.current_session_id = None
            st.session_state.course_selected = False
            for key in ["conversation", "display_history"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.divider()

    chat_container = st.container(height=900, border=True)
    with chat_container:
        # 枚举迭代历史消息，这样能拿到每条消息对应的独一无二的 index，用于分页器的状态绑定
        for i, msg in enumerate(st.session_state.display_history):
            if msg["role"] == "system":
                with st.chat_message("system", avatar="⚙️"):
                    st.info(msg["content"])
            elif msg["role"] == "rag":
                with st.chat_message("system", avatar="🔍"):
                    with st.expander("📚 知识库检索结果", expanded=False):
                        # 使用新增的分页组件替代直接渲染
                        render_rag_result(msg["content"], st.session_state.current_session_id, i)
            elif msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            elif msg["role"] == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])

    user_input = st.chat_input(f"请输入{st.session_state.course_name}相关问题...")

    if user_input:
        st.session_state.display_history.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)

        try:
            # 核心修改点：这里拿到的是一个由多个字符串片段组成的 列表 similar_text
            similar_text = st.session_state.api.retrieve_similar_text(user_input)
            rag_result = st.session_state.api.prepare_rag_result(similar_text)
            combined_text = rag_result["combined_text"]

            # 我们不再将拼接好的单条字符串存入历史，而是直接把列表存入！这样渲染时可以分页处理
            st.session_state.display_history.append({"role": "rag", "content": similar_text})
            current_idx = len(st.session_state.display_history) - 1
            
            with chat_container:
                with st.chat_message("system", avatar="🔍"):
                    with st.expander("📚 知识库检索结果", expanded=False):
                        render_rag_result(similar_text, st.session_state.current_session_id, current_idx)

            enhanced_prompt = st.session_state.api.build_enhanced_prompt(user_input, combined_text)
            st.session_state.conversation.append({"role": "user", "content": enhanced_prompt})

            with chat_container:
                with st.chat_message("assistant", avatar="🤖"):
                    response = st.session_state.api.stream_chat(messages=st.session_state.conversation)

                    def stream_generator():
                        for chunk in response:
                            if chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content

                    full_response = st.write_stream(stream_generator())

            st.session_state.conversation.append({"role": "assistant", "content": full_response})
            st.session_state.display_history.append({"role": "assistant", "content": full_response})

            # 更新本地历史文件
            session_id = st.session_state.current_session_id
            if session_id not in st.session_state.all_sessions:
                title_text = user_input[:12] + "..." if len(user_input) > 12 else user_input
            else:
                title_text = st.session_state.all_sessions[session_id].get("title", "未命名对话")
            
            st.session_state.all_sessions[session_id] = {
                "title": title_text,
                "course_type": st.session_state.course_type,
                "course_name": st.session_state.course_name,
                "conversation": st.session_state.conversation,
                "display_history": st.session_state.display_history
            }
            save_history(st.session_state.all_sessions)

        except Exception as e:
            err = f"出错了：{e}"
            st.error(err)
            st.session_state.display_history.append({"role": "system", "content": err})

st.divider()
st.caption("© 2026 Z.ai RAG 智能助教 | 基于 Streamlit 构建")