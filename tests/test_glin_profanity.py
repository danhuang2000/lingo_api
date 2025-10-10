from service.profanity.glin_profanity_check import GlinProfanityCheck

def test_glin_profanity_check():
    checker = GlinProfanityCheck(languages=["english", "spanish"], custom_words=["damn"])
    is_profane, profane_words = checker.check_profanity("This is a damn example")
    print(f"Is profane: {is_profane}, Profane words: {profane_words}")
    assert is_profane
    assert "damn" in profane_words


