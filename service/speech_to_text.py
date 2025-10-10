import logging
import tempfile
import whisper
from fastapi import UploadFile


logger = logging.getLogger(__name__)


class SpeechToText:
    __model = whisper.load_model("small")

    @staticmethod
    async def speech_to_text(file: UploadFile) -> str:
        if file.content_type not in ["audio/x-m4a", "audio/m4a", "audio/mpeg", "audio/wav"]:
            logger.info(f"Invalid audio format: {file.content_type}")
            raise ValueError("Invalid audio format")

        file_bytes = await file.read()

        with tempfile.NamedTemporaryFile(suffix=".m4a") as tmp:
            tmp.write(file_bytes)
            tmp.flush()

            result = SpeechToText.__model.transcribe(tmp.name)
            logger.debug(f"STT: {result['text']}")

        return result["text"]

