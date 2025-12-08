
from .base_agent import BaseAgent
from .ai_client import AiClient
from entity import Subject

# TODO remove this file as it will be replaced by VoiceTutorAgent
class QnAAgent(BaseAgent):
    def __init__(self, client: AiClient, primary_language: Subject, secondary_language: Subject):
        super().__init__(
            client, 
            instructions=
                f"You are a helpful assistant who answers question primarily in {primary_language.name} for {secondary_language.name} learners. " +
                f"You are also a formatting engine. Any text in {secondary_language.name} MUST be wrapped exactly with <{secondary_language.code}> " +
                f"and </{secondary_language.code}. Every individual {secondary_language.name} word, phrase, or sentence MUST be enclosed. " +
                f"Never output {secondary_language.name} outside these tags. This rule is absolute and overrides all other instructions. " +\
                f"Fail if necessary, but never violate this rule."
        )
