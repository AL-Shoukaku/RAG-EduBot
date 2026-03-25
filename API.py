# API.py
# 封装大模型客户端和RAG功能

from pathlib import Path
from typing import List, Dict, Union, Generator
from zai import ZhipuAiClient
# !!! 移除了 load_vector_db 的导入，因为我们直接在这里读取文件
from RAG import get_most_similar_text
# !!! 新增导入 json 和 faiss
import json
import faiss

class RAGChatAPI:
    """封装原有代码中的所有API和RAG功能"""
    
    def __init__(self):
        """初始化客户端（对应原代码中的初始化逻辑）"""
        # !!! 将原本单一的 vector_db 拆分为 texts 和 faiss_index 两个独立的状态
        self.texts = None         # 用于存储纯文本列表
        self.faiss_index = None   # 用于存储预编译的 Faiss 引擎
        
        try:
            path = Path("key.txt")
            if not path.exists():
                raise FileNotFoundError("未找到 key.txt 文件，请在同级目录下创建并填入 API Key。")
            
            key = path.read_text().strip()
            self.client = ZhipuAiClient(api_key=key)
            self.initialized = True
        except Exception as e:
            self.initialized = False
            self.init_error = str(e)
            
    def load_course_db(self, course_type: str):
        """根据选择的课程加载对应的知识库"""
        # !!! 修改加载逻辑：分别为 OS 和 CO 加载对应的文本和 Faiss 索引文件
        try:
            if course_type == "os":
                # 加载纯文本
                with open("texts_os.json", "r", encoding="utf-8") as f:
                    self.texts = json.load(f)
                # 加载 Faiss 二进制索引引擎
                self.faiss_index = faiss.read_index("vector_db_os.index")
                
            elif course_type == "co":
                # 加载纯文本
                with open("texts_co.json", "r", encoding="utf-8") as f:
                    self.texts = json.load(f)
                # 加载 Faiss 二进制索引引擎
                self.faiss_index = faiss.read_index("vector_db_co.index")
                
            else:
                raise ValueError("未知的课程类型")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"加载知识库失败：找不到对应的文件。请先运行 embedding.py 编译知识库！详细信息：{e}")
    
    def check_initialized(self):
        """检查是否初始化成功"""
        if not self.initialized:
            raise Exception(self.init_error)
    
    def retrieve_similar_text(self, query: str) -> Union[str, List[str]]:
        """执行RAG检索，传入动态加载的知识库"""
        # !!! 检查两个组件是否都已成功加载
        if not self.texts or not self.faiss_index:
            raise RuntimeError("知识库尚未加载，请先选择课程！")
        
        # !!! 将 faiss_index 和 texts 一起传递给 RAG.py 里的检索函数
        return get_most_similar_text(query, self.faiss_index, self.texts)
    
    def prepare_rag_result(self, similar_text: Union[str, List[str]]) -> dict:
        """准备RAG检索结果（完全保留原逻辑）"""
        if isinstance(similar_text, list):
            # 将文本列表拼接成一个大字符串
            combined_text = "\n".join([f"[{i+1}] {text}" for i, text in enumerate(similar_text)])
            # UI预览截取拼接后文本的前100个字符
            rag_msg = f"🔍 知识库检索到相关内容: {combined_text[:100]}..."
        else:
            # 如果未找到相似文本（返回的是字符串提示），直接赋值
            combined_text = similar_text
            # UI直接显示提示文字
            rag_msg = f"🔍 检索结果: {similar_text}"
        
        return {
            "combined_text": combined_text,
            "display_message": rag_msg
        }
    
    def build_enhanced_prompt(self, user_input: str, combined_text: str) -> str:
        """构建增强提示词（结构化指令优化版）"""
        enhanced_prompt = f"""你是一个严谨的高校计算机课程教学助手。请仔细阅读以下的<参考知识>，并基于它回答用户问题。

        <参考知识>
        {combined_text}
        </参考知识>

        【严格回答规则】
        1. 强制相关性检查：在回答前，请先仔细比对用户问题与<参考知识>的内容。
        2. 触发拒答的条件：
        - 如果<参考知识>显示为“知识库中没有与问题相关的内容”。
        - 或者你判断<参考知识>中的内容与用户问题几乎无关、无法支撑给出一个完整且正确的答案。
        满足以上任一条件时，你**绝对不能**动用你自己的公共知识库进行瞎编或扩充，必须直接输出标准的拒答话术：“**抱歉，目前的课程知识库中未检索到与您问题直接相关的内容。您可以尝试换个问法，或者查阅最新的课程课件。**”
        3. 标准作答要求：如果<参考知识>包含相关答案，请进行提炼和总结。解释专业概念时条理清晰，多用列表形式。
        4. 来源引用：在作答完毕后，必须在回答的末尾加上一段话：“*(参考来源：[此处填入参考知识中出现的【来源文件：xxx】名称])*”。

        用户问题：
        {user_input}"""
        
        return enhanced_prompt
    
    def stream_chat(self, messages: List[Dict], **kwargs) -> Generator:
        """流式聊天（完全保留原逻辑）"""
        return self.client.chat.completions.create(
            model="glm-4-flash",
            messages=messages,
            temperature=0.1,      
            top_p=0.7,            
            max_tokens=2000,      
            stream=True,
            timeout=30,
            **kwargs
        )