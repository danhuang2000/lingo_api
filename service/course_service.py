import logging
from pydantic import BaseModel
from sqlmodel import Session, and_, select
from entity import Subject, SubjectLevel, Tutor, InstructionLanguage, User, UserCourse, Course
from .user_service import UserService

logger = logging.getLogger(__name__)

class CourseService:
    class UserCourseData(BaseModel):
        def __init__(self, user_uuid, subject_id, level_id, tutor_id, inst_lang_id):
            self.user_uuid = user_uuid
            self.subject_id = subject_id
            self.level_id = level_id
            self.tutor_id = tutor_id
            self.instruction_language_id = inst_lang_id


    def __init__(self, session: Session):
        self.session = session

    def get_user_service(self):
        if not self.user_service:
            self.user_service = UserService()
        return self.user_service
    

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
    
    def get_tutors(self):
        stmt = select(Tutor.id, Tutor.name, Tutor.description, Tutor.url)
        rows = self.session.exec(stmt).all()
        tutors = [Tutor(id=row.id, name=row.name, url=row.url, description=row.description) for row in rows]
        return tutors
    
    def get_instruction_languages(self):
        stmt = select(InstructionLanguage.id, InstructionLanguage.name, InstructionLanguage.code)
        rows = self.session.exec(stmt).all()
        languages = [InstructionLanguage(id=row.id, name=row.name, code=row.code) for row in rows]
        return languages

    def add_user_course(self, data: UserCourseData):
        stmt = select(Course).where(
            and_(Course.subject_id == data.subject_id,
                 Course.subject_level_id == data.level_id))
        course = self.session.exec(stmt).first()
        if not course:
            course = Course(subject_id=data.subject_id, subject_level_id=data.level_id)
            self.session.add(course)
            self.session.commit()
            self.session.refresh(course)

        user = self.get_user_service.get_user_by_uuid(data.user_uuid)
        if not user:
            logger.info(f"Can't find user {data.user_uuid}")
            return None
        
        userCourse = UserCourse(
            user_id=user.id,
            course_id=course.id,
            tutor_id=data.tutor_id,
            is_active=True,
            instruction_language_id=data.instruction_language_id,
        )
        self.session.add(userCourse)
        self.session.commit()
        self.session.refresh(userCourse)
        return userCourse
    

    def get_user_courses(self, user: User):
        stmt = select(Course).join(UserCourse).where(
            and_(UserCourse.user.uuid == user.uuid,
                UserCourse.is_active == True))
        
        results = self.session.exec(stmt).all()
 