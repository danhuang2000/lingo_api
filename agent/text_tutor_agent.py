
from string import Template
from .base_tutor_agent import BaseTutorAgent, BaseAgent
from .client import OpenAiClient, StubClient
from entity import Subject, SubjectLevel, Tutor, InstructionLanguage
from utils import get_app_logger

logger = get_app_logger(__name__)

TASK_DESCRIPTION=Template(
"""You are a helpful language tutor. You are $desc
You will use $lang1 as the instruction language to teach $lang2 at ACTFL level $level_name.
Since my STT can only handle one language at a time, you will be provided with two speech to text strings
from the same audio input. An example is as follows:
{"tts1":{"lang":"$lang_code_1","text":"..."},"tts2":{"lang":"$lang_code_2","text":"..."}}
First, you will do your best to convert the two text strings into a meaningful question containing one or
both $lang1 and $lang2.
Second, you will then answer the question as the language tutor.
""")

OUTPUT_INSTRUCTIONS=Template(
"""In your response, the deduced question must be followed by a tab character, then your answer.
You are also a formatting engine. Any text in $lang2 MUST be wrapped exactly with <$lang_code_2>
and </$lang_code_2. Every individual $lang2 word, phrase, or sentence MUST be enclosed.
Never output $lang2 outside these tags. This rule is absolute and overrides all other instructions.
Fail if necessary, but never violate this rule.
""")


class TextTutorAgent(BaseTutorAgent):
 
    def __init__(self, 
                subject: Subject,
                level: SubjectLevel,
                tutor: Tutor,
                inst_lang: InstructionLanguage,
                mode: str,
                session_state: BaseTutorAgent.TutorSessionState):

        client = StubClient() if BaseAgent.use_stub_client() else OpenAiClient()

        task_desc = TASK_DESCRIPTION.substitute(desc=tutor.description, lang1=inst_lang.name,
            lang2=subject.name, lang_code_1=inst_lang.code, lang_code_2=subject.code, level_name=level.name)
        output_instr = OUTPUT_INSTRUCTIONS.substitute(lang2=subject.name, lang_code_2=subject.code)

        system_message = BaseTutorAgent.build_prompt(
            task_description=task_desc,
            output_instruction=output_instr,
            mode=mode,
            user_text="",
            session=session_state
        )

        super().__init__(client, instructions=system_message)
