import re
import json

from utils import get_app_logger
from .tts_client import TTSClient

logger = get_app_logger(__name__)


class TextToSpeech:
    GENDER_MALE = 1
    GENDER_FEMALE = 2

    tts_client = TTSClient()

    @staticmethod
    def synthesize(text: str, lang_code_1: str, lang_code_2: str, gender: int):
        logger.debug(f"synthesizing {text}")
        # Regex to find segments like <es>...</es>
        pattern = re.compile(rf"<{lang_code_2}>(.*?)</{lang_code_2}>", re.DOTALL)
        last_end = 0

        voice1 = TextToSpeech._espeak_voice(lang_code_1, gender)
        voice2 = TextToSpeech._espeak_voice(lang_code_2, gender)
        ssml = []
        ssml.append('<speak>')

        # Find all segments and their languages
        for match in pattern.finditer(text):
            # Text before the tag (lang_code_1)
            if match.start() > last_end:
                text1 = text[last_end:match.start()].strip()
                ssml.append(f'<voice lang="{voice1}">{text1}</voice>')
            # Text inside the tag (lang_code_2)
            text2 = match.group(1).strip()
            ssml.append(f'<voice lang="{voice2}">{text2}</voice>')
            last_end = match.end()

        # Any remaining text after the last tag (lang_code_1)
        if last_end < len(text):
            text1 = text[last_end:].strip()
            ssml.append(f'<voice lang="{voice1}">{text1}</voice>')

        ssml.append('</speak>')
        ssml_text = "".join(ssml)
        logger.debug(f"SSML generated: {ssml_text}")

        # Synthesize each segment and concatenate audio
        phos, audio = TextToSpeech.tts_client.post(text=ssml_text, speed=150)
        
        phonemes = json.loads(phos)
        result = {"audio": audio, "phonemes": phonemes["phonemes"]}

        logger.debug(f"Done synthesize: segment count: {len(result)}")

        return result
    

    @staticmethod
    def _espeak_voice(lang: str, gender: int) -> str:
        buffer = []
        if lang.startswith("zh"):
            buffer.append("cmn-latn-pinyin")
        else:
            buffer.append(lang)
        
        if TextToSpeech.GENDER_FEMALE == gender:
            buffer.append("+f1")
        else:
            buffer.append("+m1")

        return "".join(buffer)
    