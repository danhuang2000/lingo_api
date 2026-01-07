from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from db.database import get_session

from utils import get_app_logger
from service import TutoringService


logger = get_app_logger(__name__)

router = APIRouter()


@router.post("/{mode}/question")
async def tutor_question(mode: str, req: TutoringService.AskTutorRequest, session=Depends(get_session)):
    service = TutoringService(session=session)
    if mode == "text":
        return StreamingResponse(service.askForTextResponse(req))
    elif mode == "audio":
        response = service.askForAudioResponse(req)
        if not response:
            raise HTTPException(status_code=500, detail="Could not get answer from tutor with audio.")
        return response
    else:
        raise HTTPException(status_code=400, detail="Invalid mode specified.")

