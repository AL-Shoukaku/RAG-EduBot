# RAG.py
from zai import ZhipuAiClient
import numpy as np
from pathlib import Path
import faiss
# !!! 仅保留给下方本地测试代码使用的 json 导入
import json 

path = Path("key.txt")
key = path.read_text().strip()
# 初始化客户端（可以放在函数外面，避免重复初始化）
client = ZhipuAiClient(api_key=key)

# !!! 删除了原来的 load_vector_db 函数，因为加载逻辑已移交到 API.py 中统一管理

# !!! 修改函数入参：接收 API.py 传来的预编译 Faiss 引擎 (faiss_index) 和 纯文本列表 (texts)
def get_most_similar_text(question: str, faiss_index, texts: list):
    """
    输入用户问题，返回向量库中最相似的文本
    
    Args:
        question: 用户问题字符串
        faiss_index: 预先加载好的 Faiss 二进制索引引擎
        texts: 预先加载好的对应纯文本列表
        
    Returns:
        最相似的文本列表，或未找到时的提示字符串
    """
    # 1. 将问题转换为向量 (保持不变)
    response = client.embeddings.create(
        model="embedding-3",
        input=[question],
        dimensions=512
    )
    question_vector = response.data[0].embedding
    
    threshold = 0.65    #相似度超过这个值才认为是相关的文本
    candidates = []
    
    # !!! 删除了原先提取向量、构建 numpy 矩阵、归一化、以及 index.add() 的所有建库逻辑
    # !!! 只有当知识库确实有内容时，才进行查询
    if texts and faiss_index is not None:
        
        # ! 对问题向量进行归一化 (保持不变)
        query_vector = np.array([question_vector]).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # ! 搜索最相似的 k 个
        k = min(5, len(texts))  # !!! 使用 len(texts) 获取知识库总数
        # !!! 直接调用预编译好的 faiss_index 进行极速检索
        similarities, indices = faiss_index.search(query_vector, k)
        
        # ! 收集满足阈值的结果
        for i in range(k):
            if similarities[0][i] >= threshold:
                # !!! 直接使用返回的下标 indices[0][i] 去 texts 列表中精准定位原始文本
                candidates.append((similarities[0][i], texts[indices[0][i]]))
    
    # ! 如果没有找到任何达到阈值的相似文本，则按要求返回指定字符串 (保持不变)
    if not candidates:
        return "知识库中没有与问题相关的内容"
        
    # ! 根据相似度从大到小对候选列表进行排序 (保持不变)
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # 截取前 5 个最相似的文本 (保持不变)
    best_texts = [candidate[1] for candidate in candidates[:5]]
    
    # 3. 返回最相似的文本列表
    return best_texts

# 使用示例
if __name__ == "__main__":
    # !!! 更新了测试用例，适配双文件分离加载的逻辑
    try:
        # 手动加载操作系统的纯文本和 Faiss 引擎进行测试
        with open("texts_os.json", "r", encoding="utf-8") as f:
            test_texts = json.load(f)
        test_index = faiss.read_index("vector_db_os.index")
        
        questions = "请问什么多道程序设计？"
        
        # !!! 传入测试的 index 和 texts
        result = get_most_similar_text(questions, test_index, test_texts)
        print(f"问题: {questions}")
        
        if isinstance(result, list):
            print("最相似文本:")
            for i, text in enumerate(result, 1):
                print(f"[{i}] {text}")
        else:
            print(f"返回结果: {result}")
            
        print("-" * 40)
    except FileNotFoundError:
        print("未找到测试用的知识库文件，请确保同级目录下存在 texts_os.json 和 vector_db_os.index")