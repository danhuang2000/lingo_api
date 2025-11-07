from sqlmodel import Session, select
from entity import Language, LanguageLevel

class LanguageService:
    def __init__(self, session: Session):
        self.session = session


    def get_all_languages(self):
        stmt = select(Language.id, Language.name, Language.code)
        rows = self.session.exec(stmt).all()
        languages = [Language(id=row.id, name=row.name, code=row.code) for row in rows]
        return languages
    
    def get_all_language_levels(self):
        stmt = select(LanguageLevel.id, LanguageLevel.name, LanguageLevel.description)
        rows = self.session.exec(stmt).all()
        levels = [LanguageLevel(id=row.id, name=row.name, description=row.description) for row in rows]
        return levels
