from configure import client


def get_response(history: list[tuple[str, str]], logger=None):
    new_client = next(client)
    if logger:
        logger.info(f"Generate answer using api_key={new_client.api_key}")
    cooked_history = [{'role': 'assistant' if record[1] else 'user', 'content': record[0]} for record in history]
    response = new_client.chat.completions.create(messages=cooked_history, model='gpt-3.5-turbo-16k')
    # response = new_client.chat.completions.create(messages=cooked_history, model='gpt-4')
    if logger:
        logger.info("Answer generated successfully")
    return response.choices[0].message.content
