from typing import List
from sqlmodel import SQLModel, Field, Relationship


class Course(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subject.id")
    subject_level_id: int = Field(foreign_key="subject_level.id")
