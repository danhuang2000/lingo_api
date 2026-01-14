from enum import Enum
from string import Template
from .base_tutor_agent import BaseTutorAgent, BaseAgent
from .client.openai_client import OpenAiClient
from .client.stub_client import StubClient
from utils import get_app_logger
from entity import Subject, SubjectLevel, Tutor, InstructionLanguage

logger = get_app_logger(__name__)

TASK_DESCRIPTION=Template(
"""You are a helpful language tutor. You are $desc
You will use $lang1 as the instruction language to teach $lang2 at ACTFL level $level_name.
Since my STT can only handle one language at a time, you will be provided with two speech to text strings
from the same audio input. An example is as follows:
{"tts1":{"lang":"$lang_code_1","text":"..."},"tts2":{"lang":"$lang_code_2","text":"..."}}
You will try your best to convert the two text strings into a meaningful question containing one or
both $lang1 and $lang2. You will then answer the question.
""")

OUTPUT_INSTRUCTIONS=Template(
"""Your response must be in JSON. An example is as follows:
{"question":$question,"answer":$answer}
""")

SPANISH_QUESTION_EXAMPLE="""
[{"lang":"en","text":"What is the meaning of"},{"lang":"es","text":"aqua"},{"lang":"en","text":"?"}]
"""

SPANISH_ANSWER_EXAMPLE="""
[{"lang":"en","text":"The meaning of"},{"lang":"es","text":"agua"},{"lang":"en","text":"is water."}]
"""

class VoiceTutorAgent(BaseTutorAgent):
    def __init__(self, 
                subject: Subject,
                level: SubjectLevel,
                tutor: Tutor,
                inst_lang: InstructionLanguage,
                mode: str,
                session_state: BaseTutorAgent.TutorSessionState):
        
        if subject.code == 'es-MX':
            question_example = SPANISH_QUESTION_EXAMPLE
            answer_example = SPANISH_ANSWER_EXAMPLE
        else:
            raise ValueError(f"{subject.name} not yet supported")

        task_desc = TASK_DESCRIPTION.substitute(desc=tutor.description, lang1=inst_lang.name,
            lang2=subject.name, lang_code_1=inst_lang.code, lang_code_2=subject.code, level_name=level.name)
        
        output_instr = OUTPUT_INSTRUCTIONS.substitute(question=question_example, answer=answer_example)

        system_message = BaseTutorAgent.build_prompt(
            task_description=task_desc,
            output_instruction=output_instr,
            mode=mode,
            user_text="",
            session=session_state
        )

        client = StubClient() if BaseAgent.use_stub_client() else OpenAiClient()
        super().__init__(client=client, instructions=system_message)
  