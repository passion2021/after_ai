#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/24 09:54
# @Author  : 李明轩
# @File    : qa.py
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, and_, or_
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from orm.schema import engine, QADocument
from schema import (
    QACreateRequest, QAUpdateRequest, QAResponse,
    QASearchRequest, QABatchDeleteRequest, BaseResponse
)
from libs.easy_llm.llm.embed import get_text_embedding
from loguru import logger

router = APIRouter(
    prefix="/qa",
    tags=["知识库QA管理"]
)


def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session


@router.post("/create", response_model=BaseResponse, summary="创建QA文档")
async def create_qa(request: QACreateRequest, session: Session = Depends(get_session)):
    """创建新的QA文档"""
    try:
        # 生成问题向量
        question_embedding = get_text_embedding(request.question) if request.question else None

        # 创建QA文档
        qa_doc = QADocument(
            kb_id=request.kb_id,
            question=request.question,
            answer=request.answer,
            category_1=request.category_1,
            category_2=request.category_2,
            point_id=request.point_id,
            record_url=request.record_url,
            is_active=request.is_active,
            embedding=question_embedding
        )

        session.add(qa_doc)
        session.commit()
        session.refresh(qa_doc)

        logger.info(f"创建QA文档成功，ID: {qa_doc.id}")
        return BaseResponse(
            code=200,
            message="创建成功",
            data={"id": qa_doc.id, "question": qa_doc.question, "answer": qa_doc.answer,
                  "category_1": qa_doc.category_1, "category_2": qa_doc.category_2, "point_id": qa_doc.point_id,
                  "record_url": qa_doc.record_url, "is_active": qa_doc.is_active}
        )
    except Exception as e:
        logger.error(f"创建QA文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.post("/search", response_model=BaseResponse, summary="搜索QA文档")
async def search_qa(request: QASearchRequest, session: Session = Depends(get_session)):
    """搜索QA文档"""
    try:
        # 构建查询条件
        conditions = [QADocument.is_delete == False]

        if request.kb_id is not None:
            conditions.append(QADocument.kb_id == request.kb_id)
        if request.category_1:
            conditions.append(QADocument.category_1 == request.category_1)
        if request.category_2:
            conditions.append(QADocument.category_2 == request.category_2)
        if request.point_id is not None:
            conditions.append(QADocument.point_id == request.point_id)
        if request.is_active is not None:
            conditions.append(QADocument.is_active == request.is_active)
        if request.query:
            conditions.append(
                or_(
                    QADocument.question.contains(request.query),
                    QADocument.answer.contains(request.query)
                )
            )

        # 计算总数
        count_statement = select(QADocument).where(and_(*conditions))
        total = len(session.exec(count_statement).all())

        # 分页查询
        offset = (request.page - 1) * request.page_size
        statement = (
            select(QADocument)
            .where(and_(*conditions))
            .order_by(QADocument.created_at.desc())
            .offset(offset)
            .limit(request.page_size)
        )

        qa_docs = session.exec(statement).all()

        items = [QAResponse.model_validate(doc).model_dump() for doc in qa_docs]

        return BaseResponse(
            code=200,
            message="搜索成功",
            data={
                "items": items,
                "total": total,
                "page": request.page,
                "page_size": request.page_size
            }
        )
    except Exception as e:
        logger.error(f"搜索QA文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/list", response_model=BaseResponse, summary="获取QA文档列表")
async def list_qa(
        kb_id: Optional[int] = None,
        category_1: Optional[str] = None,
        category_2: Optional[str] = None,
        point_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10,
        session: Session = Depends(get_session)
):
    """获取QA文档列表"""
    try:
        # 构建查询条件
        conditions = [QADocument.is_delete == False]

        if kb_id is not None:
            conditions.append(QADocument.kb_id == kb_id)
        if category_1:
            conditions.append(QADocument.category_1 == category_1)
        if category_2:
            conditions.append(QADocument.category_2 == category_2)
        if point_id is not None:
            conditions.append(QADocument.point_id == point_id)
        if is_active is not None:
            conditions.append(QADocument.is_active == is_active)

        # 计算总数
        count_statement = select(QADocument).where(and_(*conditions))
        total = len(session.exec(count_statement).all())

        # 分页查询
        offset = (page - 1) * page_size
        statement = (
            select(QADocument)
            .where(and_(*conditions))
            .order_by(QADocument.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        qa_docs = session.exec(statement).all()
        items = [QAResponse.model_validate(doc).model_dump() for doc in qa_docs]

        return BaseResponse(
            code=200,
            message="获取成功",
            data={
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )
    except Exception as e:
        logger.error(f"获取QA文档列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/batch/delete", response_model=BaseResponse, summary="批量删除QA文档")
async def batch_delete_qa(request: QABatchDeleteRequest, session: Session = Depends(get_session)):
    """批量软删除QA文档"""
    try:
        statement = select(QADocument).where(
            and_(
                QADocument.id.in_(request.ids),
                QADocument.is_delete == False
            )
        )
        qa_docs = session.exec(statement).all()

        if not qa_docs:
            raise HTTPException(status_code=404, detail="未找到要删除的QA文档")

        for qa_doc in qa_docs:
            qa_doc.is_delete = True
            qa_doc.update_at = datetime.now(ZoneInfo("Asia/Shanghai"))
            session.add(qa_doc)

        session.commit()

        logger.info(f"批量删除QA文档成功，数量: {len(qa_docs)}")
        return BaseResponse(
            code=200,
            message="批量删除成功",
            data={"deleted_count": len(qa_docs)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除QA文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")


@router.post("/{qa_id}/update", response_model=BaseResponse, summary="更新QA文档")
async def update_qa(qa_id: int, request: QAUpdateRequest, session: Session = Depends(get_session)):
    """更新QA文档"""
    try:
        statement = select(QADocument).where(
            and_(QADocument.id == qa_id, QADocument.is_delete == False)
        )
        qa_doc = session.exec(statement).first()

        if not qa_doc:
            raise HTTPException(status_code=404, detail="QA文档不存在")

        # 更新字段
        update_data = request.dict(exclude_unset=True)
        if "question" in update_data and update_data["question"]:
            # 如果更新了问题，重新生成向量
            update_data["embedding"] = get_text_embedding(update_data["question"])

        for field, value in update_data.items():
            setattr(qa_doc, field, value)

        qa_doc.update_at = datetime.now(ZoneInfo("Asia/Shanghai"))
        session.add(qa_doc)
        session.commit()

        logger.info(f"更新QA文档成功，ID: {qa_id}")
        return BaseResponse(
            code=200,
            message="更新成功",
            data={"id": qa_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新QA文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post("/{qa_id}/delete", response_model=BaseResponse, summary="删除QA文档")
async def delete_qa(qa_id: int, session: Session = Depends(get_session)):
    """软删除一个QA文档"""
    try:
        statement = select(QADocument).where(
            and_(QADocument.id == qa_id, QADocument.is_delete == False)
        )
        qa_doc = session.exec(statement).first()

        if not qa_doc:
            raise HTTPException(status_code=404, detail="QA文档不存在")

        qa_doc.is_delete = True
        qa_doc.update_at = datetime.now(ZoneInfo("Asia/Shanghai"))
        session.add(qa_doc)
        session.commit()

        logger.info(f"删除QA文档成功，ID: {qa_id}")
        return BaseResponse(
            code=200,
            message="删除成功",
            data={}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除QA文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
