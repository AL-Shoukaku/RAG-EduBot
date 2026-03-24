# API.py
# 封装大模型客户端和RAG功能

from pathlib import Path
from typing import List, Dict, Union, Generator
from zai import ZhipuAiClient
from RAG import get_most_similar_text, load_vector_db

class RAGChatAPI:
    """封装原有代码中的所有API和RAG功能"""
    
    def __init__(self):
        """初始化客户端（对应原代码中的初始化逻辑）"""
        self.vector_db = None  # 动态加载的知识库
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
        if course_type == "os":
            self.vector_db = load_vector_db("vector_db_os.json")
        elif course_type == "co":
            self.vector_db = load_vector_db("vector_db_co.json")
        else:
            raise ValueError("未知的课程类型")
    
    def check_initialized(self):
        """检查是否初始化成功"""
        if not self.initialized:
            raise Exception(self.init_error)
    
    def retrieve_similar_text(self, query: str) -> Union[str, List[str]]:
        """执行RAG检索，传入动态加载的知识库"""
        if not self.vector_db:
            raise RuntimeError("知识库尚未加载，请先选择课程！")
        return get_most_similar_text(query, self.vector_db)
    
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

回答要求：
1. 若<参考知识>中包含相关信息，请严格基于知识作答，切勿捏造，并在回答末尾附上引用的知识库原文作为补充。
2. 若<参考知识>显示“知识库中没有与问题相关的内容”，请先明确告知用户“知识库中缺乏直接信息”，随后基于你的计算机科学公共知识库给出严谨的解答。
3. 解释专业概念时（如进程、缓存等），请保持条理清晰，多用列表形式。

用户问题：
{user_input}"""
        
        return enhanced_prompt
    
    def stream_chat(self, messages: List[Dict], **kwargs) -> Generator:
        """流式聊天（大模型参数优化版）"""
        return self.client.chat.completions.create(
            model="glm-4-flash",
            messages=messages,
            temperature=0.1,      # 【修改】：降温至 0.1。大幅度减少“幻觉”，让回答更稳定、更像标准答案
            top_p=0.7,            # 【新增】：控制核采样，进一步限制模型乱发散
            max_tokens=2000,      # 【修改】：降至 2000。答疑通常不需要 5000 字长篇大论，这能加快系统响应速度
            stream=True,
            timeout=30,
            **kwargs
        )
        