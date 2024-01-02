import openai

HELP_MESSAGE = """Bot with gpt-3.5-turbo engine.
Команды:
/clear - очистить историю сообщений
/help - вывод справки
Просто напишите текст запроса, чтобы получить ответ от gpt-модели
Bot made by A.B. group. avbudkova@gmail.com
"""


def get_response(client: openai.OpenAI, history: list[tuple[str, str]]):
    cooked_history = [{'role': 'system' if record[1] else 'user', 'content': record[0]} for record in history]
    response = client.chat.completions.create(messages=cooked_history, model='gpt-3.5-turbo')
    return response.choices[0].message.content
