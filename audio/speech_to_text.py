
import tempfile
import whisper
from fastapi import UploadFile

from utils import get_app_logger

logger = get_app_logger(__name__)


class SpeechToText:
    __model = whisper.load_model("small")

    @staticmethod
    async def speech_to_text(file: UploadFile) -> str:
        extension = ''
        if file.content_type ==  "audio/m4a":
            extension = ".m4a"
        elif file.content_type == "audio/wav":
            extension = ".wav"
        else:
            logger.info(f"Invalid audio format: {file.content_type}")
            raise ValueError("Invalid audio format")

        file_bytes = await file.read()

        with tempfile.NamedTemporaryFile(suffix=extension) as tmp:
            logger.debug(f"save audio to {tmp.name}")
            tmp.write(file_bytes)
            tmp.flush()

            logger.debug("Transcribing audio")
            result = SpeechToText.__model.transcribe(tmp.name)
            logger.debug(f"STT: {result['text']}")

        return result["text"]

