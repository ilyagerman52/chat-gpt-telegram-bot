import os
import sys
from datetime import datetime
import logging

import aiogram.types
import openai
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from utils import HELP_MESSAGE
from database_connectivity import DataBase
from utils import get_response

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
    openai.api_key = os.environ['OPENAI_API_KEY']
    client = openai.OpenAI()
    _LOGGER.info("openai api key has been set successfully")
except IndexError as e:
    _LOGGER.exception(e)
    raise


@dp.message_handler(commands=['start', 'help'])
async def start_chat(msg: aiogram.types.Message):
    user_id = msg.chat.id
    username = msg.from_user.username
    new_flg = database.tables['profiles'].get_data(f"uid == {user_id}").fetchall() == []
    if new_flg:
        _LOGGER.info(f"Initializing new chat for user {username} with user_id {user_id}")
        database.tables['profiles'].add_row({'uid': user_id, 'username': username})
    await msg.reply(HELP_MESSAGE)


@dp.message_handler(commands=['clear'])
async def clear_history(msg: aiogram.types.Message):
    user_id = msg.chat.id
    database.tables['history'].delete_data(condition=f"uid == {user_id}")


@dp.message_handler(content_types=['text'])
async def reply_message(msg: aiogram.types.Message):
    user_id = msg.chat.id
    content = msg.text
    _LOGGER.info(f"Got message from {user_id}")
    dttm_request = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    database.tables['history'].add_row({'uid': user_id, 'content': content, 'is_bot_response': False, 'dttm': dttm_request})
    history = database.tables['history'].get_data(f"uid == {user_id}", fields="content, is_bot_response").fetchall()
    try:
        response = get_response(client, history)
    except openai.RateLimitError as e:
        return
    await msg.reply(response)
    dttm_response = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    database.tables['history'].add_row({'uid': user_id, 'content': response, 'is_bot_response': True, 'dttm': dttm_response})


if __name__ == '__main__':
    _LOGGER.info("STARTING")
    executor.start_polling(dp)
