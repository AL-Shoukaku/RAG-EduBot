# 📚 Z.ai 高校专业课智能导学助教系统 (RAG)
欢迎加入本项目！这是一个基于 RAG（检索增强生成）技术开发的高校核心课程（如《操作系统》、《计算机组成原理》）智能答疑系统。本项目完全由纯 Python 编写，未使用笨重的第三方框架，核心检索算法采用了工业级的 FAISS 向量库，前端采用 Streamlit 实现了极简的现代化 Web 交互与流式输出。

## 🚀 快速开始 (Quick Start)
为了确保你能顺利在自己的电脑上跑通本项目，请严格按照以下步骤操作：

### 1.准备 Python 环境
建议使用 **Python 3.11 或 3.12**。当前项目依赖链在 Python 3.14 下存在兼容性问题，不建议直接使用。

推荐先创建虚拟环境，再安装依赖：

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2.需要安装的 Python 库
项目依赖已经整理到根目录的 `requirements.txt` 中，核心依赖包括：

- streamlit
- numpy
- faiss-cpu
- pypdf
- unstructured
- python-docx
- langchain-community
- langchain-text-splitters
- zai-sdk

说明：

- 当前代码使用的是新版 LangChain 的拆分包，不再直接从 `langchain` 顶层导入文档加载器和文本切分器。
- 当前项目没有使用 spaCy，已不再将其作为必装依赖。

### 3.配置API-key
1. 到[质谱清言官网](https://bigmodel.cn/console/overview)上申请一个API-key
2. 在当前目录新建一个key.txt文件，将自己的API-key写入。

**注意：请不要将自己的API-key推送到仓库中**

### 4.准备知识库
为了避免 Git 仓库臃肿，所有的课件和 PDF 资料不进行代码托管

新建一个名为knowledge_co的目录，用于存放计算机组成原理课程的资料

新建一个名为knowledge_os的目录，用于存放操作系统课程的资料。

### 5.生成向量库
运行embedding.py即可生成向量库，将会生成4个文件，text_co.json和text_os.json存储对应文本，vector_db_co.index和vector_db_os.json存储对应的向量索引

### 6.启动web界面
在终端输入`streamlit run UI.py`即可运行程序

## 代码结构指南
### 1.load_file.py
用于读取knowledge目录中的文件，然后将文本切分成若干个文本块，目前支持读取 docx、txt、pdf、md 四种类型的文件。

### 2.embedding.py
通过调用embedding-3模型，将文本块转化为向量，最终存储在向量库中。

### 3.RAG.py
输入问题，将问题转化为向量并与向量库中的向量计算余弦相似度，返回大于相似度阈值的前五个向量。

### 4.API.py
调用glm-4-flash模型，输入问题后调用RAG进行检索，将检索结果与问题一同发给AI，得到回答

### 5.UI.py
用streamlit搭建的前端界面设计

