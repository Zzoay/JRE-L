
import json
import requests
import time
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

import openai

from constants import OPENAI_CONFIG
from prompts import JOURNALIST_PROMPT, PROMPT_FOR_LLAMA


def get_response(prompt, model="gpt-3.5-turbo", mode='ust'):
    if mode == 'ust':
        return get_response_ust([{"role": "user", "content": usr_message}], {"model": model})
    if mode == 'llama':
        return get_response_llama(prompt)
    while True:
        try:
            completion = openai.ChatCompletion.create(model=model, temperature=1, messages=[{"role": "user", "content": prompt}])
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

def get_response_llama(prompt):
    url = "https://127.0.0.1:5000/predict"
    data = {"text": prompt}
    headers = {'Content-Type': 'application/json'} 
    output_text = requests.post(url, json=data, headers=headers, verify=False).json()['output_text']
    output_text = output_text[output_text.find('Output:')+7:]
    return output_text


if __name__ == "__main__":
    prompt_template = JOURNALIST_PROMPT.split("\n")[0]
    input_text = """
    {"article": "[AUTHOR] yunzhu li | massachusetts institute of technology [AUTHOR] jiajun wu | massachusetts institute of technology ", "pr_summary": "[CONTENT] [AUTHOR] [CONCLUSIONS] | [CONCLUSIONS] | [BACKGROUND] [METHODS] | [CONCLUSIONS] | [AUTHOR] [CONCLUSIONS] | [BACKGROUND] [SUMMARY] massachusetts institute of technology ( mit ) researchers have developed a particle interaction network that improves robots ' abilities to mold materials into target shapes , and to predict interactions with solid objects and liquids .\nthe learn - based particle simulator learns to capture how small portions of different materials , known as \" particles , \" interact when they are poked and prodded .\nthe model directly learns from data in cases where the underlying physics of the movements are uncertain or unknown , so a robot can use it as a guide to predict how liquids , rigid materials , and deformable materials will react to the force of its touch .\nas the robot handles the objects , the model helps further refine the robot 's control .\nsaid mit 's yunzhu li , \" humans have an intuitive physics model in our heads , where we can imagine how an object will behave if we push or squeeze it .\n... we want to build this type of intuitive model for robots to enable them to do what humans can do . \""}
    """
    print(get_response(PROMPT_FOR_LLAMA.format(system_prompt=prompt_template, user_prompt=input_text), mode='llama'))