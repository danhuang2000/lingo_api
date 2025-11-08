from typing import List
from sqlmodel import SQLModel, Field, Relationship


class SubjectTanslation(SQLModel, table=True):
    __tablename__ = "subject_translation"
    id: int = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subject.id")    
    name: str
    description: str = None
