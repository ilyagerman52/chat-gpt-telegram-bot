import openai
import telebot
from telebot import types
from keys import *
from sql_db import *
import time

bot = telebot.TeleBot(telegram_token)
openai.api_key = openai_api_key


@bot.message_handler(commands=['start'])
def start_chat(msg):
    user_id = msg.chat.id
    username = msg.from_user.full_name
    status = UserStatus.USER
    profile = Profile(user_id=user_id, username=username, parse_mode="Markdown", status=status, key="")
    if not add_profile(profile):
        with open("log.txt", "a") as logs:
            logs.write(f"[{datetime.now()}] Error in creating new user")
        print(f"[{datetime.now()}] Error in creating new user")
        raise RuntimeError()


@bot.message_handler(commands=['help'])
def show_help(msg):
    bot.send_message(chat_id=msg.chat_id,
                     text="Bot acos-exam gpt3.\n\n"
                          "This bot uses gpt-3.5-turbo engine for generating responses for your messages.\n\n"
                          "Send your response as usual message. Bot will send a response soon. Use commands:\n"
                          "/help - for call this help message;\n"
                          "/profile - to see information about your profile;\n"
                          "/edit_profile - to edit profile: change parse mode;\n"
                          "/clear - to clear conversation history.\n\n"
                          "Bot made by A.B. group. avbudkova@gmail.com")


@bot.message_handler(commands=['profile'])
def show_profile(msg):
    user_id = msg.chat.id
    profile = get_profile(user_id)
    username = profile.username
    pm = profile.parse_mode if profile.parse_mode is not None else "None"
    status = 'admin' if profile.status == UserStatus.ADMIN else 'user'
    markup = types.InlineKeyboardMarkup()
    bot.send_message(chat_id=user_id,
                     text=f"Profile.\n\nUsername: {username}\nParse mode: {pm}\nStatus: {status}",
                     reply_markup=markup)


@bot.message_handler(commands=['clear'])
def clear_conversation(msg):
    user_id = msg.chat.id
    clear_chat_history(user_id)
    bot.send_message(chat_id=user_id, text="History has been cleared.")


@bot.message_handler(commands=['settings'])
def settings(msg):
    user_id = msg.user_id
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
        raise NotImplementedError()


@bot.callback_query_handler(lambda call: call.data[:3] == 'pm_')
def set_pm_value(call):
    new_value = None
    if call[3:] != "none":
        new_value = call.data[3:]
    update_profile(call.message.chat.id, Field.PARSE_MODE, new_value)


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
