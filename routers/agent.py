import json
from fastapi import APIRouter, UploadFile, File, Form
from typing import Literal, List, Optional
from starlette.responses import StreamingResponse
from libs.easy_llm.utils import extract_struct, json_parse_dirty
from prompt.query import Query, GenerateQA
from loguru import logger
from pydantic import BaseModel, Field
from libs.easy_llm import *
from db.conn import vector_db
from schema import ResponseModel

router = APIRouter(
    prefix="/ai",
)  # 定义请求体


def set_llm(model):
    if model == "gpt-4o-mini":
        logger.info("使用 gpt-4o-mini 模型")
        return openai_chat
    elif model == "deepseek-v3":
        logger.info("使用 deepseek-v3 模型")
        return deepseek_v3_chat
    elif model == "qwen2.5:14b":
        return qwen2_5_14b
    elif model == "qwen-plus":
        return qwen_chat

class QueryRequest(BaseModel):
    document_ids: List[int]
    query: str
    model: Literal["qwen-plus"]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "document_ids": [1],
                    "query": "可以退货吗？",
                    "model": "qwen-plus"
                }
            ]
        }
    }


# 流式返回 AI 结果
@router.post("/chat", tags=["问答接口"], description="返回文本")
async def query(request: QueryRequest):
    messages = MsgList(git_mode=False)
    model = set_llm(request.model)
    query = request.query
    document_ids = request.document_ids
    if not query:
        return ResponseModel(code=400, message="问题不能为空",
                             data={"query": query, "document_ids": document_ids, "model": request.model})
    # 检索相关文档
    doc_content = vector_db.retrieve(document_ids=document_ids, query=query)
    # 生成用户提示词
    user_prompt = Query().format(question=query, context=doc_content)
    with messages:
        messages.append(HumanMsg(content=user_prompt))

    # logger.info(json.dumps(messages.to_json(), ensure_ascii=False, indent=4))

    ai_response = ""
    for chunk in model.stream(messages.to_json()):  # 流式获取 AI 生成内容
        ai_response += chunk

    return ResponseModel(code=200, message="success", data={"answer": ai_response})


class retrieveRequest(BaseModel):
    document_ids: Optional[List[int]] = Field(
        default=None,
        description="文档 ID 列表（可选，与 category 至少需要一个）",
        example=[1, 2, 3]
    )
    category: Optional[str] = Field(
        default=None,
        description="文档分类（可选，与 document_ids 至少需要一个）",
        example="clothes"
    )
    query: str = Field(..., description="检索问题", example="这个衣服会褪色吗？")
    top_k: int = Field(default=5, description="返回结果数量上限", example=3)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "document_ids": [2],
                    "query": "这个衣服会褪色吗？",
                    "category": "通用",
                    "top_k": 5
                }
            ]
        }
    }


@router.post("/retrieve", tags=["检索接口"])
async def retrieve_data(request: retrieveRequest):
    doc_content = vector_db.retrieve(document_ids=request.document_ids, category=request.category, query=request.query,
                                     top_k=request.top_k)
    return ResponseModel(code=200, message="success", data=doc_content)


class messagesRequest(BaseModel):
    messages: List[dict]
    model: Literal["gpt-4o-mini", "deepseek-v3", "qwen2.5:14b", "qwen-plus"]
    document_ids: Optional[List[int]] = Field(
        default=None,
        description="文档 ID 列表（可选，与 category 至少需要一个）",
        example=[1, 2, 3]
    )
    category: Optional[str] = Field(
        default=None,
        description="文档分类（可选，与 document_ids 至少需要一个）",
        example="clothes"
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model": "qwen-plus",
                    "document_ids": [2],
                    "category": "通用",
                    "messages": [
                        {
                            "role": "user",
                            "content": "有售后服务吗？"
                        },
                        {
                            "role": "assistant",
                            "content": "亲，我们提供完善的售后服务哦，如果您收到的内衣出现质量问题，如开线、破损等，可以在规定时间内联系客服，我们会为您安排退换货或相应的解决方案。"
                        },
                        {
                            "role": "user",
                            "content": "我刚刚的问题是？"
                        }
                    ]
                }
            ]
        }
    }


def check_messages(messages):
    last_human_speak = messages[-1]['content']
    msglist = []
    for msg in messages:
        if msg['role'] == 'user':
            msglist.append(HumanMsg(content=msg['content']))
        elif msg['role'] == 'assistant':
            msglist.append(AIMsg(content=msg['content']))
        elif msg['role'] == 'system':
            msglist.append(SystemMsg(content=msg['content']))
    return msglist, last_human_speak


@router.post("/messages", tags=["上下文问答接口"], description="流式返回文本")
async def massages_ask(request: messagesRequest):
    model = set_llm(request.model)
    messages, query = check_messages(request.messages)
    # 检索相关文档
    doc_content = vector_db.retrieve(document_ids=request.document_ids, category=request.category, query=query)
    if not doc_content:
        return ResponseModel(code=1024, message="知识库未找到相关文档",
                             data={})
    # 生成系统提示词
    system_prompt = Query().format(question=query, context=doc_content)
    messages = messages[-20:]  # 取最近20个消息
    messages = [SystemMsg(content=system_prompt)] + messages
    messages[-1].content = f'用户说：{messages[-1].content}\n根据高分知识回复：{doc_content}'
    messages = MsgList(*messages, git_mode=False)
    logger.info(messages)
    ai_response = ""
    for chunk in model.stream(messages.to_json()):  # 流式获取 AI 生成内容
        ai_response += chunk
    logger.info(f"{ai_response}")
    if '我无法回答' in ai_response:
        return ResponseModel(code=1024, message="ai无法回答", data={})
    else:
        return ResponseModel(code=200, message="success", data={"answer": ai_response})


def extract_qa_from_file(document: str, prompt: str):
    model = set_llm("qwen-plus")
    messages = MsgList(git_mode=False)
    user_prompt = GenerateQA().format(prompt=prompt, content=document)
    logger.info(user_prompt)
    messages.append(HumanMsg(content=user_prompt))
    llm_resp = ''
    for chunk in model.stream(messages.to_json()):
        llm_resp += chunk
        print(chunk, end='')
    return extract_struct(llm_resp, list)


# @router.post("/extract_qa", tags=["提取文档中的QA"])
# async def upload_file(
#         file: UploadFile = File(...),
#         prompt: Optional[str] = Form(None)
# ):
#     contents = await file.read()
#     try:
#         document = contents.decode('utf-8')  # decode 成 str
#     except UnicodeDecodeError:
#         # 如果不是 utf-8 编码，可以尝试 gbk 或其他编码，或者返回错误
#         return ResponseModel(code=400, message="文件编码格式错误，无法解码为 utf-8", data=None)
#     prompt = prompt or "请从文件中提取20个qa"
#     # 在这里使用 prompt 和文件内容提取 QA（你的核心逻辑）
#     qa_result = extract_qa_from_file(document, prompt)  # 伪函数
#
#     data = {
#         "filename": file.filename,
#         "content_type": file.content_type,
#         "size": len(contents),
#         "prompt": prompt,
#         "qa": qa_result
#     }
#     return ResponseModel(code=200, message="success", data=data)
