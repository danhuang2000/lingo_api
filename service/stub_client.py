from langchain.schema import BaseMessage
from .ai_client import AiClient

class StubClient(AiClient):
    def ask_ai(self, messages: list[BaseMessage]) -> str:
        return "Buy Bobby a puppy. <zh>练习中文发音</zh> My mom may know."