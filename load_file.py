# 导入所需的库
import os

try:
    from langchain_community.document_loaders import (
        PyPDFLoader,  # 用于加载 PDF 文件
        TextLoader,  # 用于加载 TXT 文件
        UnstructuredWordDocumentLoader,  # 用于加载 Word 文档 (.docx)
        UnstructuredMarkdownLoader,  # 用于加载 Markdown 文件 (.md)
    )
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "缺少文档加载依赖。请在 Python 3.11/3.12 环境中执行 "
        "`python -m pip install -r requirements.txt`。"
    ) from exc

def load_document(file_path):
    """
    根据文件扩展名选择合适的加载器，返回 Document 对象列表。
    支持 .pdf, .txt, .docx 格式，可根据需要扩展。
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        loader = PyPDFLoader(file_path)
    elif ext == '.txt':
        # 指定编码为 utf-8，避免中文乱码
        loader = TextLoader(file_path, encoding='utf-8')
    elif ext in ['.docx', '.doc']:
        loader = UnstructuredWordDocumentLoader(file_path)
     # !!! 增加对 .md 和 .markdown 文件的支持
    elif ext in ['.md', '.markdown']:
        loader = UnstructuredMarkdownLoader(file_path)
    else:
        # 不支持的文件格式，返回空列表或抛出警告
        print(f"跳过不支持的文件格式: {file_path}")
        return []
    
    try:
        documents = loader.load()
        print(f"成功加载文件: {file_path}，共 {len(documents)} 页/段")
        return documents
    except Exception as e:
        print(f"加载文件 {file_path} 时出错: {e}")
        return []

def load_and_split_docs_from_folder(folder_path, chunk_size=500, chunk_overlap=50):
    """
    遍历文件夹中所有支持的文件，加载并分块，返回所有文档块的列表。
    每个文本块开头会自动添加来源文件信息。
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    all_documents = []  # 收集所有原始文档（每页/每段）
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # 跳过子文件夹，只处理文件
        if not os.path.isfile(file_path):
            continue
        
        # 加载单个文件
        docs = load_document(file_path)
        
        # 为当前文件的所有文档添加来源标记
        source_info = f"【来源文件：{filename}】\n"
        for doc in docs:
            # 在文档内容开头添加来源信息
            doc.page_content = source_info + doc.page_content
            
        all_documents.extend(docs)
    
    if not all_documents:
        print("警告：未加载到任何文档，请检查文件夹中的文件格式。")
        return []
    
    print(f"\n总共加载了 {len(all_documents)} 个原始文档页/段，开始分块...")
    
    # --- 初始化文本分割器 ---
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=[
            "\n\n",
            "\n",
            "。", "！", "？",
            "；", "，", "、",
            " ",
            ""
        ]
    )
    
    # 对所有原始文档进行分块
    chunks = text_splitter.split_documents(all_documents)
    print(f"分块完成，共生成 {len(chunks)} 个文本块。")
    
    # 可选：打印前几个块作为预览
    for i, chunk in enumerate(chunks[20:30]):  # 只打印第21-30个块作为示例
        print(f"\n--- 全局块 {i+1} ---")
        print(f"元数据: {chunk.metadata}")
        print(f"内容预览: {chunk.page_content[:150]}...")
    
    return chunks

# --- 主程序示例 ---
if __name__ == "__main__":
    # 指定知识库文件夹路径
    folder = "knowledge"
    # 调用函数处理所有文件
    all_chunks = load_and_split_docs_from_folder(folder, chunk_size=500, chunk_overlap=50)
    
    # 如果你想把所有块保存起来供后续使用，可以在这里写入文件或直接传给向量库
    # 例如：将块列表保存为 pickle 文件
    # import pickle
    # with open("all_chunks.pkl", "wb") as f:
    #     pickle.dump(all_chunks, f)
