import io
import os
import logging
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
import torchaudio

from orm import init_db, start_db, get_session
from orm.user_orm import UserOrm
from entity import User, Language, LanguageLevel, LanguageLevelHistory


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
import whisper
import tempfile

model = whisper.load_model("small")  # You can use "tiny", "base", "small", "medium", "large"

@app.post("/audio/stream")
async def upload_audio_stream(file: UploadFile = File(...)):
    if file.content_type not in ["audio/x-m4a", "audio/m4a", "audio/mpeg", "audio/wav"]:
        logger.info(f"Invalid audio format: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid audio format")

    try:
        file_bytes = await file.read()

        with tempfile.NamedTemporaryFile(suffix=".m4a") as tmp:
            tmp.write(file_bytes)
            tmp.flush()

            result = model.transcribe(tmp.name)
            logger.debug(f"STT: {result['text']}")

        return JSONResponse(content={"text": result["text"]})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
