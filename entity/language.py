from typing import List
from sqlmodel import SQLModel, Field, Relationship


class Language(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    code: str
