from enum import Enum
from string import Template
from .base_agent import BaseAgent
from .openai_client import OpenAiClient
from .stub_client import StubClient
from utils import get_app_logger
from entity import Subject, SubjectLevel, Tutor, InstructionLanguage

logger = get_app_logger(__name__)

TUTOR_SYSTEM_MESSAGE=Template(
"""You are a helpful language tutor. You are $desc
You will use $lang1 as the instruction language to teach $lang2 at ACTFL level $level_name.
The goal is that the student $level_desc
You will provide 10 $lesson_type exercises on the topic of $topic.
Your response must be in JSON including $pronunciation pronunciation. An example is as follows:
[
{"words":[$example]}, "translation":"$translation"}
...
]
""")

SPANISH_PRONUNCIATION='IPA'
SPANISH_EXAMPLE='{"w":"necesito","p":"neθeˈsito"},{"w":"agua","p":"ˈaɣwa"}}'
SPANISH_TRANSLATION='I need water.'

JAPANESE_PRONUNCIATION='romanji'
JAPANESE_EXAMPLE='{"w":"りんご","p":"ringo"},{"w":"を","p":"o"},{"w":"食べる","p":"taberu"}}'
JAPANESE_TRANSLATION="I eat an apple."

class TutorAgent(BaseAgent):
    class LessonType(Enum):
        speaking = 1
        reading  = 2
        writing  = 3

    def __init__(self, 
                subject: Subject,
                level: SubjectLevel,
                tutor: Tutor,
                inst_lang: InstructionLanguage,
                topic: str,
                lesson: LessonType):
        
        if subject.code == 'ja-JP':
            lang_example = JAPANESE_EXAMPLE
            lang_trans = JAPANESE_TRANSLATION
            pronunciation = JAPANESE_PRONUNCIATION
        elif subject.code == 'es-MX':
            lang_example = SPANISH_EXAMPLE
            lang_trans = SPANISH_TRANSLATION
            pronunciation = SPANISH_PRONUNCIATION
        else:
            raise ValueError(f"{subject.name} not yet supported")

        system_message = TUTOR_SYSTEM_MESSAGE.substitute(desc=tutor.description, lang1=inst_lang.name,
            lang2=subject.name, level_name=level.name, level_desc=level.description, lesson_type=lesson.name,
            topic=topic, pronunciation=pronunciation, example=lang_example, translation=lang_trans)
        # client = OpenAiClient()
        client = StubClient()
        super().__init__(client=client, instructions=system_message)
  