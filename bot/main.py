import aiogram.types
import openai
from aiogram.utils import executor

from utils import HELP_MESSAGE, add_user, update_history
from gpt_engine import get_response
from configure import _LOGGER, database, dp, bot


@dp.message_handler(commands=['start', 'help'])
async def start_chat(msg: aiogram.types.Message):
    add_user(msg, database, _LOGGER)
    await msg.reply(HELP_MESSAGE)


@dp.message_handler(commands=['clear'])
async def clear_history(msg: aiogram.types.Message):
    user_id = msg.chat.id
    database.tables['history'].delete_data(condition=f"uid == {user_id}")
    _LOGGER.info(f"History has been cleaned for user {user_id}")
    await bot.send_message(user_id, 'History has been cleaned')


@dp.message_handler(content_types=['text'])
async def reply_message(msg: aiogram.types.Message):
    add_user(msg, database, _LOGGER)
    user_id = msg.chat.id
    _LOGGER.info(f"Got message from {user_id}")
    update_history(msg, database)
    history = database.tables['history'].get_data(f"uid == {user_id}", fields="content, is_bot_response").fetchall()
    try:
        response = get_response(history, _LOGGER)
    except openai.RateLimitError as e:
        _LOGGER.exception(e)
        await msg.reply("Please, wait and repeat your request later.")
        return
    response_msg = await msg.reply(response)
    update_history(response_msg, database)
    _LOGGER.info(f"Sent reply to {user_id}")


if __name__ == '__main__':
    _LOGGER.info("STARTING")
    executor.start_polling(dp)
