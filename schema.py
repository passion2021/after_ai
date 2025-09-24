from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class QACreateRequest(BaseModel):
    """创建QA文档请求模型"""
    kb_id: Optional[int] = Field(None, description="知识库ID")
    question: str = Field(..., description="问题")
    answer: str = Field(..., description="答案")
    category_1: Optional[str] = Field(None, description="一级分类")
    category_2: Optional[str] = Field(None, description="二级分类")
    point_id: Optional[int] = Field(None, description="中台ID")
    record_url: Optional[str] = Field(None, description="录音文件链接")
    is_active: bool = Field(True, description="是否启用")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "kb_id": 1,
                    "question": "这款内衣是什么材质的？安全吗？",
                    "answer": "我们的内衣采用 A 类婴幼儿标准纯棉面料，无甲醛、无荧光剂，通过国家质检认证，柔软亲肤，对孩子娇嫩肌肤零刺激，家长可放心选购。",
                    "category_1": "产品咨询",
                    "category_2": "材质安全",
                    "point_id": 1001,
                    "record_url": "https://example.com/record/qa_001.mp3",
                    "is_active": True
                },
                {
                    "kb_id": 2,
                    "question": "内衣会掉色吗？",
                    "answer": "我们的内衣采用环保活性印染工艺，色牢度达到国家标准，正常洗涤不会出现掉色情况，您可以先单独冷水轻柔洗涤一次，观察有无轻微浮色。",
                    "category_1": "产品咨询",
                    "category_2": "洗涤保养",
                    "is_active": True
                }
            ]
        }
    }


class QAUpdateRequest(BaseModel):
    """更新QA文档请求模型"""
    kb_id: Optional[int] = Field(None, description="知识库ID")
    question: Optional[str] = Field(None, description="问题")
    answer: Optional[str] = Field(None, description="答案")
    category_1: Optional[str] = Field(None, description="一级分类")
    category_2: Optional[str] = Field(None, description="二级分类")
    point_id: Optional[int] = Field(None, description="中台ID")
    record_url: Optional[str] = Field(None, description="录音文件链接")
    is_active: Optional[bool] = Field(None, description="是否启用")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "这款内衣的材质是什么？安全吗？",
                    "answer": "我们的内衣采用 A 类婴幼儿标准纯棉面料，无甲醛、无荧光剂，通过国家质检认证，柔软亲肤，对孩子娇嫩肌肤零刺激，家长可放心选购。",
                    "category_1": "产品咨询",
                    "category_2": "材质安全",
                    "is_active": True
                },
                {
                    "answer": "我们的内衣采用环保活性印染工艺，色牢度达到国家标准，正常洗涤不会出现掉色情况。",
                    "category_2": "洗涤保养",
                    "is_active": False
                }
            ]
        }
    }


class QAResponse(BaseModel):
    """QA文档响应模型"""
    id: int
    kb_id: Optional[int]
    question: Optional[str]
    answer: Optional[str]
    category_1: Optional[str]
    category_2: Optional[str]
    point_id: Optional[int]
    record_url: Optional[str]
    is_delete: bool
    is_active: bool
    created_at: Optional[datetime]
    update_at: Optional[datetime]

    class Config:
        from_attributes = True


class QAListResponse(BaseModel):
    """QA文档列表响应模型"""
    items: List[QAResponse]
    total: int
    page: int
    page_size: int


class QASearchRequest(BaseModel):
    """QA搜索请求模型"""
    query: Optional[str] = Field(None, description="搜索关键词")
    kb_id: Optional[int] = Field(None, description="知识库ID")
    category_1: Optional[str] = Field(None, description="一级分类")
    category_2: Optional[str] = Field(None, description="二级分类")
    point_id: Optional[int] = Field(None, description="中台ID")
    is_active: Optional[bool] = Field(None, description="是否启用")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "内衣材质",
                    "kb_id": 1,
                    "category_1": "产品咨询",
                    "point_id": 1001,
                    "is_active": True,
                    "page": 1,
                    "page_size": 10
                },
                {
                    "query": "售后服务",
                    "category_2": "售后服务",
                    "point_id": 1002,
                    "page": 1,
                    "page_size": 20
                },
                {
                    "kb_id": 2,
                    "point_id": 1003,
                    "is_active": True,
                    "page": 1,
                    "page_size": 5
                }
            ]
        }
    }


class QABatchDeleteRequest(BaseModel):
    """批量删除QA文档请求模型"""
    ids: List[int] = Field(..., description="要删除的QA文档ID列表")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ids": [1, 2, 3, 4, 5]
                },
                {
                    "ids": [10, 15, 20]
                }
            ]
        }
    }

class BaseResponse(BaseModel):
    """基础响应模型"""
    code: int = Field(200, description="响应码")
    message: str = Field("success", description="响应消息")
    data: Optional[dict] = None