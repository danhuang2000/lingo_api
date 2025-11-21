from langchain.schema import BaseMessage

class AiClient:
    def ask_ai(self, messages: list[BaseMessage]) -> str:
       raise NotImplementedError("Subclasses must implement ask_ai.")
