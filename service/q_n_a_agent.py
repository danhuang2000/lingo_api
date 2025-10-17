
from .base_agent import BaseAgent
from .ai_client import AiClient
from entity import Language

class QnAAgent(BaseAgent):
    def __init__(self, client: AiClient, primary_language: Language, secondary_language: Language):
        super().__init__(
            client, 
            instructions=
                f"You are a helpful assistant who answers question primarily in {primary_language.name} for {secondary_language.name} learners." +
                f" If the answer has text in {secondary_language.name}, each of such text segment must start with <{secondary_language.code} and " +
                f"end with </{secondary_language.code}>." +
                " Be brief and concise."
        )
