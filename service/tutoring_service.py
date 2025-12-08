
from __future__ import annotations
import json
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from typing import List
from requests_toolbelt.multipart import MultipartEncoder
from sqlmodel import Session, select

from agent import VoiceTutorAgent, QnAAgent
from agent.client import OllamaClient, OpenAiClient, StubClient
from entity import User, Subject, SubjectLevel, InstructionLanguage, Tutor
from audio import TextToSpeech
from utils import get_app_logger


logger = get_app_logger(__name__)

class TutoringService:
    class AskTutorRequest(BaseModel):
        instruction_language_code: str
        language_code: str
        question: str


    class DualLangRequest(BaseModel):
        user_uuid: str
        course_id: int
        text_1: str
        text_2: str


    class AiResponseFragment(BaseModel):
        lang: str
        text: str

    class AiResponse(BaseModel):
        question: List[TutoringService.AiResponseFragment]
        answer: List[TutoringService.AiResponseFragment]


    def __init__(self, session: Session):
        self.session = session


    def askForTextResponse(self, request: AskTutorRequest):
        # client = OpenAiClient()
        # client = OllamaClient()
        client = StubClient()
        stmt = select(Subject).where(Subject.code.in_([request.instruction_language_code, request.language_code]))
        results = self.session.exec(stmt).all()
        inst_lang = next((item for item in results if item.code == request.instruction_language_code), None)
        lang = next((item for item in results if item.code == request.language_code), None)
        if inst_lang == None or lang == None:
            msg = f"Either {request.instruction_language_code} or {request.language_code} is invalid"
            logger.info(msg)
            raise ValueError(msg)
        agent = QnAAgent(client, primary_language=inst_lang, secondary_language=lang)
        
        for chunk in agent.ask_ai_stream(request.question):
            yield chunk


    def askForAudioResponse(self, request: "TutoringService.DualLangRequest"):
        try:
            logger.info(f"user_uuid={request.user_uuid} course_id={request.course_id}\n{request.text_1}\n{request.text_2}")

            stmt = select(User).where(User.uuid == request.user_uuid)
            user = self.session.exec(stmt).first()
            if user is None:
                raise ValueError(f"{request.user_uuid} user not found.")

            course = next((c for c in user.courses if c.course_id == request.course_id), None)
            if course is None:
                raise ValueError(f"Course id {request.course_id} not found for user {request.user_uuid}.")

            subj = self.session.get(Subject, course.course.subject_id)
            if subj is None:
                raise ValueError(f"Subject id {course.course.subject_id} not found.")
            
            level = self.session.get(SubjectLevel, course.course.subject_level_id)
            if level is None:
                raise ValueError(f"Subject level id {course.course.subject_level_id} not found.")
            
            inst_lang = self.session.get(InstructionLanguage, course.instruction_language_id)
            if inst_lang is None:
                raise ValueError(f"Instruction language id {course.instruction_language_id} not found.")
            
            tutor = self.session.get(Tutor, course.tutor_id)
            if tutor is None:
                raise ValueError(f"Tutor id {course.tutor_id} not found.")

            agent = VoiceTutorAgent(subject=subj, level=level, tutor=tutor, inst_lang=inst_lang)
            ai_request = '{"tts1:{"lang":"' + inst_lang.code.split("-")[0] + '","text":"' + request.text_1 + '"},"' + \
                        '{tts2:{"lang":"' + subj.code.split("-")[0] + '","text":"' + request.text_2 + '"}}'
            result = agent.ask_ai(ai_request)
            logger.info(f"AI Answer: {result}")
            ai_result = TutoringService.AiResponse.model_validate_json(result)
            inst_lang_code = inst_lang.code.split("-")[0]
            subject_lang_code = subj.code.split("-")[0]

            answer = self._convertAiResult(inst_lang_code=inst_lang_code, fragments=ai_result.answer)

            # Synthesize audio and phonemes
            audios = TextToSpeech.synthesize(
                text=answer,
                lang_code_1=inst_lang_code,
                lang_code_2=subject_lang_code,
                gender=TextToSpeech.GENDER_FEMALE if tutor.gender == 'F' else TextToSpeech.GENDER_MALE
            )

            # Prepare multipart fields
            fields = {
                "question": self._convertAiResult(inst_lang_code=inst_lang_code, fragments=ai_result.question),
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
        

    def _convertAiResult(self, inst_lang_code: str, fragments: List[TutoringService.AiResponseFragment]) -> str:
        result = ""
        for fragment in fragments:
            if fragment.lang == inst_lang_code:
                result += fragment.text
            else:
                # For other languages, wrap it in <lang>...</lang> tags
                result += f"<{fragment.lang}>{fragment.text}</{fragment.lang}>"
        return result
