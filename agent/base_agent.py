from utils import get_app_logger
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from .ai_client import AiClient

logger = get_app_logger(__name__)


class BaseAgent:
    def __init__(self, client: AiClient, instructions: str):
        self.client = client
        self.messages = []
        self.system_message = SystemMessage(content=instructions)


    def ask_ai(self, question: str) -> str:
        messages = [
            self.system_message,
            HumanMessage(content=question)
        ]
        logger.debug("Messages sent to AI:")
        for msg in messages:
            logger.debug(f"  {msg}")
        response = self.client.ask_ai(messages)
        logger.debug(f"AI Response: {response}")
        return response