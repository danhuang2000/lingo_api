from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from db.database import get_session

from entity import User
from service import CourseService, SecurityService

router = APIRouter()

@router.get("/subjects")
def get_all_subjects(session=Depends(get_session)):
    # TODO validate token
   service = CourseService(session=session)
   languages = service.get_all_subjects()
   return languages

@router.get("/subject/levels/{category_id}")
def get_subject_levels(category_id: int, session=Depends(get_session)):
    # TODO validate token
    service = CourseService(session=session)
    levels = service.get_subject_levels(category_id=category_id)
    return levels

@router.get("/tutors")
def get_tutors(session=Depends(get_session)):
    # TODO validate token
    service = CourseService(session=session)
    tutors = service.get_tutors()
    return tutors

@router.get("/instructionlanguages")
def get_instruction_languages(session=Depends(get_session)):
    # TODO validate token
    service = CourseService(session=session)
    instruction_languages = service.get_instruction_languages()
    return instruction_languages

@router.get("/topics/all")
def get_all_topics(session=Depends(get_session)):
    service = CourseService(session=session)
    topics = service.get_all_topics()
    return topics

@router.post("/myclass/add")
def add_user_course(courseData: CourseService.UserCourseData, session=Depends(get_session)):
    service = CourseService(session=session)
    userCourse = service.add_user_course(courseData)
    return userCourse

@router.post("/myclass/update")
def update_user_course(course: CourseService.UserCourseData, session=Depends(get_session)):
    service = CourseService(session=session)
    userCourse = service.update_user_course(course)
    return userCourse

@router.post("/myclasses")
def get_user_classes(user: SecurityService.UserUuidInfo, session=Depends(get_session)):
    service = CourseService(session=session)
    courses = service.get_user_courses(user.user_uuid)
    return courses


@router.post("/lesson/speaking")
def get_speaking_lesson(request: CourseService.SpeakingLessonRequest, session=Depends(get_session)):
    service = CourseService(session=session)
    return StreamingResponse(service.get_speaking_lesson(request=request), media_type="text/plain")


@router.post("/lesson/exercise/result")
def submit_exercise_result(result: CourseService.ExerciseResultRequest, session=Depends(get_session)):
    service = CourseService(session=session)
    return service.submit_exercise_result(result)


@router.post("/lesson/listening/generate")
def generate_listening_lesson(request: CourseService.ListeningGenerateRequest, session=Depends(get_session)):
    service = CourseService(session=session)
    return service.generate_listening_lesson(request=request)


@router.post("/lesson/writing/generate")
def generate_writing_lesson(request: CourseService.WritingGenerateRequest, session=Depends(get_session)):
    service = CourseService(session=session)
    return service.generate_writing_lesson(request=request)