from fastapi import APIRouter
from typing import Literal, List
from prompt.query import Query
from loguru import logger
from pydantic import BaseModel
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
                    "query": "机器人不回复了？",
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
    # 获取身份定义提示词
    system_prompt = '''
     【角色】：你是一位人工售后客服，根据上下文内容回答客户提出的咨询与问题
     【姓名】：小王 
     【性别】：女
     【年龄】：28岁(年轻有活力)
     【职业】：售后客服
     【性格】：耐心、细致、积极向上，乐于助人，能情绪稳定地处理客户疑问与投诉
     【语言风格】：温和、阳光、专业但不生硬，能够以亲和的语气安抚客户、解答疑问。常用口头禅语包括“亲”
     【核心能力】：理解用户问题→检索上下文内容→用通俗易懂的语言回答并适当安抚用户
     【适用场景】：商品咨询、物流追踪、售后退换、备注要求、优惠活动说明等
     【行为规范】：严格遵守提示词限制、根据已知信息回答问题
     '''
    # 生成用户提示词
    user_prompt = Query().format(identity=system_prompt, question=query, context=doc_content)
    with messages:
        messages.append(HumanMsg(content=user_prompt))

    ai_response = ""
    for chunk in model.stream(messages.to_json()):  # 流式获取 AI 生成内容
        ai_response += chunk

    return ResponseModel(code=200, message="success", data={"answer": ai_response})


