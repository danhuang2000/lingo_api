from typing import List
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship

from .user_course import UserCourse
from .user_topic import UserTopic
from .device import Device


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: str | None = Field(default=None, index=True, unique=True)
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    create_date: datetime | None
    update_date: datetime | None

    courses: List[UserCourse] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "select"}  # Lazy loading
    )

    topics: List[UserTopic] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "select"}  # Lazy loading
    )

    devices: List[Device] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "select"}  # Lazy loading
    )
    
