from fastapi import APIRouter
from fastapi.params import Depends
from db.database import get_session

from service import CourseService

router = APIRouter()

@router.get("/subjects")
def get_all_subjects(session=Depends(get_session)):
    # TODO validate token
   service = CourseService(session=session)
   languages = service.get_all_subjects()
   return languages

@router.get("/subject/levels/{category_id}")
def get_subject_levels(category_id: int, session=Depends(get_session)):
    # TODO validate token
    service = CourseService(session=session)
    levels = service.get_subject_levels(category_id=category_id)
    return levels

@router.get("/tutors")
def get_tutors(session=Depends(get_session)):
    # TODO validate token
    service = CourseService(session=session)
    tutors = service.get_tutors()
    return tutors