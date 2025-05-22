# -*- coding = utf-8 -*-
# @Time : 2025/4/18 17:07
# @Author : lx
# @File : webui_adapter.py.py
# @Software : PyCharm
import json
import time
from fastapi import APIRouter

router = APIRouter()

async def format_to_openwebui(response_gen):
    chat_id = f"chatcmpl-{int(time.time())}"
    created_time = int(time.time())

    # 起始：role 声明
    yield f"data: {json.dumps({
        'id': chat_id,
        'object': 'chat.completion.chunk',
        'created': created_time,
        'model': 'yunnan-uni-agent',
        'choices': [{
            'index': 0,
            'delta': {'role': 'assistant'},
            'finish_reason': None
        }]
    })}\n\n"

    # 正文：处理混合内容
    async for chunk in response_gen:
        delta = {}
        if 'content' in chunk:
            delta['content'] = chunk['content']
        if 'reasoning_content' in chunk:
            delta['reasoning_content'] = chunk['reasoning_content']
        
        yield f"data: {json.dumps({
            'id': chat_id,
            'object': 'chat.completion.chunk',
            'created': created_time,
            'model': 'yunnan-uni-agent',
            'choices': [{
                'index': 0,
                'delta': delta,
                'finish_reason': None
            }]
        })}\n\n"

    # 结束标记
    yield f"data: {json.dumps({
        'id': chat_id,
        'object': 'chat.completion.chunk',
        'created': created_time,
        'model': 'yunnan-uni-agent',
        'choices': [{
            'index': 0,
            'delta': {},
            'finish_reason': 'stop'
        }]
    })}\n\n"

# async def format_to_openwebui(response_gen):
#     chat_id = f"chatcmpl-{int(time.time())}"
#     created_time = int(time.time())

#     # 起始：role 声明
#     yield f"data: {json.dumps({
#         'id': chat_id,
#         'object': 'chat.completion.chunk',
#         'created': created_time,
#         'model': 'yunnan-uni-agent',
#         'choices': [{
#             'index': 0,
#             'delta': {'role': 'assistant'},
#             'finish_reason': None
#         }]
#     })}\n\n"

#     # 正文：增量输出（处理中间结果和响应内容）
#     async for chunk in response_gen:
#         if chunk:
#             delta = {}
#             # 填充内容字段
#             if 'content' in chunk and chunk['content'] is not None:
#                 delta['content'] = chunk['content']
#             # 填充思维链字段
#             if 'reasoning_content' in chunk and chunk['reasoning_content'] is not None:
#                 delta['reasoning_content'] = chunk['reasoning_content']
            
#             yield f"data: {json.dumps({
#                 'id': chat_id,
#                 'object': 'chat.completion.chunk',
#                 'created': created_time,
#                 'model': 'yunnan-uni-agent',
#                 'choices': [{
#                     'index': 0,
#                     'delta': delta,
#                     'finish_reason': None
#                 }]
#             })}\n\n"

#     # 结束：finish_reason
#     yield f"data: {json.dumps({
#         'id': chat_id,
#         'object': 'chat.completion.chunk',
#         'created': created_time,
#         'model': 'yunnan-uni-agent',
#         'choices': [{
#             'index': 0,
#             'delta': {},
#             'finish_reason': 'stop'
#         }]
#     })}\n\n"


# async def format_to_openwebui(response_gen):
#     chat_id = f"chatcmpl-{int(time.time())}"
#     created_time = int(time.time())

#     # 起始：role 声明
#     yield f"data: {json.dumps({
#         'id': chat_id,
#         'object': 'chat.completion.chunk',
#         'created': created_time,
#         'model': 'yunnan-uni-agent',
#         'choices': [{
#             'index': 0,
#             'delta': {'role': 'assistant'},
#             'finish_reason': None
#         }]
#     })}\n\n"  # ← 注意两个换行符

#     # 正文：增量输出
#     async for chunk in response_gen:
#         if chunk:
#             yield f"data: {json.dumps({
#                 'id': chat_id,
#                 'object': 'chat.completion.chunk',
#                 'created': created_time,
#                 'model': 'yunnan-uni-agent',
#                 'choices': [{
#                     'index': 0,
#                     'delta': {'content': chunk, 'reasoning_content': None},
#                     'finish_reason': None
#                 }]
#             })}\n\n"  # ← 注意两个换行符

#     # 结束：finish_reason
#     yield f"data: {json.dumps({
#         'id': chat_id,
#         'object': 'chat.completion.chunk',
#         'created': created_time,
#         'model': 'yunnan-uni-agent',
#         'choices': [{
#             'index': 0,
#             'delta': {},
#             'finish_reason': 'stop'
#         }]
#     })}\n\n"  # ← 注意两个换行符
