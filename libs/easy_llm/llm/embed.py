import os
from openai import OpenAI
from dotenv import load_dotenv

# 读取 .env 中的 DASHSCOPE_API_KEY
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 百炼（DashScope）的兼容 OpenAI 接口地址
)

def get_text_embedding(text: str, model: str = "text-embedding-v4", dimensions: int = 1024) -> list[float]:
    """
    使用 DashScope 的 OpenAI 兼容接口获取文本嵌入向量。

    参数:
    - text (str): 输入文本
    - model (str): 嵌入模型名称（默认使用 text-embedding-v4）
    - dimensions (int): 向量维度（仅支持 v3/v4 模型）

    返回:
    - list[float]: 向量结果
    """
    response = client.embeddings.create(
        model=model,
        input=text,
        dimensions=dimensions,
        encoding_format="float"
    )
    return response.data[0].embedding  # 返回嵌入向量

# 🧪 示例调用
if __name__ == "__main__":
    sample_text = "衣服的质量杠杠的，很漂亮，不枉我等了这么久啊，喜欢，以后还来这里买"
    embedding = get_text_embedding(sample_text)
    print(f"Embedding length: {len(embedding)}")
    print(embedding[:10])  # 打印前10个元素看看
