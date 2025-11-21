
from utils import get_app_logger

logger = get_app_logger(__name__)

class CacheService:
    """
    Singleton implementation. TODO: distributed cache?
    """
    _instance = None
    _initialized = False


    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self):
        if not self._initialized:
            self.dictionary = {}
            CacheService._initialized = True


    def add(self, key: str, value: any) -> bool:
        if key in self.dictionary:
            logger.debug(f"key {key} already exist")
            return False

        self.dictionary[key] = value
        return True
    

    def set(self, key: str, value: any):
        self.dictionary[key] = value


    def get(self, key: str) -> any:
        if key in self.dictionary:
            return self.dictionary[key]       
        return None
    

    def contain(self, key: str) -> bool:
        return (key in self.dictionary)