
import json
import requests
import time

import openai

from constants import OPENAI_CONFIG


def get_response(history_messages, model="gpt-3.5-turbo-0613", direct=False):
    if not direct:
        return get_response_ust(history_messages, {"model": model})
    while True:
        try:
            completion = openai.ChatCompletion.create(model=model, temperature=1, messages=history_messages)
        except Exception as e:
            print(e)
            time.sleep(3)
            continue
        break
    return completion.choices[0].message.content.strip()

def get_response_ust(messages, parameters=None):
    url = OPENAI_CONFIG['openai_api_base']
    headers = {
        "Content-Type": "application/json",
        "Authorization": OPENAI_CONFIG['openai_api_key']
        }
    data = {
        "messages": messages,
        }
    if parameters is not None:
        data.update(parameters)
    max_tries, cnt = 3, 0
    while True:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data)).json()
            usage = response['usage']['total_tokens']
        except Exception as e:
            print(e)
            time.sleep(3)
            cnt += 1
            if cnt >= max_tries:
                break
            continue
        break
    return response['choices'][0]['message']['content'].strip()