# src/vector_db.py
import os
import sys
from langchain_chroma import Chroma
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
import json


class ProcedureQA:
    def __init__(self, procedure_data_path=None, persist_dir=None):
        """
        初始化问答系统

        Args:
            procedure_data_path (str): 流程数据JSON文件路径
            persist_dir (str): 向量数据库存储目录
        """
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置默认路径
        if procedure_data_path is None:
            procedure_data_path = os.path.join(current_dir, "data", "procedure.json")
        if persist_dir is None:
            persist_dir = os.path.join(current_dir, "chroma_db")

        # 确保目录存在
        os.makedirs(os.path.dirname(procedure_data_path), exist_ok=True)
        os.makedirs(persist_dir, exist_ok=True)

        os.environ['ZHIPUAI_API_KEY'] = ''

        # 加载数据
        with open(procedure_data_path, "r", encoding='utf-8') as f:
            self.procedure_data = json.load(f)

        self.document = [
            Document(
                page_content=x['title'],
                metadata={"idx": idx}
            ) for idx, x in enumerate(self.procedure_data)
        ]

        # 初始化嵌入模型
        self.embedding = ZhipuAIEmbeddings(model='embedding-3')
        self.persist_dir = persist_dir

        # 初始化向量数据库
        self.vector_store = self._init_vector_store()
        self.retriever = RunnableLambda(self.vector_store.max_marginal_relevance_search).bind(k=1)

        self.chain = (
                {"retrieved_docs": self.retriever, "question": RunnablePassthrough()}
                | RunnableLambda(self._format_response))

    def _init_vector_store(self):
        """初始化向量数据库"""
        if os.path.exists(self.persist_dir) and os.listdir(self.persist_dir):
            # 从磁盘加载
            print("Loading existing vector store...")
            return Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embedding
            )
        else:
            # 创建新的并存储到磁盘
            print("Creating new vector store...")
            return Chroma.from_documents(
                documents=self.document,
                embedding=self.embedding,
                persist_directory=self.persist_dir
            )

    def _format_response(self, data):
        """处理检索结果和用户问题"""
        retrieved_docs = data["retrieved_docs"]
        question = data["question"]

        if not retrieved_docs:
            return {"question": question, "content": "未找到相关信息"}

        texts = []
        idx = retrieved_docs[0].metadata['idx']
        text = self.procedure_data[idx].get('text')  # 安全取值
        if text:
            texts.append(text)
        if self.procedure_data[idx].get('img'):
            text = f"详细流程请参考下图：https://procedure-1319755979.cos.ap-chengdu.myqcloud.com/{idx}.png"
            texts.append(text)

        final_text = "\n".join(texts)
        return {"question": question, "content": final_text}

    def vector_query(self, question):
        return self.chain.invoke(question)


if __name__ == "__main__":
    qa_system = ProcedureQA()
    print(qa_system.vector_query('如何放弃辅修？'))
