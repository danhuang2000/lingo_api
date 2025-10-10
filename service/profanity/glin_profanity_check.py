from glin_profanity import Filter
from .profanity_check import ProfanityCheck

class GlinProfanityCheck(ProfanityCheck):
    def __init__(self, languages: list[str], custom_words: list[str] = [], ignore_words: list[str] = []):
        config = {
            "languages": languages,
            "replace_with": "***",
            "custom_words": custom_words,
            "ignore_words": ignore_words,
            "allow_obfuscated_match": True,
            "fuzzy_tolerance_level": 0.8
        }
        self.filter = Filter(config)

    def check_profanity(self, text):
        result = self.filter.check_profanity(text)
        return result["contains_profanity"], result["profane_words"]

