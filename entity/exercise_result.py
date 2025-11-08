from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class ExerciseResult(SQLModel, table=True):
    __tablename__ = "exercise_result"
    id: int | None = Field(default=None, primary_key=True)
    user_topic_id: int = Field(foreign_key="user_topic.id")
    question: str
    answer: str
    score: int
    create_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))   
