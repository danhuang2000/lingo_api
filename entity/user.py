from typing import List
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship

from .language_level_history import LanguageLevelHistory
from .language_level import LanguageLevel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str | None = None
    phone: str
    create_date: datetime # = Field(default_factory=datetime.now(timezone.utc))
    update_date: datetime # = Field(default_factory=datetime.now(timezone.utc))

    languages: List["Language"] = Relationship(
        back_populates="users",
        link_model=LanguageLevel,
        sa_relationship_kwargs={"lazy": "select"}  # or "dynamic", "subquery", etc.)
    )
 
    def delete_user(self, session, user_id):
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            session.query(LanguageLevelHistory).filter_by(user_id=user.id).delete()
            session.delete(user)
            session.commit()
        return user
