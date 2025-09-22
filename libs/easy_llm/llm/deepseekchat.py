from typing import List, Generator, Optional, Any, Dict
from openai import OpenAI, AsyncOpenAI
from ..llm.base import ModelApi, AsyncModelApi


class DeepSeekChat(ModelApi):

    def stream(
            self,
            messages: List[Dict[str, str]],
            think: bool = False,
    ) -> Generator[str, None, None]:
        client = OpenAI(api_key=self.api_key, **self.kwargs)
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
            if think:
                if chunk.choices[0].delta.reasoning_content:
                    yield chunk.choices[0].delta.reasoning_content


class AsyncDeepSeekChat(AsyncModelApi):

    async def stream(self, messages, think: bool = False, ):
        client = AsyncOpenAI(api_key=self.api_key, **self.kwargs)
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        async for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
            if think:
                if chunk.choices[0].delta.reasoning_content:
                    yield chunk.choices[0].delta.reasoning_content
