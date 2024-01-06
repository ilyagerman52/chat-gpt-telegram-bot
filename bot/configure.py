import os
import logging
import sys
import openai

import yaml
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from itertools import cycle

from database_connectivity import DataBase


def get_openai_key():
    with open("config.yml", 'r') as config:
        openai_keys = yaml.safe_load(config)['openai_api_keys']
        yield from cycle(openai_keys)


def get_client():
    for key in get_openai_key():
        yield openai.OpenAI(api_key=key)


_LOGGER = logging.Logger("default", level=20)
_handler = logging.StreamHandler(sys.stdout)
_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]  %(message)s')
_handler.setFormatter(formatter)
_LOGGER.addHandler(_handler)
_LOGGER.info("Initializing bot")
try:
    bot = Bot(token=os.environ['BOT_TOKEN'])
    dp = Dispatcher(bot)
    _LOGGER.info("bot has been initialized successfully")
except IndexError as e:
    _LOGGER.exception(e)
    raise
_LOGGER.info("Start initializing history_database")
database = DataBase("history_database", "database/profiles.db")
_LOGGER.info("history_database has been initialized")

_LOGGER.info("Setting openai api key")
try:
    client = get_client()
    _LOGGER.info("openai api key has been set successfully")
except IndexError as e:
    _LOGGER.exception(e)
    raise
