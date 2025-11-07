from sqlmodel import SQLModel, create_engine, Session
from fastapi import Depends

engine = None

def init_db(database_url: str):
    global engine
    engine = create_engine(database_url, echo=True)
    return engine


def start_db(engine):
    SQLModel.metadata.create_all(engine)


def get_session():
    global engine
    with Session(engine) as session:
        yield session

