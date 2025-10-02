from typing import List
from sqlmodel import SQLModel, Field, Relationship
from .language_level import LanguageLevel

class Language(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    code: str

    users: List["User"] = Relationship(
        back_populates="languages",
        link_model=LanguageLevel,
        sa_relationship_kwargs={"lazy": "select"}  # or "dynamic", "subquery", etc.)
    )

    def get_all_languages(self, session):
        return session.query(Language).all()
