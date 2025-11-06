from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship

from .language_level_history import LanguageLevelHistory


class LanguageLevel(SQLModel, table=True):
    """
    Language level entity representing a user's proficiency in a specific language.
    ACTFL levels are used: 
        Novice - Low, Mid, High 
        Intermediate - Low, Mid, High
        Advanced - Low, Mid, High 
        Superior
        Distinguished
    """
    # __tablename__ = 'language_level'
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    language_id: Optional[int] = Field(default=None, foreign_key="language.id", primary_key=True)
    level: int
    update_date: datetime # = Field(default_factory=datetime.now(timezone.utc))


    def get_language_level_by_user(self, session, user, language):
        return session.query(LanguageLevel).filter_by(
            user_id=user.id,
            language_id=language.id
        ).first()
    

    def set_user_language_level(self, session, user, language, level):
        user_language_level = LanguageLevel(user_id=user.id, language_id=language.id, level=level)
        user_language_level.update_date = datetime.utcnow()
        session.add(user_language_level)

        history = LanguageLevelHistory(
            user_id=user.id,
            language_id=language.id,
            level=level,
            create_date=datetime.utcnow()
        )
        session.add(history)

        session.commit()
        return user_language_level