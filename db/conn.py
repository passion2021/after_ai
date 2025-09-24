from typing import List
import numpy as np
from sqlmodel import select
from sqlmodel import Session
from libs.easy_llm.llm.embed import get_text_embedding
from orm.schema import engine, QADocument
from loguru import logger
import json
from utils.common import timing


class VectorDB:

    def retrieve(self, query: str, kb_id: int, point_id: int | None = None, top_k: int = 5) -> List[dict]:
        """
        向量检索QA文档
        
        Args:
            query: 查询文本
            kb_id: 知识库ID（必填）
            point_id: 中台ID（非必填）
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        # 文本转向量
        query_vector = self.embedding(query)
        logger.info(f"retrieve input - kb_id:{kb_id}, point_id:{point_id}, query:{query[:50]}...")
        
        # 向量检索
        results = self.select_db(query_vector, kb_id, point_id, top_k)
        # 过滤无效结果
        results = self.post_process(results)
        logger.info(f"检索结果： \n{json.dumps(results, ensure_ascii=False, indent=4)}")
        return results


    @staticmethod
    def embedding(text):
        return  get_text_embedding(text)

    @timing
    def select_db(self, query_vector: np.ndarray, kb_id: int, point_id: int | None = None, top_k: int = 5):
        """
        从数据库中进行向量检索
        
        Args:
            query_vector: 查询向量
            kb_id: 知识库ID
            point_id: 中台ID（可选）
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        with Session(engine) as session:
            # 构建查询条件
            conditions = [
                QADocument.kb_id == kb_id,
                QADocument.is_delete == False,
                QADocument.is_active == True
            ]
            
            # 如果指定了point_id，添加该条件
            if point_id is not None:
                conditions.append(QADocument.point_id == point_id)
            
            stmt = (
                select(
                    QADocument,
                    QADocument.embedding.l2_distance(query_vector).label("distance")
                )
                .where(*conditions)
                .order_by(QADocument.embedding.l2_distance(query_vector))
                .limit(top_k)
            )

            results = session.exec(stmt).all()
            retrieve_result = []

            for document, distance in results:
                data = {
                    'question': document.question,
                    'answer': document.answer,
                    'score': self.distance_to_score(distance)
                }

                retrieve_result.append(data)
            return retrieve_result

    @staticmethod
    def distance_to_score(distance: float, max_distance: float = 1.0) -> float:
        """
        将 L2 距离映射为 [0, 1] 的相似度分数，距离越小，相似度越高。

        :param distance: L2 距离（越小越相似）
        :param max_distance: 距离上限，超过这个值的距离会映射为相似度 0
        :return: 相似度得分，0.0 ~ 1.0
        """
        if distance >= max_distance:
            return 0.0
        return round(1 - (distance / max_distance), 4)

    @staticmethod
    def post_process(retrieve_result):
        return [item for item in retrieve_result if item['score'] > 0.0]


vector_db = VectorDB()
if __name__ == '__main__':
    # 测试向量检索
    test_queries = [
        "机器人不回复了？",
    ]
    
    for query in test_queries:
        print(f"\n🔍 测试查询: {query}")
        results = vector_db.retrieve(query, kb_id=1, top_k=3)
        print(f"找到 {len(results)} 个相关结果")
