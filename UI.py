# UI.py
# 彻底修复课程选择+全屏纯色背景（修复底部黑边）+检索结果默认折叠版
import streamlit as st
from API import RAGChatAPI

# ================= 全局设置与样式 =================
st.set_page_config(
    page_title="Z.ai RAG 智能助教",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# 自定义 CSS - 全屏纯色背景+卡片单选框美化
def load_custom_css():
    st.markdown("""
    <style>
    /* ================= 核心背景修改 ================= */
    /* 1. 覆盖底层主视图容器，彻底替换默认黑/白背景 */
    [data-testid="stAppViewContainer"] {
        background-color: #0f3460 !important;
    }
    
    /* 2. 将顶部的 Streamlit Header（页眉）背景设为透明 */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* 3. 确保底层应用本体也是同色 */
    .stApp {
        background-color: #0f3460 !important;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }

    /* 4. 彻底解决底部固定区域（输入框周围）的背景色 */
    footer {
        background-color: transparent !important;
    }
    /* 强制底部悬浮容器为深蓝色 */
    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background-color: #0f3460 !important;
    }
    [data-testid="stBottomBlock"] {
        background-color: #0f3460 !important;
    }
    /* 消除底部可能存在的内容渐变遮罩 */
    .stApp > header + div > div:last-child {
        background-image: none !important;
        background-color: #0f3460 !important;
    }

    /* 内容层优先级，确保在背景之上 */
    .main > div {
        position: relative;
        z-index: 1;
    }

    /* 全局字体 */
    html, body, [class*="css"] {
        font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
        line-height: 1.6;
    }

    /* 标题样式 */
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

    /* 输入框 - 保持原有玻璃态设定，不受外部背景影响 */
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

    /* 警告提示框 */
    .stAlert {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }

    /* 底部自制声明文本 */
    .caption {
        color: rgba(0,255,255,0.7) !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# ================= 状态初始化 =================
if "api" not in st.session_state:
    try:
        st.session_state.api = RAGChatAPI()
        st.session_state.api.check_initialized()
    except Exception as e:
        st.error(f"初始化失败: {e}")
        st.stop()

if "course_selected" not in st.session_state:
    st.session_state.course_selected = False

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
                    在生成回答前，你必须在后台比对用户问题与<参考知识>。若出现以下任一情况：
                    1. 知识库显示“没有与问题相关的内容”。
                    2. 【无关拒答】：问题属于跨学科、日常生活或非本课程范围，参考知识无法对应。
                    3. 【超纲拒答】：参考知识虽然命中了部分关键词，但提供的信息“极度碎片化”或“不足以支撑给出一个准确且完整的解答”（如前沿技术探讨）。
                    -> 只要满足上述任一情况，请**立即停止作答**，绝不能使用你的公共知识库进行推测或编造。必须直接输出以下标准化拒答话术：
                    “**同学你好，抱歉，目前的课程知识库中未检索到足以准确解答该问题的相关内容。请检查提问是否属于本课程（{st.session_state.course_name}）范围，或尝试补充更多关键词后重新提问。**”

                    第二步：构建教学解答（若校验通过）
                    如果<参考知识>足以回答问题，请按照以下“助教教学规范”组织你的回答：
                    1. 绝对忠实：回答的核心观点、数据、公式、概念界定必须 100% 来源于<参考知识>。你可以用更容易理解的话去解释原文，但绝不能捏造原文不存在的事实。
                    2. 针对性结构（极其重要）：
                    - 【概念与事实题】：直接明了地给出答案，条理清晰。
                    - 【对比与归纳题】：强烈建议使用**对比列表或Markdown表格**，清晰列出不同方案的优缺点和区别。
                    - 【应用计算题】：严禁直接给出最终结果。必须**分步骤展示已知条件、所用原理以及推导/计算过程**。
                    - 【综合问答题】：提取不同知识块的信息，使用“首先、其次、综上所述”等逻辑连接词进行串联。
                    3. 教学语气：态度专业、客观、有启发性。合理排版，重点概念加粗。

                    第三步：强制标注来源
                    在解答的最末尾，另起一行，必须列出你本次回答所引用的知识来源（请准确提取参考知识中出现的【来源文件：xxx】，不要遗漏，也不要罗列问题中没用到的文件）：
                    格式：“*📚 参考资料：[文件A], [文件B]*”回答时请换为具体的文件来源。"""}
                    ]
                    st.session_state.display_history = [
                        {"role": "system",
                         "content": f"欢迎使用《{st.session_state.course_name}》智能助教！您可以开始提问了。"}
                    ]

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
            st.session_state.course_selected = False
            for key in ["conversation", "display_history"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.divider()

    chat_container = st.container(height=900, border=True)
    with chat_container:
        for msg in st.session_state.display_history:
            if msg["role"] == "system":
                with st.chat_message("system", avatar="⚙️"):
                    st.info(msg["content"])
            elif msg["role"] == "rag":
                with st.chat_message("system", avatar="🔍"):
                    with st.expander("📚 知识库检索结果", expanded=False):
                        # 纯文本渲染
                        st.text(msg["content"])
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
            similar_text = st.session_state.api.retrieve_similar_text(user_input)
            rag_result = st.session_state.api.prepare_rag_result(similar_text)
            rag_msg = rag_result["display_message"]
            combined_text = rag_result["combined_text"]

            st.session_state.display_history.append({"role": "rag", "content": rag_msg})
            with chat_container:
                with st.chat_message("system", avatar="🔍"):
                    # 修改点：将 expanded=True 修改为 expanded=False
                    with st.expander("📚 知识库检索结果", expanded=False):
                        # 纯文本渲染
                        st.text(rag_msg)

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

        except Exception as e:
            err = f"出错了：{e}"
            st.error(err)
            st.session_state.display_history.append({"role": "system", "content": err})

st.divider()
st.caption("© 2026 Z.ai RAG 智能助教 | 基于 Streamlit 构建")