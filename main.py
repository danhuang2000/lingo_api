from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from orm import init_db, start_db, get_session
from orm.user_orm import UserOrm
from entity import User, Language, LanguageLevel, LanguageLevelHistory



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


