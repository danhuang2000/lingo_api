from typing import List
from sqlmodel import SQLModel, Field, Relationship


class SubjectCategory(SQLModel, table=True):
    __tablename__ = "subject_category"
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str = None
