from langchain_openai import ChatOpenAI

from .kg_qa import KGQA


class KnowledgeGraphAgent:
    def __init__(self, llm):
        self.kg = KGQA(llm=llm)

    async def query(self, question: str) -> dict:
        try:
            result = self.kg.neo4j_query(question)
            return {"type": "neo4j", "data": result["content"], 'cypher': result['cypher']}
        except Exception as e:
            return {"error": str(e)}