
from __future__ import annotations
import os
import json
import redis
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from typing import List, Literal
from requests_toolbelt.multipart import MultipartEncoder
from sqlmodel import Session, select

from agent import VoiceTutorAgent, TextTutorAgent, BaseTutorAgent
from agent.client import OllamaClient, OpenAiClient, StubClient
from entity import User, Subject, SubjectLevel, InstructionLanguage, Tutor
from audio import TextToSpeech
from utils import get_app_logger


logger = get_app_logger(__name__)

class TutoringService:
    class AskTutorRequest(BaseModel):
        user_uuid: str
        course_id: int
        text_1: str
        text_2: str
        mode: str

    class AiResponseFragment(BaseModel):
        lang: str
        text: str

    class AiResponse(BaseModel):
        question: List[TutoringService.AiResponseFragment]
        answer: List[TutoringService.AiResponseFragment]

    class TutorPolicy(BaseModel):
        response_mode: Literal[
            "nextQuestion",
            "correction",
            "explanation",
            "repetition",
            "encouragement"
        ]
        target_language: str
        native_language: str
        learner_level: str
        max_sentence_length: int
        speech_speed: float


    def __init__(self, session: Session):
        self.session = session


    def askForTextResponse(self, request: AskTutorRequest):
        try:
            subj, level, inst_lang, tutor, ai_request = self._getCourseInfo(request)
            session_state = self._get_or_create_session_state(user_uuid=request.user_uuid, course_id=request.course_id)
            agent = TextTutorAgent(subject=subj, level=level, tutor=tutor, inst_lang=inst_lang, mode=request.mode, session_state=session_state)
        
            for chunk in agent.ask_ai_stream(ai_request):
                yield chunk
        except Exception as e:
            logger.error(f"Error processing QnA: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


    def askForAudioResponse(self, request: "TutoringService.DualLangRequest"):
        try:
            subj, level, inst_lang, tutor, ai_request = self._getCourseInfo(request)
            session_state = self._get_or_create_session_state(user_uuid=request.user_uuid, course_id=request.course_id)
            agent = VoiceTutorAgent(subject=subj, level=level, tutor=tutor, inst_lang=inst_lang, mode=request.mode, session_state=session_state)
            result = agent.ask_ai(ai_request)
            logger.info(f"AI Answer: {result}")
            ai_result = TutoringService.AiResponse.model_validate_json(result)
            inst_lang_code = inst_lang.code.split("-")[0]
            subject_lang_code = subj.code.split("-")[0]

            answer = self._convertAiResult(inst_lang_code=inst_lang_code, fragments=ai_result.answer)

            # Synthesize audio and phonemes
            tts = TextToSpeech.synthesize(
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
            idx_lang = f"0_{inst_lang_code}"
            fields[f"phoneme_{idx_lang}"] = (None, json.dumps(tts["phonemes"]), "application/json")
            fields[f"audio_{idx_lang}"] = (f"audio_{idx_lang}.wav", tts["audio"], "audio/wav")
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


    def _getCourseInfo(self, request: AskTutorRequest):
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
        
        ai_request = '{"tts1:{"lang":"' + inst_lang.code.split("-")[0] + '","text":"' + request.text_1 + '"},"' + \
                     '{tts2:{"lang":"' + subj.code.split("-")[0] + '","text":"' + request.text_2 + '"}}'

        return subj, level, inst_lang, tutor, ai_request


    def _convertAiResult(self, inst_lang_code: str, fragments: List[TutoringService.AiResponseFragment]) -> str:
        result = ""
        for fragment in fragments:
            if fragment.lang == inst_lang_code:
                result += fragment.text
            else:
                # For other languages, wrap it in <lang>...</lang> tags
                result += f"<{fragment.lang}>{fragment.text}</{fragment.lang}>"
        return result
    

    def _get_or_create_session_state(self, user_uuid: str, course_id: int) -> BaseTutorAgent.TutorSessionState:
        session_state = self._get_from_dist_memory(key=f"tutor_session:{user_uuid}")

        if session_state == None:
            session_state_obj = BaseTutorAgent.TutorSessionState(
                user_uuid=user_uuid,
                course_id=course_id
            )
            self._set_to_dist_memory(key=f"tutor_session:{user_uuid}", value=json.dumps(session_state_obj.model_dump()))
            return session_state_obj
        
        return BaseTutorAgent.TutorSessionState.model_validate_json(session_state)
    

    def _get_from_dist_memory(self, key: str) -> str | None:
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        r = redis.Redis(host=host, port=port, db=db)
        value = r.get(key)
        if value:
            return value.decode('utf-8')
        return None
    

    def _set_to_dist_memory(self, key: str, value: str):
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        db = int(os.getenv("REDIS_DB", "0"))
        r = redis.Redis(host=host, port=port, db=db)
        r.set(key, value)
