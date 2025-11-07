from fastapi import APIRouter
from fastapi.params import Depends
from db.database import get_session

from entity import User
from service import UserService

router = APIRouter()

@router.post("/add")
def add_user(user: User, session=Depends(get_session)):
    # TODO validate token
    user_service = UserService(session=session)
    user_service.add_user(user)


@router.get("/get/{user_uuid}")
def get_user(user_uuid: str, session=Depends(get_session)):
    # TODO validate token
    user_service = UserService(session=session)
    user = user_service.get_user_by_uuid(user_uuid)
    return user
