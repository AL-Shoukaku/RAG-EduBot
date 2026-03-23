# RAG.py
from zai import ZhipuAiClient
import numpy as np
import json
from pathlib import Path
# ! 导入 faiss
import faiss

path = Path("key.txt")
key = path.read_text().strip()
# 初始化客户端（可以放在函数外面，避免重复初始化）
client = ZhipuAiClient(api_key=key)

def load_vector_db(file_path: str):
    """根据提供的路径动态加载向量库"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ! 移除原来的 cosine_similarity 函数，改用 faiss 实现

# ! 将 vector_db 作为参数传入，而不是使用全局变量
def get_most_similar_text(question: str, vector_db: list):
    """
    输入用户问题，返回向量库中最相似的文本
    
    Args:
        question: 用户问题字符串
        vector_db: 已加载的向量知识库列表
        
    Returns:
        最相似的文本列表，或未找到时的提示字符串
    """
    # 1. 将问题转换为向量
    response = client.embeddings.create(
        model="embedding-3",
        input=[question],
        dimensions=512
    )
    question_vector = response.data[0].embedding
    
    # ! 使用 faiss 进行相似度计算
    threshold = 0.65    #相似度超过这个值才认为是相关的文本
    candidates = []
    
    # ! 如果向量库不为空，使用 faiss 进行批量相似度计算
    if vector_db:
        # ! 提取所有向量并转换为 float32 数组（faiss 要求）
        vectors = np.array([item['vector'] for item in vector_db]).astype('float32')
        
        # ! 构建 faiss 索引（使用内积，因为余弦相似度 = 内积 / (|a|*|b|)）
        # ! 需要先归一化向量，这样内积就等于余弦相似度
        faiss.normalize_L2(vectors)  # 对库向量进行归一化
        
        # ! 创建索引（使用内积，因为归一化后内积=余弦相似度）
        index = faiss.IndexFlatIP(vectors.shape[1])  # IP = Inner Product
        index.add(vectors)
        
        # ! 对问题向量进行归一化
        query_vector = np.array([question_vector]).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # ! 搜索最相似的 k 个（先搜索全部，再过滤阈值）
        k = min(5, len(vector_db))  # 最多搜索5个
        similarities, indices = index.search(query_vector, k)
        
        # ! 收集满足阈值的结果
        for i in range(k):
            if similarities[0][i] >= threshold:
                candidates.append((similarities[0][i], vector_db[indices[0][i]]['text']))
    
    # ! 如果没有找到任何达到阈值的相似文本，则按要求返回指定字符串
    if not candidates:
        return "知识库中没有与问题相关的内容"
        
    # ! 根据相似度从大到小对候选列表进行排序
    # ! 注意：faiss 返回的结果已经按相似度从大到小排序，但为了保持与原代码一致，仍然进行排序
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # 截取前 5 个最相似的文本
    best_texts = [candidate[1] for candidate in candidates[:5]]
    
    # 3. 返回最相似的文本列表
    return best_texts

# 使用示例
if __name__ == "__main__":
    # 测试时可以手动加载对应的库
    try:
        test_db = load_vector_db("vector_db_os.json")
        questions = "请问什么是进程？"
        
        result = get_most_similar_text(questions, test_db)
        print(f"问题: {questions}")
        
        if isinstance(result, list):
            print("最相似文本:")
            for i, text in enumerate(result, 1):
                print(f"[{i}] {text}")
        else:
            print(f"返回结果: {result}")
            
        print("-" * 40)
    except FileNotFoundError:
        print("未找到测试用的 json 文件，请确保同级目录下存在 vector_db_os.json")