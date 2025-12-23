import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, File, Request, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from audio import SpeechToText    

from routes import course_api, user_api, tutoring_api
from utils import get_app_logger
from db import init_db, start_db


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


logger = get_app_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # database_url = "sqlite:///./sqlite.db"  # Example database URL
    database_url = "mysql+mysqlconnector://localhost:3306/lingoDB"
    engine = init_db(database_url)
    start_db(engine)
    yield
    # Clean up if any


app = FastAPI(lifespan=lifespan)

app.include_router(user_api.router, prefix="/api/user", tags=["Users"])
app.include_router(course_api.router, prefix="/api/courses", tags=["Courses"])
app.include_router(tutoring_api.router, prefix="/api/tutor", tags=["Tutor"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Language Learning API"}


app.mount("/audio", StaticFiles(directory="audio_files"), name="static")
app.mount("/image", StaticFiles(directory="image_files"), name="static")


@app.middleware("http")
async def log_request_body(request: Request, call_next):   
    headers = dict(request.headers)
    logger.debug(f"Request headers: {headers}")
    body = await request.body()
    logger.debug(f"Raw request body: {body}")
    response = await call_next(request)
    return response


#TODO the following API is for testing
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
