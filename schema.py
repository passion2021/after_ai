from pydantic import BaseModel, Field
from typing import Optional, Any


# 定义统一的响应格式
class ResponseModel(BaseModel):
    code: int
    message: str
    data: Optional[Any] = {}
