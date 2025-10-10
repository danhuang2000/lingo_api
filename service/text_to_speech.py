import os
from piper.voice import PiperVoice

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
    def synthesize(text: str, language_code: str, gender: int):
        voice = TextToSpeech.voices.get((language_code, gender))
        if not voice:
            raise ValueError(f"Voice not found for {language_code} and gender {gender}")
        audio = voice.synthesize(text)
        return audio


    @staticmethod
    def phonemize(text: str, language_code: str, gender: int):
        voice = TextToSpeech.voices.get((language_code, gender))
        if not voice:
            raise ValueError(f"Voice not found for {language_code} and gender {gender}")
        phonemes = voice.phonemize(text)
        return phonemes
    