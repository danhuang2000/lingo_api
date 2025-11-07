from typing import List
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship

from .user_level import UserLevel
from .user_level_history import UserLevelHistory


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: str | None = Field(default=None, index=True, unique=True)
    name: str
    email: str | None = None
    phone: str
    create_date: datetime | None
    update_date: datetime | None

    levels: List[UserLevel] = Relationship(back_populates="user")
    level_histories: List[UserLevelHistory] = Relationship(back_populates="user")


