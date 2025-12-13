from utils import get_app_logger
from langchain.schema import BaseMessage
from .client.ai_client import AiClient


logger = get_app_logger(__name__)


class BaseAgent:
    def __init__(self, client: AiClient, instructions: str):
        self.client = client
        self.hist_messages = []
        self.system_message = BaseMessage(content=instructions, type="system")


    def append_assistant_message(self, message: str):
        self.hist_messages.append(BaseMessage(content=message, type="assistant"))


    def append_user_message(self, message: str):
        self.hist_messages.append(BaseMessage(content=message, type="user"))

    
    def clear_history_messages(self):
        self.hist_messages = []


    def ask_ai(self, question: str) -> str:
        user_message = BaseMessage(content=question, type="user")
        messages = [self.system_message] + self.hist_messages + [user_message]
        response = self.client.ask_ai(messages)
        logger.debug(f"AI Response: {response}")
        return response

    
    def ask_ai_stream(self, question: str):
        user_message = BaseMessage(content=question, type="user")
        messages = [self.system_message] + self.hist_messages + [user_message]
        logger.debug("AI response streaming...")
        for chunk in self.client.ask_ai_stream(messages):
            yield chunk
