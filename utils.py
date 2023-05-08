import openai



def generate_response(text, messages):
    messages.append({"role": "user", "content": text})
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )