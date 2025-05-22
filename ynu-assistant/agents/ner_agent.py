from langchain_openai import ChatOpenAI
import json
from ner import NER


class NERAgent:
    def __init__(self, llm):
        pass
        # self.ner = NER(llm=llm)
    def query(self, question: str) -> str:
        # entities_str = await self.ner.process(question=question)
        entities_str = """```json
                        {
                            "person": ["王静"],
                            "classroom": ["格物楼1栋1507"],
                            "course": ["算法课"],
                            "department": ["信院"]
                        }
                        ```"""
        if "```json" in entities_str:
            entities_str = entities_str.split("```json")[1].split("```")[0].strip()
        entities_obj = json.loads(entities_str)
        print(entities_obj)
if __name__ == "__main__":
    agent = NERAgent(llm=None)
    question = "信院的王静老师的算法课是在格物楼1栋1507上吗？"
    agent.query(question)
    
