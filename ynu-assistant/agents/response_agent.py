# -*- coding = utf-8 -*-
# @Time : 2025/4/18 17:06
# @Author : lx
# @File : response_agent.py.py
# @Software : PyCharm
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os


class ResponseAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
        model="glm-4-air-250414",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        stream=False
    )
        self.prompt = ChatPromptTemplate.from_template("""
        你是云南大学的智能助手 Ynu-Assistant，专为解答与校园生活相关的问题而设计。

        你将接收到用户的问题和系统提供的参考资料。需要你自己从参考资料中提取有用信息，并且整合结果：
        **输入格式**
        [{{问题：用户问题1，相关资料：参考资料1}}，……]

        请注意：
                                            
        - 若背景信息中包含图片链接，请仅将链接转换为 Markdown 格式输出（例如：`![图示](链接)`），无需解释。
        - 若问题属于开放领域（如通识知识），请直接作答，无需依赖背景资料。
        - 若某个问题给出了背景资料，那么这个背景资料一定是和问题相关的                                              
        - 若提供的信息不足以回答，请简洁说明，如：“暂未找到相关信息”。

        请用**简洁、清晰的中文**回答，确保准确、有条理。
        输入：{question}""")
        self.chain = self.prompt | self.llm

    async def response(self, question: str) -> str:
        response = await self.chain.ainvoke({"question": question})
        return response.content
    async def stream_response(self, question: str) -> dict:
        chain = self.prompt | self.llm
        async for chunk in chain.astream({"question": question}):
            # 确保 chunk.content 是字符串
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            yield {'content':content, 'reasoning_content': None}