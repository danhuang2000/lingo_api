import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse

from orm import init_db, start_db, get_session
from orm.user_orm import UserOrm
from entity import User, Language, LanguageLevel, LanguageLevelHistory


load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


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

@app.post("/qna")
async def ask_question(file: UploadFile = File(...)):
    try:
        stt_text = await SpeechToText.speech_to_text(file=file)
        import base64
        from typing import Iterable
        from piper.voice import AudioChunk
        from service import OllamaClient, QnAAgent, TextToSpeech
        from entity import Language
        import numpy as np
        import wave

        client = OllamaClient()
        english = Language(code="en", name="English")
        chinese = Language(code="zh", name="Chinese")
        agent = QnAAgent(client, primary_language=english, secondary_language=chinese)
        answer = agent.ask_ai(stt_text)
        logger.info(f"AI Answer: {answer}")
        audio = TextToSpeech.synthesize(text=answer, language_code="en", gender=TextToSpeech.GENDER_FEMALE)
        file_path = "audio_files/output.wav"
        with wave.open(file_path, "wb") as wf:
            set_header = True
            for chunk in audio:
                if set_header:
                    wf.setnchannels(chunk.sample_channels)  # mono
                    wf.setsampwidth(chunk.sample_width)  # 2 bytes = 16 bits
                    wf.setframerate(chunk.sample_rate)  # sample rate from model config
                    set_header = False
                wf.writeframes(chunk.audio_int16_bytes)
        phonemes_arrays = TextToSpeech.phonemize(text=answer, language_code="en", gender=TextToSpeech.GENDER_FEMALE)
        phonemes = [item for sublist in phonemes_arrays for item in sublist]
        file_url = "http://192.168.1.170:8000/audio/output.wav"
        return JSONResponse(content={"text": answer, "audio": file_url, "phoneme": phonemes})
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing QnA: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")    
    
