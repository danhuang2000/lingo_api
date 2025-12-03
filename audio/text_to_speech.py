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
        segments = []
        last_end = 0

        # Find all segments and their languages
        for match in pattern.finditer(text):
            # Text before the tag (lang_code_1)
            if match.start() > last_end:
                segments.append((text[last_end:match.start()], lang_code_1))
            # Text inside the tag (lang_code_2)
            segments.append((match.group(1), lang_code_2))
            last_end = match.end()

        # Any remaining text after the last tag (lang_code_1)
        if last_end < len(text):
            segments.append((text[last_end:], lang_code_1))

        # Synthesize each segment and concatenate audio
        result = []
        for segment_text, language_code in segments:
            segment_text = segment_text.strip()
            if not segment_text:
                continue
            
            phos, audio = TextToSpeech.tts_client.post(
                lang=language_code,
                gender="female" if TextToSpeech.GENDER_FEMALE == gender else "male",
                text=segment_text 
            )
            
            phonemes = json.loads(phos)
            result.append({"lang": language_code, "audio": audio, "phonemes": phonemes["phonemes"]})

        logger.debug(f"Done synthesize: segment count: {len(result)}")

        return result
    
    