from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel, Column, Integer, ForeignKey, DateTime

class ExerciseSet(SQLModel, table=True):
    __tablename__ = 'exercise_set'

    class ExerciseTypeEnum(str, Enum):
        speaking  = "speaking"
        writing   = "writing"
        listening = "listening"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    course_id: int = Field(default=None, foreign_key="course.id")
    topic_id: int = Field(default=None, foreign_key="topic.id")
    exercise_type: Optional[ExerciseTypeEnum] = Field(sa_column=SAEnum(ExerciseTypeEnum, name="exercise_type", nullable=True))
    exercise_count: int = Field(default=0)
    correct_percentage: float = Field(default=0.0)
    create_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    )

    user: Optional["User"] = Relationship(
        back_populates="exercises",
        sa_relationship_kwargs={"lazy": "select"}  # Lazy loading
    )