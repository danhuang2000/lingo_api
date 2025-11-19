from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class UserCourse(SQLModel, table=True):
    __tablename__ = "user_course"
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
    course_id: int = Field(default=None, foreign_key="course.id", primary_key=True)
    tutor_id: Optional[int] = Field(default=None, foreign_key="tutor.id")
    is_active: bool = Field(default=True)
    instruction_language_id: Optional[int] = Field(default=None, foreign_key="instruction_language.id")
    enrollment_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completion_date: Optional[datetime] = None

    user: Optional["User"] = Relationship(
        back_populates="courses",
        sa_relationship_kwargs={"lazy": "select"}  # Lazy loading
    )

    course: Optional["Course"] = Relationship(
        back_populates="user_courses",
        sa_relationship_kwargs={"lazy": "select"}  # Lazy loading
    )