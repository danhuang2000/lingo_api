from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship


class SubjectLevelTranslation(SQLModel, table=True):
    __tablename__ = "subject_level_translation"
    id: int | None = Field(default=None, primary_key=True)
    subject_level_id: int = Field(foreign_key="subject_level.id")
    lang_code: str
    name: str
    description: str

