import aiogram


HELP_MESSAGE = """
Hello!
I am bot, that uses gpt-model (version 3.5) for answer generation.
I can generate answers basing on data, collected before 2019, so i can miss some modern information.

To ask something just send a text of question to me and I will answer you no more that 40 seconds. You're allowed to write no more then two questions a minute.  

To delete context, use /clear command.

There is a channel with announcements. Please, subscribe, if you want to receive updates.
https://t.me/+C2jCvemaNWo5NGE6

If you found a bug, please contact us: @ilyagerman52 or @adam_brancy.
"""


def add_user(msg: aiogram.types.Message, database, logger=None):
    user_id = msg.chat.id
    username = msg.from_user.username
    new_flg = database.tables['profiles'].get_data(f"uid == {user_id}").fetchall() == []
    if new_flg:
        if logger:
            logger.info(f"Adding user {username} with user_id {user_id}")
        row = {
            'uid': user_id,
            'username': username,
            'first_name': msg.from_user.first_name,
            'full_name': msg.from_user.full_name,
            'premium_flg': bool(msg.from_user.is_premium),
        }
        if msg.from_user.last_name:
            row['last_name'] = msg.from_user.last_name
        database.tables['profiles'].add_row(row)


def update_history(msg: aiogram.types.Message, database):
    user_id = msg.chat.id
    content = msg.text
    dttm_request = msg.date.strftime("%Y-%m-%d %H-%M-%S")
    is_bot_response = msg.from_user.is_bot
    database.tables['history'].add_row({
        'uid': user_id,
        'content': content,
        'is_bot_response': is_bot_response,
        'dttm': dttm_request,
        'message_id': msg.message_id,
    })
