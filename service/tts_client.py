import requests
import os
import io

from utils import get_app_logger

logger = get_app_logger(__name__)


class TTSClient:
    DEFAULT_SPEED = 175

    def __init__(self):
        self.url = os.getenv("TTS_SERVICE_URL", "")
        logger.debug(f"URL={self.url}")


    def post(self, lang: str, gender: str, text: str, speed: int = DEFAULT_SPEED):
        if lang == "zh":
            lang = "cmn"
        
        payload = {
            "lang": lang,
            "gender": gender,
            "speed": speed,
            "text": text
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, json=payload)

        # Extract boundary from header
        content_type = response.headers.get("Content-Type", "")
        boundary = content_type.split("boundary=")[-1]
        boundary = boundary.strip()

        # Split parts
        parts = response.content.split(f"--{boundary}".encode())

        phonemes = ""
        buffer = io.BytesIO()

        for part in parts:
            if b"Content-Type: application/json" in part:
                body = part.split(b"\r\n\r\n", 1)[-1].strip()
                logger.debug(f"phonemes: {body}")
                phonemes = body
            elif b"Content-Type: audio/wav" in part:
                body = part.split(b"\r\n\r\n", 1)[-1].strip()
                buffer.write(body)
                buffer.seek(0)
                logger.debug(f"RECV {len(body)} audio bytes")

        return (phonemes, buffer)