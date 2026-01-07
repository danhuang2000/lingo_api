
import textwrap
from pydantic import BaseModel

from agent.client.ai_client import AiClient
from .base_agent import BaseAgent


BASE_TUTOR_PROMPT = """
Rules:
- Be concise.
- Never overwhelm the learner.
- Correct only ONE mistake at a time.
- Prefer examples over explanations.
- Adapt difficulty to learner confidence.
- Speak naturally, like a human tutor.

If explaining:
- Use the learner's native language briefly.
- Then repeat the correct sentence in the target language.
"""
# Always end with a follow-up question.


MODE_PROMPTS = {
    "correction": """
The learner made a mistake.
1. Gently correct the sentence.
2. Explain the mistake briefly.
3. Ask them to repeat the corrected sentence.
""",

    "repetition": """
The learner seems unsure.
1. Repeat the sentence slowly.
2. Break it into chunks.
3. Ask them to repeat.
""",

    "explanation": """
The learner is struggling.
1. Explain the grammar simply.
2. Give ONE example.
3. Ask a very easy follow-up question.
""",

    "nextQuestion": """
Continue the conversation naturally.
Increase difficulty slightly if appropriate.
""",

    "encouragement": """
Encourage the learner.
Praise effort.
Then ask an easy question.
"""
}


class BaseTutorAgent(BaseAgent):

    class TutorSessionState(BaseModel):
        user_uuid: str
        course_id: int
        
        consecutive_errors: int = 0
        last_confidence: float = 1.0
        weak_grammar: dict[str, int] = {}
        weak_vocab: dict[str, int] = {}


    def __init__(self, client: AiClient, instructions: str):
        super().__init__(client, instructions)
        

    @staticmethod
    def build_prompt(
        task_description: str,
        output_instruction: str,
        mode: str,
        user_text: str,
        session: TutorSessionState
    ) -> str:
        prompt = f"""
            {task_description}
            {BASE_TUTOR_PROMPT}

            Current mode: {mode}
            Learner confidence: {session.last_confidence}
            Consecutive errors: {session.consecutive_errors}

            {MODE_PROMPTS[mode]}

            {output_instruction}
        """

        return textwrap.dedent(prompt)