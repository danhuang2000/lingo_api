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
Since my STT can only handle one language at a time, you will be provided with two speech to text strings
from the same audio input. An example is as follows:
{"tts1":{"lang":"$lang_code_1","text":"..."},"tts2":{"lang":"$lang_code_2","text":"..."}}
You will try your best to convert the two text strings into a meaningful question containing one or
both $lang1 and $lang2. You will then answer the question.
Your response must be in JSON. An example is as follows:
{"question":$question,"answer":$answer}
""")

SPANISH_QUESTION_EXAMPLE="""
[{"lang":"en","text":"What is the meaning of"},{"lang":"es","text":"aqua"},{"lang":"en","text":"?"}]
"""

SPANISH_ANSWER_EXAMPLE="""
[{"lang":"en","text":"The meaning of"},{"lang":"es","text":"agua"},{"lang":"en","text":"is water."}]
"""

class VoiceTutorAgent(BaseAgent):
    def __init__(self, 
                subject: Subject,
                level: SubjectLevel,
                tutor: Tutor,
                inst_lang: InstructionLanguage):
        
        if subject.code == 'es-MX':
            question_example = SPANISH_QUESTION_EXAMPLE
            answer_example = SPANISH_ANSWER_EXAMPLE
        else:
            raise ValueError(f"{subject.name} not yet supported")

        system_message = TUTOR_SYSTEM_MESSAGE.substitute(desc=tutor.description, lang1=inst_lang.name,
            lang2=subject.name, lang_code_1=inst_lang.code, lang_code_2=subject.code,
            level_name=level.name, question=question_example, answer=answer_example)
        
        logger.debug(f"VoiceTutorAgent system message:\n{system_message}")
        # client = OpenAiClient()
        client = StubClient()
        super().__init__(client=client, instructions=system_message)
  