
import textwrap
from .base_agent import BaseAgent
from .client.openai_client import OpenAiClient
from .client.stub_client import StubClient


SYSTEM_PROMPT = """
You are a language-learning content generator.

Rules:
- Generate content ONLY in the target language.
- Keep sentences short and clear.
- Vocabulary and grammar must match the ACTFL level.
- Do NOT explain anything.
- Do NOT include translations.
- Avoid idioms unless ACTFL level is Intermediate Mid or higher.

Output must be valid JSON.
"""


class ListeningGeneratorAgent(BaseAgent):
    def __init__(self):
        client = StubClient() if BaseAgent.use_stub_client() else OpenAiClient()
        super().__init__(client=client, instructions=SYSTEM_PROMPT)
 

    def build_listening_prompt(topic, actfl_level, target_language):
        prompt = f"""
            Task:
            Create a short listening comprehension exercise.

            Parameters:
            - Topic: {topic}
            - ACTFL level: {actfl_level}
            - Target language: {target_language}

            Requirements:
            1. One short paragraph (4–6 sentences).
            2. Exactly 2 or 3 multiple-choice questions.
            3. Each question must test understanding of the passage.
            4. Each question must have 3 options.
            5. Clearly mark the correct option using an index.

            Return JSON with this structure:

            {{
            "passage": "...",
            "questions": [
                {{
                "question": "...",
                "options": ["...", "...", "..."],
                "correct_index": 0
                }}
            ]
            }}
            """
        return textwrap.dedent(prompt)
