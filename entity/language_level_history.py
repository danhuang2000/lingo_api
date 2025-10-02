from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Column, Integer, ForeignKey, DateTime

class LanguageLevelHistory(SQLModel, table=True):
    __tablename__ = 'language_level_history'
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    language_id: int = Field(default=None, foreign_key="language.id")
    level: int
    create_date: datetime


    def add_language_level_history(self, session, user_id, language_id, level):
        history = LanguageLevelHistory(
            user_id=user_id,
            language_id=language_id,
            level=level,
            create_date=datetime.now(timezone.utc)
        )
        session.add(history)
        session.commit()
        return history
    

    def get_language_level_history(self, session, user_id, language_id):
        return session.query(LanguageLevelHistory).filter_by(
            user_id=user_id,
            language_id=language_id
        ).all()

    
    def delete_language_level_history(self, session, user_id):
        histories = session.query(LanguageLevelHistory).filter_by(
            user_id=user_id
        ).delete()
        session.commit()
