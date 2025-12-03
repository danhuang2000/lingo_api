
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from pydantic import BaseModel
from requests_toolbelt.multipart import MultipartEncoder
from sqlmodel import Session, select

from agent import VoiceTutorAgent, StubClient
from entity import Subject, Tutor, User
from audio import TextToSpeech
from utils import get_app_logger


logger = get_app_logger(__name__)

class TutoringService:
    class AskTutorRequest(BaseModel):
        instruction_language_code: str
        language_code: str
        question: str


    class AskTutorResponse(BaseModel):
        answer: str

    class DualLangRequest(BaseModel):
        user_uuid: str
        course_id: int
        text_1: str
        text_2: str


    class AiResponseFragment(BaseModel):
        lang: str
        text: str
    class AiResponse(BaseModel):
        question: ["TutoringService.AiResponseFragment"]
        answer: ["TutoringService.AiResponseFragment"]


    def __init__(self, session: Session):
        self.session = session


    def askQuestion(self, request: AskTutorRequest) -> AskTutorResponse:
        from agent import StubClient, QnAAgent
        from entity import InstructionLanguage

        # client = OpenAiClient()
        # client = OllamaClient()
        client = StubClient()
        instruction_language = InstructionLanguage(code=request.instruction_language_code, name="Instruction Language")
        language = InstructionLanguage(code=request.language_code, name="Language")
        agent = QnAAgent(client, primary_language=instruction_language, secondary_language=language)
        answer = agent.ask_ai(request.question)
        return TutoringService.AskTutorResponse(answer=answer)


    def askQuestionWithAudio(self, request: "TutoringService.DualLangRequest"):
        try:
            # TODO 
            logger.info(f"user_uuid={request.user_uuid} course_id={request.course_id}\n{request.text_1}\n{request.text_2}")

            stmt = select(User).where(User.uuid == request.user_uuid)
            user = self.session.exec(stmt).first()
            if user is None:
                raise ValueError(f"{request.user_uuid} user not found.")

            course = user.courses.filter(Subject.id == request.course_id).first()
            if course is None:
                raise ValueError(f"Course id {request.course_id} not found for user {request.user_uuid}.")

            subj = course.course.subject
            level = course.course.level
            inst_lang = course.instruction_language

            stmt = select(Tutor).where(Tutor.id == user.course.tutor_id)
            tutor = self.session.exec(stmt).first()
            if tutor is None:
                raise ValueError(f"Tutor id {request.tutor_id} not found.")

            agent = VoiceTutorAgent(subject=subj, level=level, tutor=tutor, inst_lang=inst_lang)
            ai_request = '{"tts1:{"lang":"' + inst_lang.code.split("-")[0] + '","text":"' + request.text_1 + '"},"' + \
                        '{tts2:{"lang":"' + subj.code.split("-")[0] + '","text":"' + request.text_2 + '"}}'
            result = agent.ask_ai(ai_request)
            logger.info(f"AI Answer: {result}")
            ai_result = TutoringService.AiResponse.model_validate_json(result)
            inst_lang_code = inst_lang.code.split("-")[0]
            subject_lang_code = subj.code.split("-")[0]

            answer = self._convertAiResult(ai_result.answer)

            # Synthesize audio and phonemes
            audios = TextToSpeech.synthesize(
                text=answer,
                lang_code_1=inst_lang_code,
                lang_code_2=subject_lang_code,
                gender=TextToSpeech.GENDER_FEMALE if tutor.gender == 'F' else TextToSpeech.GENDER_MALE
            )

            # Prepare multipart fields
            fields = {
                "question": self._convertAiResult(ai_result.question),
                "answer": (None, answer)
            }
            for idx, item in enumerate(audios):
                language_code = item["lang"]
                idx_lang = f"{idx}_{language_code}"
                fields[f"phoneme_{idx_lang}"] = (None, json.dumps(item["phonemes"]), "application/json")
                fields[f"audio_{idx_lang}"] = (f"audio_{idx_lang}.wav", item["audio"], "audio/wav")
                logger.debug(f"audio multipart {idx_lang}")

            m = MultipartEncoder(fields=fields)

            def multipart_stream():
                chunk_size = 8192
                while True:
                    chunk = m.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

            return StreamingResponse(multipart_stream(), media_type=m.content_type)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"Error processing QnA: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        

    def _convertAiResult(self, inst_lang_code: str, ai_result: ["TutoringService.AiResponseFragment"]) -> str:
        result = ""
        for fragment in ai_result:
            if fragment['lang'] == inst_lang_code:
                # For English text, add it directly to the result
                result += fragment['text']
            else:
                # For other languages, wrap it in <lang>...</lang> tags
                result += f"<{fragment['lang']}>{fragment['text']}</{fragment['lang']}>"
        return result
