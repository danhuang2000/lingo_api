from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel, Column, Integer, ForeignKey, DateTime

class UserLevelHistory(SQLModel, table=True):
    __tablename__ = 'user_level_history'
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    language_id: int = Field(default=None, foreign_key="language.id")
    level: int
    create_date: datetime

    user: Optional["User"] = Relationship(back_populates="level_histories")

