import openai
import telebot
from telebot import types
from keys import *
from sql_db import *
import time
import logging
import sys
from utils import HELP_MESSAGE


# region logger_setup
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(stream=sys.stderr)
file_handler = logging.FileHandler(filename="info.log")
formatter = logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
# endregion logger_setup

_logger.info("Start")

_logger.info("Initializing bot")
bot = telebot.TeleBot(telegram_token)
_logger.info("Bot has been initialized successfully")

_logger.info("Setting openai api key")
openai.api_key = openai_api_key
_logger.info("openai api key has been set successfully")


@bot.message_handler(commands=['start'])
def start_chat(msg):
    user_id = msg.chat.id
    username = msg.from_user.full_name
    _logger.info(f"Initializing new chat for user {username} with user_id {user_id}")
    status = UserStatus.USER
    profile = Profile(user_id=user_id, username=username, parse_mode="Markdown", status=status, key="")
    if not add_profile(profile):
        _logger.warning("Warning! Cannot create new user")
        raise RuntimeError()


@bot.message_handler(commands=['help'])
def show_help(msg):
    _logger.info(f"Sending `show_help` message: user_id={msg.chat_id}")
    try:
        bot.send_message(chat_id=msg.chat_id,
                         text=HELP_MESSAGE)
        _logger.info(f"Successfully sent `show_help` message: user_id={msg.chat_id}")
    except Exception as exc:
        _logger.exception("Cannot send message in `show_help`.")


@bot.message_handler(commands=['profile'])
def show_profile(msg):
    user_id = msg.chat.id
    profile = get_profile(user_id)
    username = profile.username
    pm = profile.parse_mode if profile.parse_mode is not None else "None"
    status = 'admin' if profile.status == UserStatus.ADMIN else 'user'
    markup = types.InlineKeyboardMarkup()
    _logger.info(f"Sending `show_profile` message: user_id={user_id}")
    try:
        bot.send_message(chat_id=user_id,
                         text=f"Profile.\n\nUsername: {username}\nParse mode: {pm}\nStatus: {status}",
                         reply_markup=markup)
        _logger.info(f"Sent `show_profile` message: user_id={user_id}")
    except Exception as exc:
        _logger.exception(f"Cannot send `show_profile` message: user_id={user_id}.")


@bot.message_handler(commands=['clear'])
def clear_conversation(msg):
    user_id = msg.chat.id
    if not clear_chat_history(user_id):
        _logger.info(f"History for user {user_id} has been cleared")
        reply_text = "History has been cleared."
    else:
        _logger.warning(f"Cannot clear history for user {user_id}")
        reply_text = "Cannot clear history."
    try:
        bot.send_message(chat_id=user_id, text=reply_text)
    except Exception as exc:
        _logger.exception(f"Cannot send `clear_conversation` message: user_id={user_id}.")


@bot.message_handler(commands=['settings'])
def settings(msg):
    user_id = msg.user_id
    markup = types.InlineKeyboardMarkup()
    btn_chg_pm = types.InlineKeyboardButton("Change parse mode", callback_data="set_chg_pm")
    btn_enter_key = types.InlineKeyboardButton("Enter key", callback_data="set_enter_key")
    markup.add(btn_chg_pm, btn_enter_key)
    try:
        bot.send_message(chat_id=user_id, text="Chose parameter that you want to change", reply_markup=markup)
    except Exception as exc:
        _logger.exception(f"Cannot send `settings` message: user_id:{user_id}.")


@bot.callback_query_handler(lambda call: call.data[:4] == 'set_')
def edit_profile(call):
    if call.data == 'set_chg_pm':
        markup = types.InlineKeyboardMarkup()
        btn_none = types.InlineKeyboardButton("None", callback_data="pm_none")
        btn_html = types.InlineKeyboardButton("HTML", callback_data="pm_html")
        btn_md = types.InlineKeyboardButton("Markdown", callback_data="pm_md")
        markup.add(btn_none, btn_html, btn_md)
        try:
            bot.edit_message_text("Chose new parse mode value:", call.message.chat.id, reply_markup=markup)
            _logger.info(f"Edited `edit_profile` message: user_id={call.message.chat.id}.")
        except Exception as exc:
            _logger.exception(f"Cannot edit `edit_profile` message: user_id={call.message.chat.id}.")
    elif call.data == 'set_enter_key':
        _logger.warning("Not implemented")
        raise NotImplementedError()


@bot.callback_query_handler(lambda call: call.data[:3] == 'pm_')
def set_pm_value(call):
    new_value = None
    if call[3:] != "none":
        new_value = call.data[3:]
    if update_profile(call.message.chat.id, Field.PARSE_MODE, new_value):
        _logger.info(f"Updated profile: user_id={call.message.chat.id}")
    else:
        _logger.warning(f"Cannot update profile: user_id={call.message.chat.id}")


@bot.message_handler(content_types=['text'])
def reply_message(msg):
    request_dt = datetime.now()
    user_id = msg.chat.id
    profile = get_profile(user_id)
    if profile.status == UserStatus.BLOCKED:
        bot.send_message(user_id,
                         "Sorry, you were banned. If you consider it is a mistake, please contact technical support.")
        return
    request_content = msg.text
    chat_history = get_chat_history(user_id)
    if chat_history is None:
        add_profile(Profile(user_id=user_id,
                            username=msg.from_user.username,
                            parse_mode="Markdown",
                            status=UserStatus.USER,
                            key=None))
    chat_history.append({"role": "user", "content": request_content})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=chat_history)
    response_content = response.choices[0]['message']
    pm = profile.parse_mode
    bot.send_message(user_id, response_content, parse_mode=pm)
    response_dt = datetime.now()
    add_message_chat(user_id, ChatMessage(role="user", content=request_content, dt=request_dt))
    add_message_chat(user_id, ChatMessage(role="system", content=response_content, dt=response_dt))


bot.polling()
