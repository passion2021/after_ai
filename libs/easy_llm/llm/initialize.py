import os
from .ollamachat import OllamaChat
from .qwenchat import QwenChat
from ..llm.deepseekchat import DeepSeekChat, AsyncDeepSeekChat
from ..llm.openaichat import OpenAIChat, AsyncOpenAIChat

siliconflow_base_url = "https://api.siliconflow.cn/v1"
deepseek_chat = DeepSeekChat(model="deepseek-chat", api_key='sk-86b1e7e75d25419bac07fa0a8d6eb10c',base_url='https://api.deepseek.com/v1')
async_deepseek_chat = AsyncDeepSeekChat(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
openai_chat = OpenAIChat(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
async_openai_chat = AsyncOpenAIChat(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), max_concurrent_tasks=10)
deepseek_v3_chat = DeepSeekChat(model="deepseek-ai/DeepSeek-V3",
                                api_key="sk-fzpiejbrcwyfsodzavmrvbnvobyifnczodjvbiktcafcmapo",
                                base_url=siliconflow_base_url)

deepseek_r1_chat = DeepSeekChat(model="deepseek-ai/DeepSeek-R1",
                                api_key="sk-fzpiejbrcwyfsodzavmrvbnvobyifnczodjvbiktcafcmapo",
                                base_url=siliconflow_base_url)
async_deepseek_v3_chat = AsyncDeepSeekChat(model="deepseek-ai/DeepSeek-V3",
                                           api_key="sk-fzpiejbrcwyfsodzavmrvbnvobyifnczodjvbiktcafcmapo",
                                           base_url=siliconflow_base_url)
async_deepseek_r1_chat = AsyncDeepSeekChat(model="deepseek-ai/DeepSeek-R1",
                                           api_key="sk-fzpiejbrcwyfsodzavmrvbnvobyifnczodjvbiktcafcmapo",
                                           base_url=siliconflow_base_url)
gemma3_4b = OllamaChat(model='gemma3:4b')
qwen2_5_7b = OllamaChat(model='qwen2.5:7b')
qwen2_5_14b = OllamaChat(model='qwen2.5:14b')
qwen_chat = QwenChat(model="qwen-plus", api_key="sk-fc4c928841ba490589e1e60b9f7a86d3")