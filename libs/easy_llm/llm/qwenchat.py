from typing import List, Dict, Generator
import dashscope
from libs.easy_llm.llm.base import ModelApi


class QwenChat(ModelApi):

    def stream(self, messages: List[Dict]) -> Generator[str, None, None]:
        responses = dashscope.Generation.call(
            api_key=self.api_key,  # 建议从 self.api_key 取，而不是写死
            model=self.model or "qwen-plus",
            messages=messages,
            result_format='message',
            stream=True,
            incremental_output=True
        )
        for response in responses:
            # 检查是否有 choices
            if (
                hasattr(response, "output")
                and response.output is not None
                and "choices" in response.output
                and len(response.output["choices"]) > 0
            ):
                choice = response.output["choices"][0]
                if "message" in choice and choice["message"].get("content"):
                    yield choice["message"]["content"]
            else:
                print("⚠️ Warning: Empty response chunk:", response)