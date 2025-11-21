from langchain_ollama import ChatOllama
from langchain.schema import BaseMessage
from .ai_client import AiClient

class OllamaClient(AiClient):
    __llm = ChatOllama(
        model="mistral:7b",   # e.g. "llama3", "mistral", "phi3", etc.
        base_url="http://localhost:11434",  # Ollama’s default API endpoint
        temperature=0.7,
    )

    def ask_ai(self, messages: list[BaseMessage]) -> str:
        response = OllamaClient.__llm.invoke(messages)
        return response.content

