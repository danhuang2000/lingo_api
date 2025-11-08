from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel, Column, Integer, ForeignKey, DateTime

class UserTopic(SQLModel, table=True):
    __tablename__ = 'user_topic'
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    course_id: int = Field(default=None, foreign_key="course.id")
    topic_id: int = Field(default=None, foreign_key="topic.id")
    name: str | None = None
    is_active: bool = Field(default=True)
    exercise_count: int = Field(default=0)
    correct_percentage: float = Field(default=0.0)

    user: Optional["User"] = Relationship(
        back_populates="topics",
        sa_relationship_kwargs={"lazy": "select"}  # Lazy loading
    )