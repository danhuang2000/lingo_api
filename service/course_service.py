import json
from typing import List
from pydantic import BaseModel
from sqlmodel import Session, and_, select
from fastapi.responses import JSONResponse
from entity import Subject, SubjectLevel, Tutor, InstructionLanguage, Topic, UserCourse, Course
from .user_service import UserService
from .cache_service import CacheService
from utils import get_app_logger
from agent import SpeakingLessonAgent

logger = get_app_logger(__name__)

class WordData(BaseModel):
    word: str
    pronunciation: str

class SentenceData(BaseModel):
    sentence: List[WordData]
    translation: str
    
 
class CourseService:
    class UserCourseData(BaseModel):
        user_uuid: str
        course_id: int
        subject_id: int
        level_id: int
        tutor_id: int
        instruction_language_id: int

    class SpeakingLessonRequest(BaseModel):
        user_uuid: str
        course_id: int
        instruction_language_id: int
        topic: str
        lesson_type: str


    def __init__(self, session: Session):
        self.session = session
        self.user_service = UserService(session=session)    


    def get_all_subjects(self):
        cache = CacheService()
        key = "all_subjects"
        if cache.contain(key=key):
            return cache.get(key=key)
        
        stmt = select(Subject.id, Subject.name, Subject.code, Subject.category_id)
        rows = self.session.exec(stmt).all()
        subjects = [Subject(id=row.id, name=row.name, code=row.code, category_id=row.category_id) for row in rows]
        cache.add(key=key, value=subjects)
        return subjects


    def get_subject_levels(self, category_id: int):
        cache = CacheService()
        key = f"all_levels_{category_id}"
        if cache.contain(key=key):
            return cache.get(key=key)
        
        stmt = select(SubjectLevel.id, SubjectLevel.name, SubjectLevel.description).where(SubjectLevel.subject_category_id == category_id)
        rows = self.session.exec(stmt).all()
        levels = [SubjectLevel(id=row.id, name=row.name, description=row.description) for row in rows]
        cache.add(key=key, value=levels)
        return levels
    

    def get_tutors(self):
        cache = CacheService()
        key = "tutors"
        if cache.contain(key=key):
            return cache.get(key=key)
        
        stmt = select(Tutor.id, Tutor.name, Tutor.description, Tutor.url)
        rows = self.session.exec(stmt).all()
        tutors = [Tutor(id=row.id, name=row.name, url=row.url, description=row.description) for row in rows]
        cache.add(key=key, value=tutors)
        return tutors
    

    def get_instruction_languages(self):
        cache = CacheService()
        key = "instruction_languages"
        if cache.contain(key=key):
            return cache.get(key=key)
        stmt = select(InstructionLanguage.id, InstructionLanguage.name, InstructionLanguage.code)
        rows = self.session.exec(stmt).all()
        languages = [InstructionLanguage(id=row.id, name=row.name, code=row.code) for row in rows]
        cache.add(key=key, value=languages)
        return languages


    def get_all_topics(self):
        cache = CacheService()
        key = "all_topics"
        if cache.contain(key=key):
            return cache.get(key=key)
        
        stmt = select(Topic.id, Topic.name, Topic.topic_category_id, Topic.subject_category_id)
        rows = self.session.exec(stmt).all()
        topics = [Topic(id=row.id, name=row.name, topic_category_id=row.topic_category_id, subject_category_id=row.subject_category_id) for row in rows]
        cache.add(key=key, value=topics)
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
            data.course_id = course.id

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

        return data
    

    def update_user_course(self, data: UserCourseData):
        if data.course_id == 0:
            logger.debug("course_id is 0, which is invalid for update_user_course")
            return None

        user = self.user_service.get_user_by_uuid(data.user_uuid)
        if not user:
            logger.info(f"Can't find user {data.user_uuid}")
            return None

        stmt = select(UserCourse).where(UserCourse.user_id == user.id, UserCourse.course_id == data.course_id)

        item = self.session.exec(stmt).first()

        if item == None:
            logger.debug(f"user id={user.id} has no course_id={data.course_id}")
            return item
        
        item.tutor_id = data.tutor_id
        item.instruction_language_id = data.instruction_language_id

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

        logger.debug(f"Update course_id={data.course_id} for user {user.id}")

        return data


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


    def get_speaking_lesson(self, request: SpeakingLessonRequest):
        user = self.user_service.get_user_by_uuid(request.user_uuid)
        user_course = next((item for item in user.courses if item.course_id == request.course_id), None)
        if user_course == None:
            logger.debug("can't find course {request.course_id} for user {request.user_uuid}")
            return None
        
        course = user_course.course

        level_category = 1 # TODO we hard code the subject category
        subject = next((s for s in self.get_all_subjects() if s.id == course.subject_id), None)
        level = next((l for l in self.get_subject_levels(level_category) if l.id == course.subject_level_id), None)
        tutor = next((t for t in self.get_tutors() if t.id == user_course.tutor_id), None)
        inst_lang = next((i for i in self.get_instruction_languages() if i.id == user_course.instruction_language_id), None)

        lesson_type = SpeakingLessonAgent.LessonType[request.lesson_type]

        if subject and level and tutor and inst_lang:
            agent = SpeakingLessonAgent(subject=subject, level=level, tutor=tutor, inst_lang=inst_lang, topic=request.topic, lesson=lesson_type)
            result = agent.ask_ai(question="Please give me a new set of exercises")
            data = json.loads(result)
            return JSONResponse(content=data)
        else:
            logger.info(f"Invalid request: {json.dumps(request)}")

        return None
        