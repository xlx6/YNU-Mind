# -*- coding = utf-8 -*-
# @Time : 2025/4/18 17:06
# @Author : lx
# @File : vector_agent.py
# @Software : PyCharm
from .vector_db import ProcedureQA


class VectorDBAgent:
    def __init__(self):
        self.vector_qa = ProcedureQA()

    async def query(self, question: str) -> dict:
        try:
            result = self.vector_qa.vector_query(question)
            return {"type": "vector", "data": result["content"]}
        except Exception as e:
            return {"error": str(e)}
