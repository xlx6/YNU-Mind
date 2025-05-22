from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class RoutingAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template("""
        请根据用户问题判断最合适的处理方式，类型包括：
        - neo4j：涉及教师、课程、教室、学院(网址等)、建筑等结构化校园信息
        - vector：涉及学生证补办、成绩单打印、缓考申请等办事流程（非结构化）
        - open：通用性知识问答，不需要网络搜索
        - search: 需要网络搜索的问题，如天气查询等

        ⚠️ 如果问题包含多个子问题，请拆分，每个子问题归类一个类型。

        📌 返回格式如下（**标准 JSON**）：
        {{
        "question": ["子问题1", "子问题2", ...],
        "type": ["neo4j", "vector", ...]
        }}

        示例：

        用户：介绍一下王津老师？
        回答：
        ```json
        {{
        "question": ["介绍一下王津老师？"],
        "type": ["neo4j"]
        }}```
        用户：计算机网络实践的教学班有多少人？学生申请课程免修办理流程的具体步骤有哪些？介绍一下图灵测试。
        回答：
        ```json
        {{
        "question": ["计算机网络实践的教学班有多少人？", "学生申请课程免修办理流程的具体步骤有哪些？", "介绍一下图灵测试。"],
        "type": ["neo4j", "vector", "open"]
        }}``` 
        当前问题：{question}""")

        self.chain = self.prompt | self.llm | self._parse_output

    def _parse_output(self, response):
        return response.content.strip()

    async def route(self, question: str) -> str:
        return await self.chain.ainvoke({"question": question})