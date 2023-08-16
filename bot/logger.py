from bot._logger import logger, setup_logger, LoggingLevel
from bot.config import CONFIG

setup_logger(CONFIG.LOGGING_LEVEL)
