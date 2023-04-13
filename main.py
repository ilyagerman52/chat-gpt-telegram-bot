import telebot
from telebot import types
import openai
import json

from keys import *

bot = telebot.TeleBot(telegram_token)
openai.api_key = openai_api_key


@bot.message_handler(commands=['start'])
def create_profile(message):
    chat_id = message.chat.id
    new_profile = {chat_id: {"name": "name", "parse_mode": "Markdown", "active_chat_id": 0, "max_chat_id": 0,
                             'chats': [[{"role": "system", "content": "Hello"}]]}}  # names will be soon
    with open('profiles.json', 'w') as profs:
        json.dump(new_profile, profs)
    bot.send_message(chat_id, "Доброе утро! Я готов вам помочь.")


@bot.message_handler(commands=['profile'])
def call_profile(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    first = types.InlineKeyboardButton(text="Выбрать чат", callback_data='chose_chat')
    second = types.InlineKeyboardButton(text="Настройки профиля", callback_data='settings')
    markup.add(first, second)
    bot.send_message(chat_id, "Выберите кнопку", parse_mode='Markdown', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == 'settings':
        pass
    elif call.data == 'chose_chat':
        with open('profiles.json', 'r') as profs:
            all_profs = json.load(profs)[str(chat_id)]
        markup = types.InlineKeyboardMarkup(row_width=2)
        new_chat_btn = types.InlineKeyboardButton(text="Новый чат", callback_data="create_new_chat")
        markup.add(new_chat_btn)
        btns = []
        for i in range(all_profs["max_chat_id"] + 1):
            btn = types.InlineKeyboardButton(text=str(i), callback_data="chat_" + str(i))
            btns.append(btn)
        markup.add(*btns)
        bot.send_message(chat_id, "Выберите чат", reply_markup=markup)

    elif call.data[:5] == 'chat_':
        with open('profiles.json', 'r') as profs:
            all_profs = json.load(profs)
        chat_number = int(call.data[5:])
        all_profs[str(chat_id)]["active_chat_id"] = chat_number
        with open('profiles.json', 'w') as profs:
            json.dump(all_profs, profs)
        bot.send_message(chat_id, "Выбран чат №" + str(chat_number))

    elif call.data == 'create_new_chat':
        with open('profiles.json', 'r') as profs:
            all_profs = json.load(profs)
        new_chat = [{"role": "system", "content": "Hello"}]
        all_profs[str(chat_id)]["chats"].append(new_chat)
        all_profs[str(chat_id)]["max_chat_id"] += 1
        with open('profiles.json', 'w') as profs:
            json.dump(all_profs, profs)
        bot.send_message(chat_id, "Новый чат создан")



def chat(text, messages):
    messages.append({"role": "user", "content": text})
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )


@bot.message_handler(content_types=["text"])
def handle_text(user_input):
    chat_id = user_input.chat.id
    bot.send_chat_action(chat_id, "typing", 10)
    # profile = None
    with open('profiles.json', 'r') as profs:
        all_profs = json.load(profs)

    parse_mode = all_profs[str(chat_id)]['parse_mode']
    active_chat_id = all_profs[str(chat_id)]['active_chat_id']
    conversation = all_profs[str(chat_id)]['chats'][active_chat_id]
    response = chat(user_input.text, conversation)
    result = response.choices[0]['message']
    all_profs[str(chat_id)]['chats'][active_chat_id].append(result)
    with open('profiles.json', 'w') as profs:
        json.dump(all_profs, profs)
    if len(result['content']) > 2048:
        for x in range(0, len(result['content']), 2048):
            bot.send_chat_action(chat_id, "typing")
            bot.send_message(user_input.chat.id, result['content'][x:x + 2048], parse_mode="Markdown")
    else:
        bot.send_chat_action(chat_id, "typing")
        bot.send_message(user_input.chat.id, result['content'], parse_mode="Markdown")


bot.polling()
