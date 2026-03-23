from zai import ZhipuAiClient
import json
# ! 导入 load_file.py 中的加载和分块函数
from load_file import load_and_split_docs_from_folder

from pathlib import Path
path = Path("key.txt")
key = path.read_text().strip()

# 1. 初始化客户端
client = ZhipuAiClient(api_key=key)

# 2. 知识库文本
# ! 调用函数读取 knowledge 目录下的文件进行分块
chunks = load_and_split_docs_from_folder("knowledge")
# ! 提取 Document 对象中的文本内容（page_content）组成字符串列表，供模型使用
texts = [chunk.page_content for chunk in chunks]

# 3. 分批调用embedding-3生成向量
# ! 提前定义好用来存储最终结果的列表
vector_db = []
# ! 设置每批处理的最大数量，智谱 API 限制为最大 64
batch_size = 64
print(f"共提取到 {len(texts)} 条文本块，准备分批生成向量...")

# ! 使用 range 函数按 batch_size 的步长遍历所有文本
for i in range(0, len(texts), batch_size):
    # ! 截取当前批次的文本
    batch_texts = texts[i:i + batch_size]
    # ! 打印当前的进度，方便观察运行状态
    print(f"正在处理第 {i+1} 到 {min(i+batch_size, len(texts))} 条...")
    
    # ! 请求 API 处理当前批次
    response = client.embeddings.create(
        model="embedding-3",
        input=batch_texts,
        dimensions=512
    )

    # 4. 构建向量库（向量 + 对应文本）
    # ! 遍历当前批次返回的结果并将其加入到总向量库中
    for j, data in enumerate(response.data):
        vector_db.append({
            "text": batch_texts[j],     # ! 对应当前批次内的原始文本
            "vector": data.embedding,   # 向量值
            "index": i + j              # ! 计算在全局列表中的绝对索引
        })

# 5. 输出向量库内容
print("\n=== 向量库内容（仅预览前10条） ===")
# ! 使用切片 [:10] 限制只遍历前 10 个向量块
for item in vector_db[:10]:
    # ! 由于真实的知识库文本块往往较长，这里修改为只截取前 30 个字符进行打印预览，避免刷屏
    print(f"\n文本: {item['text'][:30]}...")
    print(f"向量维度: {len(item['vector'])}")
    print(f"向量前5个值: {[round(x, 4) for x in item['vector'][:5]]}")

# 6. 保存完整的向量库到文件
with open("vector_db.json", "w", encoding="utf-8") as f:
    # 保存完整的向量数据
    json.dump(vector_db, f, ensure_ascii=False, indent=2)
    print("\n✓ 向量库已完整保存到 vector_db.json")
    print(f"  共保存 {len(vector_db)} 个向量")
    # ! 增加非空判断，防止 knowledge 文件夹为空时获取不到向量而导致 IndexError
    if vector_db:
        print(f"  每个向量维度: {len(vector_db[0]['vector'])}")

print(f"\n总共生成 {len(vector_db)} 个向量")