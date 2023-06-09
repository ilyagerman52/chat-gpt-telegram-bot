import openai
import telebot
from telebot import types
from keys import *
from sql_db import *


bot = telebot.TeleBot(telegram_token)
openai.api_key = openai_api_key


@bot.message_handler(commands=['start'])
def start_chat(message):
    user_id = message.chat.id
    username = message.from_user.full_name
    status = UserStatus.USER
    profile = Profile(user_id=user_id, username=username, parse_mode=ParseMode.MARKDOWN, status=status, key="")
    if not add_profile(profile):
        print("Error in creating new user")
        raise RuntimeError


@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(chat_id=message.chat_id, text="Help message")


@bot.message_handler(commands=['profile'])
def show_profile(message):
    user_id = message.chat.id
    profile = get_profile(user_id)
    username = profile.username
    pm = profile.parse_mode if profile.parse_mode != ParseMode.EMPTY else "None"
    status = 'admin' if profile.status == UserStatus.ADMIN else 'user'
    markup = types.InlineKeyboardMarkup()
    bot.send_message(chat_id=user_id, text=f"Профиль.\n\nИмя пользователя: {username}\nParse mode: {pm}\nStatus: {status}", reply_markup=markup)


@bot.message_handler(commands=['clear'])
def clear_conversation(message):
    user_id = message.chat.id
    clear_chat_history(user_id)
    bot.send_message(chat_id=user_id, text="History has been cleared.")


@bot.message_handler(commands=['settings'])
def settings(message):
    user_id = message.user_id
    markup = types.InlineKeyboardMarkup()
    btn_chg_pm = types.InlineKeyboardButton("Change parse mode", callback_data="set_chg_pm")
    btn_enter_key = types.InlineKeyboardButton("Enter key", callback_data="set_enter_key")
    markup.add(btn_chg_pm, btn_enter_key)
    bot.send_message(chat_id=user_id, text="Chose parameter that you want to change", reply_markup=markup)


@bot.callback_query_handler(lambda call: call.data[:4] == 'set_')
def edit_profile(call):
    if call.data == 'set_chg_pm':
        markup = types.InlineKeyboardMarkup()
        btn_none = types.InlineKeyboardButton("None", callback_data="pm_none")
        btn_html = types.InlineKeyboardButton("HTML", callback_data="pm_html")
        btn_md = types.InlineKeyboardButton("Markdown", callback_data="pm_md")
        markup.add(btn_none, btn_html, btn_md)
        bot.edit_message_text("Chose new parse mode value:", call.message.chat.id, reply_markup=markup)
    elif call.data == 'set_enter_key':
        raise NotImplementedError


@bot.callback_query_handler(lambda call: call.data[:3] == 'pm_')
def set_pm_value(call):
    new_value = ParseMode.EMPTY
    if call.data == 'pm_html':
        new_value = ParseMode.HTML
    elif call.data == 'pm_md':
        new_value = ParseMode.MARKDOWN
    update_profile(call.message.chat.id, Field.PARSE_MODE, new_value)


bot.polling()