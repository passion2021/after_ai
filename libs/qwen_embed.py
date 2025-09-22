from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union, Optional
from loguru import logger

class QwenEmbedder:
    """本地加载 Qwen Embedding 模型测试使用"""
    def __init__(self, model_path: str):
        self.model = SentenceTransformer(model_path,device="cuda:0")

    def get_text_embedding(
            self,
            texts: Union[str, List[str]],
            prompt_name: Optional[str] = None,
            convert_to_numpy: bool = True
    ) -> np.ndarray:
        """
        获取文本的 embedding 向量。

        参数:
        - texts: 单个字符串或字符串列表
        - prompt_name: 可选，例如 "query"。如果提供，则会使用模型内置的 prompt。
        - convert_to_numpy: 是否返回 numpy 格式

        返回:
        - np.ndarray: shape=(len(texts), hidden_size)
        """
        if isinstance(texts, str):
            texts = [texts]

        kwargs = {"convert_to_numpy": convert_to_numpy}
        if prompt_name:
            kwargs["prompt_name"] = prompt_name

        return self.model.encode(texts, **kwargs)


def warmup():
    qwen_embedder = QwenEmbedder(r"E:\ai-eb\models\Qwen3-Embedding-0.6B")
    qwen_embedder.get_text_embedding(["1","1"], prompt_name="query")
    logger.info("QwenEmbedder warmup success")
    return qwen_embedder


qwen_embedder = warmup()

if __name__ == '__main__':
    embedder = QwenEmbedder(r"E:\ai-eb\models\Qwen3-Embedding-0.6B")
    # 有 prompt_name（query 类型）
    query_emb = embedder.get_text_embedding(["What is the capital of China?"], prompt_name="query")
    # 没有 prompt_name（文档类型）
    doc_emb = embedder.get_text_embedding(["Beijing is the capital of China."])
    # 输出 shape
    print("Query embedding shape:", query_emb.shape)
    print("Doc embedding shape:", doc_emb.shape)
