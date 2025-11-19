from typing import List
from sqlmodel import SQLModel, Field, Relationship

class TopicCategory(SQLModel, table=True):
    __tablename__ = "topic_category"
    id: int = Field(default=None, primary_key=True)
    name: str
