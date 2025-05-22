# -*- coding = utf-8 -*-
# @Time : 2025/4/18 15:02
# @Author : lx
# @File : main.py.py
# @Software : PyCharm
from fastapi import FastAPI
from contextlib import asynccontextmanager

from langchain_openai import ChatOpenAI
from fastapi.responses import StreamingResponse

from agents.kg_agent import KnowledgeGraphAgent
from agents.response_agent import ResponseAgent
from fastapi.middleware.cors import CORSMiddleware
from agents.vector_agent import VectorDBAgent
from agents.websearch import WebSearchAgent
from schemas import ChatRequest
from webui_adapter import format_to_openwebui
from routing_agent import RoutingAgent
from agents import *
import json
from agents.ner import NER
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    llm = ChatOpenAI(
        model="glm-4-plus",
        openai_api_key=os.get("OPENAI_API_KEY"),
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )
    qwen = ChatOpenAI(
        model="qwen-max",
        openai_api_key=os.get("OPENAI_API_KEY"),
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    app.state.routing_agent = RoutingAgent(qwen)
    app.state.kg_agent = KnowledgeGraphAgent(qwen)
    app.state.vector_agent = VectorDBAgent()
    app.state.response_agent = ResponseAgent()
    app.state.websearch_agent = WebSearchAgent()
    app.state.ner_agent = NER(qwen)

    app.state.llm = llm
    
    yield

app = FastAPI(
    title="云南大学智能助手 API",
    description="提供兼容 OpenAI 的问答服务",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/openai/models")
async def list_models():
    return {
        "object": "list",
        "data": [{
            "id": "Ynu-Assistant",
            "name": "Ynu-Assistant",
            "object": "model",
            "info": {
                "meta": {
                    "profile_image_url": "/ROMvxnXmql.png",
                    "description": "输入关于校园生活的问题，我将通过：问题解析 → 智能路由 → 多源查询 为您提供精准解答",
                    "model_ids": None
                }
            },
            "created": 1686935002,
            "owned_by": "YNU"
        }]
    }


# @app.post("/openai/chat/completions")
# async def chat_endpoint(request: ChatRequest):
#     reasoning_results = []
#     user_question = request.messages[-1].content
#     ner_agent = app.state.ner_agent
#     routing_agent = app.state.routing_agent
#     kg_agent = app.state.kg_agent
#     vector_agent = app.state.vector_agent
#     response_agent = app.state.response_agent
#     websearch_agent = app.state.websearch_agent
#     # print(f'INFO: User question: {user_question}')



#     if user_question.startswith("json") or user_question.startswith("###"):
#         async def dummy_stream():
#             resp = app.state.llm.invoke(user_question)
#             yield f"data: {resp.content}\n\n"
#         yield StreamingResponse(dummy_stream(), media_type="text/event-stream")##
#     # 实体修正
#     user_question, reason = await ner_agent.process(user_question)
#     reasoning_results.append(reason)
#     yield {'reasoning_content': reason}
#     # 路由决策
#     result_routing_str = await routing_agent.route(user_question)
#     if "```json" in result_routing_str:
#         result_routing_str = result_routing_str.split("```json")[1].split("```")[0].strip()
#     result_routing_obj = json.loads(result_routing_str)

#     reasoning_results.append('意图识别与子问题拆分'+result_routing_str + '\n')
#     yield {'reasoning_content': '意图识别与子问题拆分'+result_routing_str + '\n'}
#     middle_results = []
    
#     reasoning_results.append('子问题查询：' + '\n')
#     for sub_question, q_type in zip(result_routing_obj.get('question', []), result_routing_obj.get('type', [])):
#         if q_type == "neo4j":
#             result = await kg_agent.query(sub_question)
#         elif q_type == "vector":
#             result = await vector_agent.query(sub_question)
#         elif q_type == "search":
#             result = await websearch_agent.search(sub_question)
#         else:
#             result = None
#         middle_results.append({"问题": sub_question, "相关资料": result})
#         reasoning_results.append(f"{q_type} 问题: {sub_question}\n相关资料: {result}\n")
#         yield {'reasoning_content': f"{q_type} 问题: {sub_question}\n相关资料: {result}\n"}

#     middle_results_string = json.dumps(middle_results, ensure_ascii=False)
#     # print(f"INFO: Middle results: {middle_results}")
#     # 生成流式响应
#     async def generate_reasoning_chunks():
#         for result in reasoning_results:
#             yield {'reasoning_content': result}
#     response_gen = response_agent.stream_response(question=middle_results_string)

#     async def combined_generator():
#         async for chunk in generate_reasoning_chunks():
#             yield chunk
#         async for chunk in response_gen:
#             yield chunk

#     yield StreamingResponse(
#         format_to_openwebui(response_gen),
#         media_type="text/event-stream"
#     )

@app.post("/openai/chat/completions")
async def chat_endpoint(request: ChatRequest):
    reasoning_results = []
    user_question = request.messages[-1].content
    ner_agent = app.state.ner_agent
    routing_agent = app.state.routing_agent
    kg_agent = app.state.kg_agent
    vector_agent = app.state.vector_agent
    response_agent = app.state.response_agent
    websearch_agent = app.state.websearch_agent
    
    async def generate_full_stream(user_question):
        # 处理特殊请求
        if user_question.startswith("json") or user_question.startswith("###"):
            resp = app.state.llm.invoke(user_question)
            yield {'content': resp.content}
            return

        # 实体修正
        user_question, reason = await ner_agent.process(user_question)
        yield {'reasoning_content': f"实体修正结果: {reason}"}

        # 路由决策
        result_routing_str = await routing_agent.route(user_question)
        if "```json" in result_routing_str:
            result_routing_str = result_routing_str.split("```json")[1].split("```")[0].strip()
        yield {'reasoning_content': f"路由决策结果: {result_routing_str}"}

        result_routing_obj = json.loads(result_routing_str)
        
        # 处理子问题
        middle_results = []
        for sub_question, q_type in zip(result_routing_obj.get('question', []), result_routing_obj.get('type', [])):
            # 实时生成中间结果
            yield {'reasoning_content': f"开始处理 {q_type} 问题: {sub_question}"}
            
            if q_type == "neo4j":
                result = await kg_agent.query(sub_question)
            elif q_type == "vector":
                result = await vector_agent.query(sub_question)
            elif q_type == "search":
                result = await websearch_agent.search(sub_question)
            else:
                result = None
                
            yield {'reasoning_content': f"{q_type} 查询结果: {result}"}
            middle_results.append({"问题": sub_question, "相关资料": result})

        # 生成最终响应
        middle_results_string = json.dumps(middle_results, ensure_ascii=False)
        response_gen = response_agent.stream_response(question=middle_results_string)
        
        async for chunk in response_gen:
            # 混合最终响应内容
            yield {'content': chunk.get('content', '')}

    return StreamingResponse(
        format_to_openwebui(generate_full_stream(user_question)),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
