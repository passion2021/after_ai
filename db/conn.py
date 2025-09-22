from typing import List
import numpy as np
from sqlmodel import select
from sqlmodel import Session
from libs.easy_llm.llm.embed import get_text_embedding
from orm.schema import engine, QADocument, Document
from loguru import logger
import json
from utils.common import timing


class VectorDB:

    def retrieve(self, query: str, document_ids: List[int] | None = None, category: str | None = None,
                 top_k: int = 5) -> List[dict]:
        # 文本转向量
        query_vector = self.embedding(query)
        logger.info(f"retrieve input - document_ids:{document_ids}, category:{category}")
        if document_ids and not category:  # ✅ 只传 document_ids
            document_ids = document_ids
        elif document_ids and category:  # ✅ 两者都传
            document_ids = list(set(document_ids + self.get_document_ids(category)))
        elif not document_ids and category:  # ✅ 只传 category
            document_ids = self.get_document_ids(category)
        elif not document_ids and not category:  # ✅ 都没传
            document_ids = [1]  # 默认值
        logger.info(f"参与查询的文档id：{document_ids}")
        # 向量检索
        results = self.select_db(query_vector, document_ids, top_k)
        # 过滤无效结果
        results = self.post_process(results)
        return results

    def get_document_ids(self, category: str) -> List[int]:
        """根据传入的分类，查询出对应的文档id"""
        with Session(engine) as session:
            statement = (
                select(Document.id)
                .where(Document.category == category, Document.enabled == True)
            )
            results = session.exec(statement).all()
            return results

    @staticmethod
    def embedding(text):
        return  get_text_embedding(text)

    @timing
    def select_db(self, query_vector: np.ndarray, document_ids: List[int], top_k: int = 5):
        with Session(engine) as session:
            stmt = (
                select(
                    QADocument,
                    QADocument.embedding.l2_distance(query_vector).label("distance")
                )
                .where(QADocument.document_id.in_(document_ids))  # 🔹 多个 ID 条件
                .order_by(QADocument.embedding.l2_distance(query_vector))
                .limit(top_k)
            )

            results = session.exec(stmt).all()
            retrieve_result = []

            for document, distance in results:
                data = {
                    'question': document.question,
                    'answer': document.answer,
                    # 'distance': distance,
                    'score': self.distance_to_score(distance)
                }

                retrieve_result.append(data)
            logger.info(f"检索结果： \n{json.dumps(retrieve_result, ensure_ascii=False, indent=4)}")
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
    qa_pairs = [{"question": "这款内衣是什么材质的？安全吗？",
                 "answer": "我们的内衣采用 A 类婴幼儿标准纯棉面料，无甲醛、无荧光剂，通过国家质检认证，柔软亲肤，对孩子娇嫩肌肤零刺激，家长可放心选购。"},
                {"question": "内衣会掉色吗？",
                 "answer": "我们的内衣采用环保活性印染工艺，色牢度达到国家标准，正常洗涤不会出现掉色情况，您可以先单独冷水轻柔洗涤一次，观察有无轻微浮色。"}]

    for qa in qa_pairs:
        vector_db.retrieve(qa['question'], document_ids=[1, 12])
