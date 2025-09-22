import asyncio
import traceback
from typing import List, Union, Optional, Any
from pydantic import BaseModel

from ..msg import MsgList, BaseMsg
from ..utils.print_style import *
from abc import ABC, abstractmethod


class OneQuestion(BaseModel):
    value: str


class RawMessages(BaseModel):
    value: List[dict]


class ListQuestions(BaseModel):
    value: List[str]


class ListRawMessages(BaseModel):
    value: List[List[dict]]


class ModelApiBase(ABC):
    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            **kwargs: Any
    ):
        self.model = model
        self.api_key = api_key
        self.kwargs = kwargs

    @abstractmethod
    def stream(self, messages):
        pass


class ModelApi(ModelApiBase):

    def chat_complete(
            self,
            messages: Union[str, List[dict]]
    ) -> str:
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
            return "".join(self.stream(messages))
        elif isinstance(messages, list):
            return "".join(self.stream(messages))

    def chat_stream(self, messages: Union[str, List[dict]]):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
            return self._log_stream(self.stream(messages))
        elif isinstance(messages, list):
            return self._log_stream(self.stream(messages))

    def _log_stream(self, generator):
        text = ''
        prefix_font.print(f"{self.__class__.__name__}:")
        for r in generator:
            text += r
            ai_font.print(r)
        print()
        return text


class AsyncModelApi(ModelApiBase):
    def __init__(self, max_concurrent_tasks: int = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = []
        self.results = []
        self.max_concurrent_tasks = max_concurrent_tasks  # 最大并发任务数

    def wrapper(self, messages: Union[str, List[dict]]):
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        else:
            return messages

    async def process_batches(self, messages_list: Union[ListQuestions, ListRawMessages]):
        for index, messages in enumerate(messages_list.value):
            messages = self.wrapper(messages)
            self.tasks.append(asyncio.create_task(self.fetch_data(messages, index)))
            # 等待当前批次所有任务完成，并将结果收集到 results
            if len(self.tasks) >= self.max_concurrent_tasks:
                self.results.extend(await asyncio.gather(*self.tasks))
                self.tasks = []
        if self.tasks:
            # 处理最后剩余的请求
            self.results.extend(await asyncio.gather(*self.tasks))
        return self.results

    async def fetch_data(self, messages, index):
        try:
            result = "".join([text async for text in self.stream(messages)])
            prefix_font.print(f"{self.__class__.__name__}-{index}:")
            ai_font.print(f"{result}\n")
            return result
        except Exception as e:
            error_font.print(traceback.format_exc())

    @staticmethod
    def validate_type(messages) -> Union[RawMessages, ListQuestions, ListRawMessages]:
        if isinstance(messages, MsgList):
            return RawMessages(value=messages.to_json())
        if isinstance(messages, str):
            return RawMessages(value=[{"role": "user", "content": messages}])
        for data_type in [RawMessages, ListQuestions, ListRawMessages]:
            try:
                return data_type(value=messages)
            except Exception:
                pass
        raise ValueError(f"Unsupported input type: {type(messages)}")

    async def chat_complete(self,
                            messages: Union[str, List[dict], List[str], List[List[dict]], MsgList[BaseMsg]],
                            stream=False
                            ):
        """
        支持以下输入格式：

        # 单条消息
        "query1"
        [{"role": "user", "content": "query1"}, {"role": "user", "content": "query2"}]

        # 多条消息
        ["query1","query2"]
        [[{"role": "user", "content": "query1"}], [{"role": "user", "content": "query2"}]]
        """
        messages = self.validate_type(messages)
        if isinstance(messages, RawMessages):
            if stream:
                return self.stream(messages.value)
            else:
                return "".join([text async for text in self.stream(messages.value)])
        else:
            return await self.process_batches(messages)
