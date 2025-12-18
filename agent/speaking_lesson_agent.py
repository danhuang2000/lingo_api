from enum import Enum
from string import Template
from .base_agent import BaseAgent
from .client.openai_client import OpenAiClient
from .client.stub_client import StubClient
from utils import get_app_logger
from entity import Subject, SubjectLevel, Tutor, InstructionLanguage

logger = get_app_logger(__name__)

TUTOR_SYSTEM_MESSAGE=Template(
"""You are a helpful language tutor. You are $desc
You will use $lang1 as the instruction language to teach $lang2 at ACTFL level $level_name.
The goal is that the student $level_desc
You will provide $count speaking exercises on the topic of $topic.
Each exercise contains two paragraphs, one in $lang2 and one in $lang1 for translation.
For $lang2, your response must include $pronunciation pronunciation after each word, marked by \t character.
No $pronunciation is needed for $lang1.
An example is as follows:
$example
...
""")

SPANISH_PRONUNCIATION='IPA'
SPANISH_EXAMPLE='Necesito\tneθeˈsito\tagua\taɣwa\t\r\nI need water.\r\n'

ITALIAN_PRONUNCIATION='IPA'
ITALIAN_EXAMPLE='Ho\to\tbisogno\tbiˈzoɲɲo\tdi\tdi\tacqua\tˈakkwa\t.\r\nI need water.\r\n'

JAPANESE_PRONUNCIATION='romanji'
JAPANESE_EXAMPLE='りんご\tringo\tを\to\t食べる\ttaberu\t.\r\nI eat an apple.\r\n'

class SpeakingLessonAgent(BaseAgent):
    def __init__(self, 
                subject: Subject,
                level: SubjectLevel,
                tutor: Tutor,
                inst_lang: InstructionLanguage,
                topic: str,
                exercise_count: int =10):
        
        if subject.code == 'ja-JP':
            lang_example = JAPANESE_EXAMPLE
            pronunciation = JAPANESE_PRONUNCIATION
        elif subject.code == 'es-MX':
            lang_example = SPANISH_EXAMPLE
            pronunciation = SPANISH_PRONUNCIATION
        elif subject.code == 'it-IT':
            lang_example = ITALIAN_EXAMPLE
            pronunciation = ITALIAN_PRONUNCIATION
        else:
            raise ValueError(f"{subject.name} not yet supported")

        system_message = TUTOR_SYSTEM_MESSAGE.substitute(desc=tutor.description, lang1=inst_lang.name,
            lang2=subject.name, level_name=level.name, level_desc=level.description, count=exercise_count,
            topic=topic, pronunciation=pronunciation, example=lang_example)
        # client = OpenAiClient()
        client = StubClient()
        super().__init__(client=client, instructions=system_message)
  