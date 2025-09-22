from ollama import Client
from .base import ModelApiBase

client = Client(host='http://192.168.10.174:11434')


class OllamaChat(ModelApiBase):
    def stream(self, messages):
        for chunk in client.chat(model=self.model, messages=messages, stream=True):
            yield chunk.message.content
