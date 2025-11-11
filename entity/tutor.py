from typing import List
from sqlmodel import SQLModel, Field, Relationship


class Tutor(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    url: str
    description: str
