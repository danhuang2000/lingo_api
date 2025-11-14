from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class Device(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: str | None = Field(default=None, index=True, unique=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    key_id: str | None = None
    public_key: str | None = None
    challenge: str | None = None
    create_date: datetime | None

    user: Optional["User"] = Relationship(
        back_populates="devices",
        sa_relationship_kwargs={"lazy": "select"}
    )