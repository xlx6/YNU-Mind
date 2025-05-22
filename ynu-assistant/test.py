import json
import asyncio
from langchain_openai import ChatOpenAI
from agents.kg_agent import KnowledgeGraphAgent
from agents.vector_agent import VectorDBAgent
from agents.response_agent import ResponseAgent
from routing_agent import RoutingAgent
from tqdm.asyncio import tqdm
import time



class SystemTest:
    def __init__(self, test_qa_path='./test/test_test.json'):
        self.test_qa_path = test_qa_path
        self.llm = ChatOpenAI(
            model="glm-4-air-250414",
            openai_api_key="",
            openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
            temperature=0
        )
        self.hy = ChatOpenAI(
            model='hunyuan-turbos-latest',
            openai_api_key="",
            openai_api_base='https://api.hunyuan.cloud.tencent.com/v1',
        )
        self.bc = ChatOpenAI(
            model='Baichuan4-Turbo',
            api_key="",
            openai_api_base='https://api.baichuan-ai.com/v1/',
            temperature=0
        )
        self.routing_agent = RoutingAgent(self.llm)
        self.kg_agent = KnowledgeGraphAgent(self.llm)
        self.vector_agent = VectorDBAgent()
        self.response_agent = ResponseAgent()

        with open(test_qa_path, 'r', encoding='utf-8') as f:
            self.test_qa = json.load(f)

    async def start(self):
        for item in tqdm(self.test_qa, desc="Processing Questions", unit="q"):
            t1 = time.time()
            question = item["question"]
            item['errors'] = []  # 每条记录都带错误收集字段

            # 路由阶段
            try:
                result_routing_str = await self.routing_agent.route(question)
                t2 = time.time()
                if "```json" in result_routing_str:
                    result_routing_str = result_routing_str.split("```json")[1].split("```")[0].strip()
                result_routing_obj = json.loads(result_routing_str)
                item['routing_result'] = result_routing_obj
                item['routing_time'] = t2 - t1
            except Exception as e:
                item['routing_result'] = {"error": str(e)}
                item['answer'] = "路由解析失败，无法生成回答"
                item['errors'].append(f"[Routing Error] {str(e)}")
                continue

            neo4j_middle_result = []
            vector_middle_result = []
            open_questions = []

            for sub_question, q_type in zip(result_routing_obj.get('question', []), result_routing_obj.get('type', [])):
                t3 = time.time()
                if q_type == 'neo4j':
                    result_query = await self.kg_agent.query(sub_question)
                    if "error" in result_query:
                        neo4j_middle_result.append({
                            'question': sub_question,
                            'content': f"[KG Error] {result_query['error']}",
                            'time': time.time() - t3
                        })
                        item['errors'].append(f"[KG Error] {sub_question}: {result_query['error']}")
                    else:
                        neo4j_middle_result.append({
                            'question': sub_question,
                            'content': result_query['data'],
                            'cypher': result_query['cypher'],
                            'time': time.time() - t3
                        })
                elif q_type == 'vector':
                    result_query = await self.vector_agent.query(sub_question)
                    if "error" in result_query:
                        vector_middle_result.append({
                            'question': sub_question,
                            'content': f"[Vector Error] {result_query['error']}",
                            'time': time.time() - t3
                        })
                        item['errors'].append(f"[Vector Error] {sub_question}: {result_query['error']}")
                    else:
                        vector_middle_result.append({
                            'question': sub_question,
                            'content': result_query['data'],
                            'time': time.time() - t3
                        })
                elif q_type == 'open':
                    open_questions.append({'question': sub_question})
                else:
                    item['errors'].append(f"[Unknown Type] {sub_question} - 类型 {q_type} 未知")

            item['neo4j'] = neo4j_middle_result
            item['vector'] = vector_middle_result
            item['open'] = open_questions

            # 构造上下文并生成最终回答
            context_parts = [f"{r['question']}：{r['content']}" for r in neo4j_middle_result + vector_middle_result]
            context = '\n'.join(context_parts)
            t4 = time.time()
            try:
                final_response = await self.response_agent.response(question, context)
                item['answer'] = final_response
                item['answer_time'] = time.time() - t4
            except Exception as e:
                item['answer'] = f"[Answer Error] 回答失败：{str(e)}"
                item['errors'].append(f"[Answer Error] {str(e)}")
                item['answer_time'] = time.time() - t4

        # 写入最终结果
            
        with open(self.test_qa_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_qa, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    asyncio.run(SystemTest().start())
