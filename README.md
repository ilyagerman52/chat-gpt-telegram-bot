# Telegram bot Chat-GPT.

Bot uses gpt-3.5-turbo engine. https://t.me/acos_exam_gpt_bot

Help:
This bot uses gpt-3.5-turbo engine for generating responses for your messages.

Send your request as usual message. Bot will send a response soon. Use commands:
- /help - for call this help message;
- /profile - to see information about your profile; [unavailable now]
- /edit_profile - to edit profile: change parse mode; [unavailable now]
- /clear - to clear conversation history.

Bot made by A.B. group. avbudkova@gmail.com
tg: @adam_brancy


## How to run your own bot
1. Clone project.
2. Get openai token from https://openai.com.
3. Set environment variable OPENAI_API_KEY.
4. Create your bot in telegran by writing @BotFather and get token.
5. Set environment variable BOT_TOKEN.
6. Run your bot by `python main.py`.

Alternatively, you can run `BOT_TOKEN=<your telegram token> OPENAI_API_KEY=<your openai api key> python main.py`
