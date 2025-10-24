import logging

APP_LOG_LEVEL = logging.DEBUG

def get_app_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(APP_LOG_LEVEL)
    return logger
