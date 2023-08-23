import sys

from dotenv import load_dotenv
from dynaconf import LazySettings
from loguru import logger

load_dotenv('.env')
config = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF=False)
logger.info('Settings loaded from .env')
logger.add(sys.stderr, level=config.LOG_LEVEL, colorize=False)
