from langchain.schema import BaseMessage

class AiClient:
    def ask_ai(self, messages: list[BaseMessage]) -> str:
       raise NotImplementedError("Subclasses must implement ask_ai.")

    def ask_ai_stream(self, messages: list[BaseMessage]):
        raise NotImplementedError("Subclasses must implement ask_ai_stream.")