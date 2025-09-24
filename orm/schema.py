import os
from typing import Optional, Any, List
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlmodel import Field, SQLModel, Session, select
from urllib.parse import quote_plus
from datetime import datetime
from zoneinfo import ZoneInfo
from pgvector.sqlalchemy import Vector

load_dotenv()
password = os.getenv("POSTGRESQL_PASSWORD")


class QADocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, description="主键")
    kb_id: Optional[int] = Field(default=None, description="知识库ID")
    question: Optional[str] = Field(default=None, description="问题")
    answer: Optional[str] = Field(default=None, description="答案")
    category_1: Optional[str] = Field(default=None, description="一级分类")
    category_2: Optional[str] = Field(default=None, description="二级分类")
    embedding: Optional[Any] = Field(sa_type=Vector(1024), nullable=True, description="向量")
    point_id: Optional[int] = Field(default=None, description="中台ID")
    record_url: Optional[str] = Field(default=None, description="录音文件链接")
    is_delete: bool = Field(default=False, nullable=False, description="是否删除")
    is_active: bool = Field(default=True, nullable=False, description="是否启用")
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")),
        description="创建时间"
    )
    update_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")),
        description="更新时间"
    )

db_url = "postgresql://%s:%s@%s:%d/%s" % (
    quote_plus("postgres"),
    quote_plus(password),
    "36.134.51.155",
    5432,
    "lryk",
)
engine = create_engine(db_url)
# 创建表
SQLModel.metadata.create_all(engine)



