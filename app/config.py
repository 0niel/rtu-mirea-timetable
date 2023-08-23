import sys

from dotenv import load_dotenv
from dynaconf import LazySettings
from loguru import logger

logger.remove()
logger.add(sys.stderr, level='INFO', colorize=False)

load_dotenv('.env')
logger.info('Settings loaded from .env')

config = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF=False)

logger.remove()
logger.add(sys.stderr, level=config.LOG_LEVEL, colorize=False)
