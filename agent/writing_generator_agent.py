
import textwrap
from .base_agent import BaseAgent
from .client.openai_client import OpenAiClient
from .client.stub_client import StubClient


SYSTEM_PROMPT = """
You are a language-learning content generator.

Rules:
- Generate ONE sentence or short paragraph.
- Grammar and vocabulary must match the ACTFL level.
- Avoid synonyms that could create multiple correct translations.
- Use simple, canonical word order.
- Output ONLY valid JSON.
"""


class WritingGeneratorAgent(BaseAgent):
    def __init__(self):
        client = StubClient()
        # client = OpenAiClient()
        super().__init__(client=client, instructions=SYSTEM_PROMPT)
 

    def build_writing_prompt(target_language, instruction_language, topic, actfl_level):
        prompt = f"""
            Task:
            Create a writing (translation-building) exercise.

            Parameters:
            - Target language: {target_language}
            - Instruction language: {instruction_language}
            - Topic: {topic}
            - ACTFL level: {actfl_level}

            Requirements:
            1. Generate one sentence (or 2 short sentences max) in the instruction language.
            2. Provide ONE correct translation in the target language.
            3. Split the translation into individual words.
            4. Add 2–4 extra distractor words.
            5. Shuffle all words.
            6. Ensure only ONE correct word order is valid.

            Return JSON in this exact format:

            {{
            "prompt_text": "...",
            "correct_translation": "...",
            "word_bank": ["...", "...", "..."]
            }}
        """
        return textwrap.dedent(prompt)
