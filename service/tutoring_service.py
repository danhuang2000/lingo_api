
from pydantic import BaseModel
from sqlmodel import Session


class TutoringService:

    class AskTutorRequest(BaseModel):
        instruction_language_code: str
        language_code: str
        question: str


    class AskTutorResponse(BaseModel):
        answer: str


    def __init__(self, session: Session):
        self.session = session


    async def askQuestion(self, request: AskTutorRequest) -> AskTutorResponse:
        from agent import StubClient, QnAAgent
        from entity import InstructionLanguage

        # client = OpenAiClient()
        # client = OllamaClient()
        client = StubClient()
        instruction_language = InstructionLanguage(code=request.instruction_language_code, name="Instruction Language")
        language = InstructionLanguage(code=request.language_code, name="Language")
        agent = QnAAgent(client, primary_language=instruction_language, secondary_language=language)
        answer = agent.ask_ai(request.question)
        return self.AskTutorResponse(answer=answer)
