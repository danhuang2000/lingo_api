import logging
import io
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, File, Request, UploadFile, HTTPException
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse, StreamingResponse
from requests_toolbelt.multipart import MultipartEncoder

from routes import course_api, user_api
from utils import get_app_logger
from db import init_db, start_db, get_session
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
    # database_url = "sqlite:///./sqlite.db"  # Example database URL
    database_url = "mysql+mysqlconnector://localhost:3306/lingoDB"
    engine = init_db(database_url)
    start_db(engine)
    yield
    # Clean up if any


app = FastAPI(lifespan=lifespan)

app.include_router(user_api.router, prefix="/api/user", tags=["Users"])
app.include_router(course_api.router, prefix="/api/courses", tags=["Courses"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Language Learning API"}


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
app.mount("/image", StaticFiles(directory="image_files"), name="static")


@app.middleware("http")
async def log_request_body(request: Request, call_next):
    headers = dict(request.headers)
    logger.debug(f"Request headers: {headers}")
    body = await request.body()
    logger.debug(f"Raw request body: {body}")
    response = await call_next(request)
    return response


from pydantic import BaseModel

class LangWithText(BaseModel):
    lang: str
    text: str

class DualLangContent(BaseModel):
    content1: LangWithText
    content2: LangWithText

@app.post("/topics")
async def get_topics():
    topics = [
        {"category": "Personal Information",
         "topics": [
            "Introducing yourself",
            "Talking about age, nationality, and occupation",
            "Describing physical appearance and personality"
            ]
        },
        {"category": "Family & Relationships",
         "topics": [
            "Talking about family members",
            "Describing relationships and roles",
            "Expressing likes/dislikes about people"
            ]
        },
        {"category": "Daily Life",
         "topics": [
            "Discussing routines and schedules",
            "Talking about school or work",
            "Time, days of the week, and calendar vocabulary"
            ]
        },
        {"category": "Education",
         "topics": [
            "Describing classes and subjects",
            "Talking about teachers and classmates",
            "School supplies and classroom language"
            ]
        },
        {"category": "Food & Drink",
         "topics":[             
            "Eating in a restaurant",
            "Grocery shopping",
            "Describing meals and dietary preferences"
            ]
        },
        {"category": "Hobbies & Leisure",
         "topics": [
            "Talking about hobbies and interests",
            "Sports and games",
            "Music, movies, and books"
            ]
        },
        {"category": "Travel & Transportation",
         "topics": [
            "Asking for directions",
            "Using public transport",
            "Booking hotels or flights"
            ]
        },
        {"category": "Shopping",
         "topics": [
            "Buying clothes, gifts, or groceries",
            "Asking about prices and sizes",
            "Describing items and preferences"
            ]
        },
        {"category": "Weather & Seasons",
         "topics": [
            "Describing the weather",
            "Talking about seasons and climate",
            "Planning activities based on weather"
            ]
        },
        {"category": "Health & Body",
         "topics": [
            "Describing symptoms and illnesses",
            "Visiting the doctor or pharmacy",
            "Talking about fitness and well-being"
            ]
        },
        {"category": "Home & Living",
         "topics": [
            "Describing your house or apartment",
            "Talking about chores and furniture",
            "Neighborhood and community"
            ]
        },
        {"category": "Celebrations & Culture",
         "topics": [
            "Holidays and traditions",
            "Birthdays and parties",
            "Cultural customs and etiquette",
            "idioms and expressions"
            ]
        },
        {"category": "Technology & Media",
         "topics": [
            "Using phones and computers",
            "Social media and communication",
            "News and entertainment"
            ]
        },
        {"category": "Jobs & Professions",
         "topics": [
            "Describing different occupations",
            "Talking about career plans",
            "Workplace vocabulary"
            ]
        }
    ]

    return topics


@app.get("/speaking")
async def get_speaking_practice():
    return "This is the speaking practice endpoint."


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
        
