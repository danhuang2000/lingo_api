from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class UserLevel(SQLModel, table=True):
    __tablename__ = "user_level"
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
    language_id: int = Field(default=None, foreign_key="language.id", primary_key=True)
    level_id: int = Field(foreign_key="language_level.id")
    update_date: datetime = Field(default_factory=datetime.now(timezone.utc))

    user: Optional["User"] = Relationship(back_populates="levels")

