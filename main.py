import telebot
from telebot import types
import openai
import json

from keys import *
from utils import *

bot = telebot.TeleBot(telegram_token)
openai.api_key = openai_api_key


@bot.message_handler(commands=['start', 'refresh'])
def create_profile(message):
    chat_id = message.chat.id
    try:
        with open('profiles.json', 'r') as profs:
            all_profs = json.load(profs)
    except FileNotFoundError:
        all_profs = dict()
    all_profs[str(chat_id)] = {"name": message.from_user.full_name, "parse_mode": "Markdown", "waiting_param": "None",
                               "chats": [{"role": "system", "content": "Hello"}]}
    with open('profiles.json', 'w') as profs:
        json.dump(all_profs, profs)
    call_profile(message)


@bot.message_handler(commands=['edit_profile'])
def edit_profile(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_name = types.InlineKeyboardButton(text="Имя", callback_data='change_name')
    btn_parse_mode = types.InlineKeyboardButton(text="Parse mode", callback_data='change_parse_mode')
    markup.add(btn_name, btn_parse_mode)
    bot.send_message(message.chat.id, "Выберите, что вы хотите изменить", reply_markup=markup)


@bot.message_handler(commands=['profile'])
def call_profile(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    first = types.InlineKeyboardButton(text="Выбрать чат", callback_data='chose_chat')
    second = types.InlineKeyboardButton(text="Настройки профиля", callback_data='settings')
    markup.add(first, second)
    with open('profiles.json', 'r') as profs:
        all_profs = json.load(profs)
    username = all_profs[str(chat_id)]["name"]
    bot.send_message(chat_id,
                     f"Profile.\n\nName: {username}\nPerson id: {chat_id}\n\nYou can chose chat from already existing or create new. Also you can delete existing chats.",
                     parse_mode='HTML', reply_markup=markup)

@bot.message_handler(commands=['clear'])
def call_clear(message):
    chat_id = message.chat.id
    with open("profiles.json", "r") as profs:
        all_profs = json.load(profs)
    all_profs[str(chat_id)]["chats"] = [{"role": "system", "content": "Hello"}]
    with open("profiles.json", "w") as profs:
        json.dump(all_profs, profs)
    bot.send_message(chat_id, "History has been cleared")

@bot.callback_query_handler(lambda call: True)
def reply_callback(call):
    if call.data[:7] == "change_":
        bot.send_message(call.message.chat.id, "Введите новое значение")
        with open('profiles.json', 'r') as profs:
            all_profs = json.load(profs)
        all_profs[str(call.message.chat.id)]["waiting_param"] = call.data[7:]
        with open('profiles.json', 'w') as profs:
            json.dump(all_profs, profs)


def set_waiting_param(message):
    with open('profiles.json', 'r') as profs:
        all_profs = json.load(profs)
    waiting_param = all_profs[str(message.chat.id)]["waiting_param"]
    all_profs[str(message.chat.id)][waiting_param] = message.text
    bot.send_message(message.chat.id, "Параметр успешно изменён")
    all_profs[str(message.chat.id)]["waiting_param"] = "None"
    with open('profiles.json', 'w') as profs:
        json.dump(all_profs, profs)
    call_profile(message)


@bot.message_handler(content_types=["text"])
def handle_text(user_input):
    chat_id = user_input.chat.id
    with open('profiles.json', 'r') as profs:
        all_profs = json.load(profs)
    if all_profs[str(chat_id)]["waiting_param"] != "None":
        set_waiting_param(user_input)
        return
    wait_message = bot.send_message(user_input.chat.id, "Please wait. GPT is generating answer...")
    parse_mode = all_profs[str(chat_id)]['parse_mode']
    conversation = all_profs[str(chat_id)]['chats']
    response = generate_response(user_input.text, conversation)
    result = response.choices[0]['message']
    all_profs[str(chat_id)]['chats'].append(result)
    with open('profiles.json', 'w') as profs:
        json.dump(all_profs, profs)
    if len(result['content']) > 4000:
        for x in range(0, len(result['content']), 4000):
            bot.send_chat_action(chat_id, "typing")
            bot.send_message(user_input.chat.id, result['content'][x:x + 4000], parse_mode=parse_mode)
    else:
        try:
            bot.send_message(user_input.chat.id, result['content'], parse_mode=parse_mode)
        except telebot.apihelper.ApiTelegramException as e_level1:
            print(e_level1)
            try:
                bot.send_message(user_input.chat.id, result['content'], parse_mode="HTML")
            except telebot.apihelper.ApiTelegramException as e_level2:
                print(e_level2)
                bot.send_message(user_input.chat.id, "Error in sending message")
        bot.delete_message(user_input.chat.id, wait_message.id)

while True:
    try:
        bot.polling()
    except Exception as e:
        print(e)
