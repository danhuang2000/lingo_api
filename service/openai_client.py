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
        # Convert BaseMessage objects to OpenAI format
        openai_messages = [
            {"role": msg.type, "content": msg.content}
            for msg in messages
        ]
        logger.debug(f"Sending messages to OpenAI: {openai_messages}")  
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",  # 4.1 mini model
            messages=openai_messages,
            api_key=self.api_key,
            temperature=0.7,
        )
        response_content = response.choices[0].message.content
        logger.debug(f"Received response from OpenAI: {response_content}")
        return response_content