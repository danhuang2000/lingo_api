from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from db.database import get_session

from utils import get_app_logger
from service import TutoringService


logger = get_app_logger(__name__)

router = APIRouter()


@router.post("/question")
def ask_question(request: TutoringService.AskTutorRequest, session=Depends(get_session)):
    service = TutoringService(session=session)
    response = service.askForTextResponse(request)
    if not response:
        raise HTTPException(status_code=500, detail="Could not get answer from tutor.")
    return response


@router.post("/audio/question")
def ask_question_with_audio(request: TutoringService.DualLangRequest, session=Depends(get_session)):
    service = TutoringService(session=session)
    response = service.askForAudioResponse(request)
    if not response:
        raise HTTPException(status_code=500, detail="Could not get answer from tutor with audio.")
    return response