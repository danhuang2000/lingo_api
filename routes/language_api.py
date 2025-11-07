from fastapi import APIRouter
from fastapi.params import Depends
from db.database import get_session

from service import LanguageService

router = APIRouter()

@router.get("/all")
def add_user(session=Depends(get_session)):
    # TODO validate token
   service = LanguageService(session=session)
   languages = service.get_all_languages()
   return languages

@router.get("/levels")
def get_language_levels(session=Depends(get_session)):
    # TODO validate token
    service = LanguageService(session=session)
    levels = service.get_all_language_levels()
    return levels