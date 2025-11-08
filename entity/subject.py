from typing import List
from sqlmodel import SQLModel, Field, Relationship


class Subject(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    code: str
    description: str = None
    category_id: int = Field(foreign_key="subject_category.id")
