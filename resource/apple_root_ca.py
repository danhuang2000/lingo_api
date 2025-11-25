import os
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from utils import get_app_logger

logger = get_app_logger(__name__)

class AppleRootCA:
    ROOT_CERT: str = None

    @classmethod
    def get_root_cert(cls) -> str:
        if cls.ROOT_CERT is None:
            path = os.getenv("APPLE_ROOT_CA_PATH")
            try:
                with open(path, 'rb') as file:
                    file_content = file.read()
                AppleRootCA.ROOT_CERT = x509.load_pem_x509_certificate(file_content, default_backend())
            except FileNotFoundError:
                logger.error(f"Apple Root CA file not found in {path}.")
            except Exception as e:
                print(f"can't read {path}: {e}")

        return cls.ROOT_CERT
