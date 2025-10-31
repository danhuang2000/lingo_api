import logging
import io
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse, StreamingResponse
from requests_toolbelt.multipart import MultipartEncoder


from utils import get_app_logger
from orm import init_db, start_db, get_session
from orm.user_orm import UserOrm
from entity import User, Language, LanguageLevel, LanguageLevelHistory
from service import SpeechToText


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = get_app_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = "sqlite:///./sqlite.db"  # Example database URL
    engine = init_db(database_url)
    start_db(engine)
    yield
    # Clean up if any


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Language Learning API"}

@app.post("/user/add")
def add_user(user: User, session=Depends(get_session)):
    user_orm = UserOrm()
    user_orm.add_user(session, user)


@app.get("/user/{user_id}")
def get_user(user_id: int, session=Depends(get_session)):
    user_orm = UserOrm()
    user = user_orm.get_user_by_id(session, user_id)
    return user

from service import get_all_languages

@app.get("/languages")
def get_languages(session=Depends(get_session)):
    languages = get_all_languages(session)
    return languages


from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from service import SpeechToText


@app.post("/audio/stream")
async def upload_audio_stream(file: UploadFile = File(...)):
    try:
        text = await SpeechToText.speech_to_text(file)
        return JSONResponse(content={"transcription": text})
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

from fastapi.staticfiles import StaticFiles
app.mount("/audio", StaticFiles(directory="audio_files"), name="static")


from pydantic import BaseModel

class LangWithText(BaseModel):
    lang: str
    text: str

class DualLangContent(BaseModel):
    content1: LangWithText
    content2: LangWithText

@app.post("/question")
async def ask_qustion(content: DualLangContent):
    try:
        from service import OllamaClient, OpenAiClient, StubClient, QnAAgent, TextToSpeech
        from entity import Language
        import json

        logger.info(f"lang={content.content1.lang} text={content.content1.text}")
        logger.info(f"lang={content.content2.lang} text={content.content2.text}")

        # client = OpenAiClient()
        # client = OllamaClient()
        client = StubClient()
        english = Language(code="en", name="English")
        chinese = Language(code="zh", name="Chinese")
        agent = QnAAgent(client, primary_language=english, secondary_language=chinese)
        answer = agent.ask_ai(content.content1.text)
        logger.info(f"AI Answer: {answer}")

        # Synthesize audio and phonemes
        audios = TextToSpeech.synthesize(
            text=answer,
            lang_code_1="en",
            lang_code_2="zh",
            gender=TextToSpeech.GENDER_FEMALE
        )

        # Prepare multipart fields
        fields = {
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


@app.post("/qna")
async def ask_qna(file: UploadFile = File(...)):
    try:
        stt_text = await SpeechToText.speech_to_text(file=file)
        from service import OllamaClient, OpenAiClient, StubClient, QnAAgent, TextToSpeech
        from entity import Language
        import json

        # client = OpenAiClient()
        # client = OllamaClient()
        client = StubClient()
        english = Language(code="en", name="English")
        chinese = Language(code="zh", name="Chinese")
        agent = QnAAgent(client, primary_language=english, secondary_language=chinese)
        answer = agent.ask_ai(stt_text)
        logger.info(f"AI Answer: {answer}")

        # Synthesize audio and phonemes
        audios = TextToSpeech.synthesize(
            text=answer,
            lang_code_1="en",
            lang_code_2="zh",
            gender=TextToSpeech.GENDER_FEMALE
        )

        # Prepare multipart fields
        fields = {
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
        
