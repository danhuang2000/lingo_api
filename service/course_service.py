from sqlmodel import Session, select
from entity import Subject, SubjectLevel

class CourseService:
    def __init__(self, session: Session):
        self.session = session


    def get_all_subjects(self):
        stmt = select(Subject.id, Subject.name, Subject.code, Subject.category_id)
        rows = self.session.exec(stmt).all()
        subjects = [Subject(id=row.id, name=row.name, code=row.code, category_id=row.category_id) for row in rows]
        return subjects
    
    def get_subject_levels(self, category_id: int):
        stmt = select(SubjectLevel.id, SubjectLevel.name, SubjectLevel.description).where(SubjectLevel.subject_category_id == category_id)
        rows = self.session.exec(stmt).all()
        levels = [SubjectLevel(id=row.id, name=row.name, description=row.description) for row in rows]
        return levels
