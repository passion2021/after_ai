import json
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


# pip install psycopg2
class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))


class QADocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int  # 关联 Document 的 id，弱关联，代码层控制
    question: Optional[str] = None
    answer: Optional[str] = None
    # embedding 是 pgvector 的 VECTOR(1024)，这里用 bytes 或 str 占位，具体用法见下
    embedding: Any = Field(sa_type=Vector(1024))
    created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Shanghai")))
    # 新增字段
    is_delete: bool = Field(default=False, nullable=False, description="逻辑删除标记")
    category: Optional[str] = Field(default=None, description="行业分类(直接存字符串)")
    point_id: Optional[int] = Field(default=None, description="中台id")

db_url = "postgresql://%s:%s@%s:%d/%s" % (
    quote_plus("postgres"),
    quote_plus(password),
    "117.72.210.205",
    5433,
    "after_ai"
)
engine = create_engine(db_url)
# 创建表
SQLModel.metadata.create_all(engine)



