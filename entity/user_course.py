from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class UserCourse(SQLModel, table=True):
    __tablename__ = "user_course"
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
    course_id: int = Field(default=None, foreign_key="course.id", primary_key=True)
    is_active: bool = Field(default=True)
    enrollment_date: datetime = Field(default_factory=datetime.now(timezone.utc))
    completion_date: Optional[datetime] = None

    user: Optional["User"] = Relationship(
        back_populates="courses",
        sa_relationship_kwargs={"lazy": "select"}  # Lazy loading
    )