from openai import OpenAI, AsyncOpenAI
from ..llm.base import ModelApi, AsyncModelApi


class OpenAIChat(ModelApi):

    def stream(self, messages):
        base_url = self.kwargs.get("base_url", "https://sg.uiuiapi.com/v1")
        client = OpenAI(api_key=self.api_key, base_url=base_url, **self.kwargs)
        stream = client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            **self.kwargs
        )
        for chunk in stream:
            if not chunk.choices or len(chunk.choices) == 0:
                print("⚠️ Warning: Empty choices received. Skipping this chunk.")
                continue  # 跳过空 chunk
            if hasattr(chunk.choices[0], "delta") and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content



class AsyncOpenAIChat(AsyncModelApi):

    async def stream(self, messages):
        base_url = self.kwargs.get("base_url", "https://sg.uiuiapi.com/v1")
        client = AsyncOpenAI(api_key=self.api_key, base_url=base_url, **self.kwargs)
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        async for chunk in response:
            if not chunk.choices or len(chunk.choices) == 0:
                print("⚠️ Warning: Empty choices received. Skipping this chunk.")
                continue  # 跳过空 chunk
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
