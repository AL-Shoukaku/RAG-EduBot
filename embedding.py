from zai import ZhipuAiClient
import json
# !!! 新增导入 numpy 和 faiss 用于处理向量运算和二进制索引
import numpy as np
import faiss
# !!! 新增导入 os 用于处理文件路径和提取文件名
import os 
# ! 导入 load_file.py 中的加载和分块函数
from load_file import load_and_split_docs_from_folder

from pathlib import Path
path = Path("key.txt")
key = path.read_text().strip()

# 1. 初始化客户端
client = ZhipuAiClient(api_key=key)

# !!! 定义需要处理的两门课程：对应的知识文件夹和生成文件的后缀名
courses = [
    {"folder": "knowledge_os", "suffix": "os"},
    {"folder": "knowledge_co", "suffix": "co"}
]

# !!! 循环处理每一门课程
for course in courses:
    folder_name = course["folder"]
    suffix = course["suffix"]
    
    print(f"\n{'='*20} 开始处理课程知识库: {folder_name} {'='*20}")

    # 2. 加载知识库并处理文本
    # ! 调用 load_file.py 中的函数读取文件夹下的文件并分块
    chunks = load_and_split_docs_from_folder(folder_name)
    
    # !!! 核心逻辑修改：为每一个文本块手动注入来源信息
    # !!! 这样即便文件被切分成了很多块，大模型依然能知道每一块的具体出处
    texts = []
    for chunk in chunks:
        # 从元数据中获取原始文件路径
        source_path = chunk.metadata.get("source", "未知来源")
        # 提取纯文件名（例如：chapter1.pdf）
        file_name = os.path.basename(source_path)
        # 将来源信息拼接到文本块的最前面
        combined_text = f"【来源文件：{file_name}】\n{chunk.page_content}"
        texts.append(combined_text)
    
    # ! 增加非空判断
    if not texts:
        print(f"警告：{folder_name} 文件夹下未读取到任何有效文本，跳过该课程...")
        continue

    # 3. 分批调用 embedding-3 生成向量
    all_vectors = [] 
    batch_size = 64
    print(f"共生成 {len(texts)} 个带来源标注的文本块，准备获取向量...")

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        print(f"正在处理进度: {i+1} ~ {min(i+batch_size, len(texts))}...")
        
        response = client.embeddings.create(
            model="embedding-3",
            input=batch_texts,
            dimensions=512
        )

        # !!! 只收集纯向量数据，用于后续构建 Faiss 索引
        for data in response.data:
            all_vectors.append(data.embedding)

    # 4. 构建 Faiss 暴力搜索索引 (100% 精准度优化)
    print("\n正在构建预编译向量搜索引擎...")
    
    # !!! 将向量列表转换为 numpy 矩阵，这是 Faiss 要求的格式
    vectors_matrix = np.array(all_vectors).astype('float32')
    
    # !!! 对向量进行 L2 归一化。归一化后的“内积”计算等同于“余弦相似度”
    faiss.normalize_L2(vectors_matrix)
    
    # !!! 创建 IndexFlatIP 索引（暴力搜索，计算内积），维度为 512
    index = faiss.IndexFlatIP(512)
    
    # !!! 将所有向量一次性写入索引
    index.add(vectors_matrix)
    
    # 5. 分离保存：文本 JSON 和 向量 Index
    # !!! 定义输出文件名
    texts_file = f"texts_{suffix}.json"
    index_file = f"vector_db_{suffix}.index"
    
    # !!! 保存文本：只存带来源标注的字符串列表，极大地减小了 JSON 体积
    with open(texts_file, 'w', encoding='utf-8') as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
        
    # !!! 保存索引：将向量及其检索结构固化为二进制文件
    faiss.write_index(index, index_file)

    # 6. 打印统计信息
    print(f"\n✓ {folder_name} 知识库编译完成！")
    print(f"  - 文本文件: {texts_file}")
    print(f"  - 索引文件: {index_file}")
    print(f"  - 包含文本块总数: {len(texts)}")

print("\n所有课程知识库处理完毕，请运行 UI.py 启动系统。")