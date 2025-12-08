import os
from langchain.schema import BaseMessage
import openai

from utils import get_app_logger
from .ai_client import AiClient

logger = get_app_logger(__name__)

class OpenAiClient(AiClient):
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")


    def ask_ai(self, messages: list[BaseMessage]) -> str:
        request = self._create_request(messages, stream=False)
        response = openai.chat.completions.create(**request)

        response_content = response.choices[0].message.content
        logger.debug(f"Received response from OpenAI: {response_content}")
        return response_content
        

    def ask_ai_stream(self, messages: list[BaseMessage]):
        request = self._create_request(messages, stream=True)
        response = openai.chat.completions.create(**request)

        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content


    def _create_request(self, messages: list[BaseMessage], stream: bool = False) -> dict:
        # Helper method to create OpenAI request payload
        openai_messages = [
            {"role": msg.type, "content": msg.content}
            for msg in messages
        ]
        logger.debug(f"Sending messages to OpenAI: {openai_messages}")  
        return {
            "model": "gpt-4.1-mini",
            "messages": openai_messages,
            "temperature": 0.7,
            "stream": stream,
        }