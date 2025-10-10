class ProfanityCheck:
    def check_profanity(self, text: str) -> tuple[bool, list[str]]:
        """Check if the text contains profanity. To be implemented by subclasses.

        Args:
            text (str): The text to check.

        Returns:
            True/False, [list of profane words found] 
        """
        return True, []