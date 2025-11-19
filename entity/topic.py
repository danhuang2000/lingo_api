from typing import List
from sqlmodel import SQLModel, Field, Relationship

class Topic(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    topic_category_id: int = Field(foreign_key="topic_category.id")
    subject_category_id: int = Field(foreign_key="subject_category.id")
