from sqlmodel import select
from entity import Language

def get_all_languages(session):
    stmt = select(Language.id, Language.name, Language.code)
    rows = session.exec(stmt).all()
    languages = [Language(id=row.id, name=row.name, code=row.code) for row in rows]
    return languages
