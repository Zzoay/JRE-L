
import json
import requests
import time

import openai

from constants import OPENAI_CONFIG


def get_response(usr_message, model="gpt-3.5-turbo", direct=False):
    if not direct:
        return get_response_ust([{"role": "user", "content":usr_message}], {"model": model})
    while True:
        try:
            completion = openai.ChatCompletion.create(model=model, temperature=1, messages=[{"role": "user", "content":usr_message}])
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
            with open('usage.txt', 'a') as f:
                f.write(f"{response['created']}\t{parameters['model']}\t{response['usage']}\n")
        except Exception as e:
            print(e)
            time.sleep(3)
            cnt += 1
            if cnt >= max_tries:
                break
            continue
        break
    return response['choices'][0]['message']['content'].strip()