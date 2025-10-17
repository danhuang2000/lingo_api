import io
import os
import re
import logging
import wave
from piper.voice import PiperVoice

logger = logging.getLogger(__name__)


class TextToSpeech:
    GENDER_MALE = 1
    GENDER_FEMALE = 2

    EN_MALE = ("en", GENDER_MALE)
    EN_FEMALE = ("en", GENDER_FEMALE)
    ES_MALE = ("es", GENDER_MALE)
    ES_FEMALE = ("es", GENDER_FEMALE)
    ZH_MALE = ("zh", GENDER_MALE)
    ZH_FEMALE = ("zh", GENDER_FEMALE)

    VOICE_MODEL_PATH = os.getenv("VOICE_MODEL_PATH", ".")

    voices = {
        EN_FEMALE: PiperVoice.load(VOICE_MODEL_PATH + "en_US-amy-medium.onnx"),
        ZH_FEMALE: PiperVoice.load(VOICE_MODEL_PATH + "zh_CN-huayan-x_low.onnx"),
    }


    @staticmethod
    def synthesize(text: str, lang_code_1: str, lang_code_2: str, gender: int):
        logging.debug(f"synthesizing {text}")
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
        audios = []
        for segment_text, language_code in segments:
            segment_text = segment_text.strip()
            if not segment_text:
                continue
            voice = TextToSpeech.voices.get((language_code, gender))
            if not voice:
                raise ValueError(f"Voice not found for {language_code} and gender {gender}")
            
            buffer = io.BytesIO()

            with wave.open(buffer, "wb") as wav_file:
                write_header = True
                for chunk in voice.synthesize(segment_text):
                    if write_header:
                        wav_file.setframerate(chunk.sample_rate)
                        wav_file.setsampwidth(chunk.sample_width)
                        wav_file.setnchannels(chunk.sample_channels)
                        write_header = False
                    wav_file.writeframes(chunk.audio_int16_bytes)

            buffer.seek(0)

            audio = voice.synthesize(segment_text)
            phonemes = voice.phonemize(segment_text)
            audios.append({"lang": language_code, "audio": buffer, "phoneme": phonemes[0]})

        logger.debug(f"Done synthesize: segment count: {len(audios)}")

        return audios
    
    