import logging
from pydantic import BaseModel
from sqlmodel import Session, and_, select
from entity import Subject, SubjectLevel, Tutor, InstructionLanguage, Topic, UserCourse, Course
from .user_service import UserService

logger = logging.getLogger(__name__)

class CourseService:
    class UserCourseData(BaseModel):
        user_uuid: str
        course_id: int
        subject_id: int
        level_id: int
        tutor_id: int
        instruction_language_id: int


    def __init__(self, session: Session):
        self.session = session
        self.user_service = UserService(session=session)    

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

    def get_all_topics(self):
        stmt = select(Topic.id, Topic.name, Topic.topic_category_id, Topic.subject_category_id)
        rows = self.session.exec(stmt).all()
        topics = [Topic(id=row.id, name=row.name, topic_category_id=row.topic_category_id, subject_category_id=row.subject_category_id) for row in rows]
        return topics

    def add_user_course(self, data: UserCourseData):
        if data.course_id == 0:
            stmt = select(Course).where(
                and_(Course.subject_id == data.subject_id,
                    Course.subject_level_id == data.level_id))
            course = self.session.exec(stmt).first()
            if not course:
                course = Course(subject_id=data.subject_id, subject_level_id=data.level_id)
                self.session.add(course)
                self.session.commit()
                self.session.refresh(course)

        user = self.user_service.get_user_by_uuid(data.user_uuid)
        if not user:
            logger.info(f"Can't find user {data.user_uuid}")
            return None
        
        item = next((uc for uc in user.courses if uc.course_id == course.id), None)

        if item != None:
            logger.debug(f"user id={user.id} with course_id={course.id} aleady exist")
            return item
        
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

        logger.debug(f"Add course_id={course.id} for user {user.id}")

        return userCourse
    

    def get_user_courses(self, user_uuid: str) -> list[UserCourseData]:
        user = self.user_service.get_user_by_uuid(user_uuid)
        
        results = []
        for uc in user.courses:
            item = CourseService.UserCourseData(
                user_uuid=user_uuid,
                course_id=uc.course_id,
                subject_id=uc.course.subject_id, 
                level_id=uc.course.subject_level_id, 
                tutor_id=uc.tutor_id, 
                instruction_language_id=uc.instruction_language_id
            )
            results.append(item)

        return results

 