
import json
import re
import requests
import time
from collections import OrderedDict
from datetime import datetime

import gpustat
import openai

from constants import OPENAI_CONFIG
from prompts import JOURNALIST_PROMPT, PROMPT_FOR_LLAMA, STUDENT_PROMPT, TEACHER_PROMPT


def get_response(prompt, input_text, model="gpt-3.5-turbo", mode='ust', port=8000, top_p=0.9):
    if mode in ['ust', 'llama']:
        return ger_response_url(
            # [{"role": "system", "content": prompt}, {"role": "user", "content": input_text}],
            [{"role": "user", "content": prompt + '\n' + input_text}],
            mode=mode, parameters={"model": model, "top_p": top_p}, port=port)
    while True:
        try:
            completion = openai.ChatCompletion.create(model=model, top_p=top_p, messages=[{"role": "user", "content": prompt + '\n' + input_text}])
        except Exception as e:
            print(e)
            time.sleep(3)
            continue
        break
    return completion.choices[0].message.content.strip()

def ger_response_url(messages, mode, parameters=None, port=8000):
    if mode == 'ust':
        url = OPENAI_CONFIG['openai_api_base']
        headers = {
        "Content-Type": "application/json",
        "Authorization": OPENAI_CONFIG['openai_api_key']
        }
    elif mode == 'llama':
        url = f"http://0.0.0.0:{port}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            }
    else:
        raise ValueError("Invalid mode")
    data = {
        "messages": messages,
        "max_tokens": 2048,
        "frequency_penalty": 1,
        "repetition_penalty": 1,
        # "stop_token_ids": [128001, 128009]
        }
    if parameters is not None:
        data.update(parameters)
    max_tries, cnt = 5, 0
    while True:
        try:
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response = requests.post(url, headers=headers, data=json.dumps(data)).json()
            with open('usage.txt', 'a') as f:
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                usage = dict(OrderedDict(sorted(response['usage'].items(), key=lambda x: x[0])))
                f.write(f"{start_time}\t{end_time}\t{parameters['model']}\t{usage}\n")
            if has_chinese(response['choices'][0]['message']['content']):
                time.sleep(3)
                cnt += 1
                if cnt >= max_tries:
                    return remove_chinese(response['choices'][0]['message']['content'])
                continue
            if len(response['choices'][0]['message']['content'].strip().split(" ")) < 100:
                time.sleep(3)
                cnt += 1
                if cnt >= max_tries:
                    # return the original paper
                    return messages[0]['content'][messages[0]['content'].find("### Content")+len("### Content"):]
                continue
        except Exception as e:
            print(e)
            print(response)
            time.sleep(5 + cnt**2)
            cnt += 1
            if cnt >= max_tries:
                # return the original paper
                return messages[0]['content'][messages[0]['content'].find("### Content")+len("### Content"):]
            continue
        break
    return response['choices'][0]['message']['content'].strip()

# def extract_section(text, term):
#     start_index = text.find(f"[{term.upper()}_START]")
#     end_index = text.find(f"[{term.upper()}_END]")
#     if start_index != -1:
#         if end_index != -1:
#             terms = text[start_index:end_index + len(f"[{term.upper()}_END]")]
#             return '\n' + terms.strip()
#         # if end not found
#         pattern = r"\[(.*?)_START\]"
#         matches = list(re.finditer(pattern, text[start_index + len(f"[{term.upper()}_START]"):]))
#         if len(matches) != 0:
#             new_start_index = matches[0].start()
#             terms = text[start_index:new_start_index + start_index + len(f"[{term.upper()}_START]")]
#         else:
#             terms = text[start_index:]
#         return '\n' + terms.strip()
#     # if term.upper() == "ADVICE":  # advice is special, if match nothing, return ""
#     #     return ""
#     return text

def extract_section(text, term):
    start_index = text.find(f"## {term}")
    if start_index != -1:
        # if end not found
        pattern = r"##\s\w+\n"
        matches = list(re.finditer(pattern, text[start_index + len(f"## {term}"):]))
        if len(matches) != 0:
            new_start_index = matches[0].start()
            terms = text[start_index:new_start_index + start_index + len(f"## {term}")]
        else:
            terms = text[start_index:]
        return '\n' + terms.strip()
    if term == "Advice": # advice is special, if match nothing, return ""
        return ""
    return text

# def extract_score(text, dim):
#     # find all [[]] pattern
#     pattern = r'\[\[(\d+)\]\]'
#     matches = re.findall(pattern, text)
#     if len(matches) >= 3:
#         if dim.upper() == "ACCURACY":
#             return int(matches[0])
#         elif dim.upper() == "ACCESSIBILITY":
#             return int(matches[1])
#         elif dim.upper() == "INFORMATION":
#             return int(matches[2])
#     return 3.0

def extract_score(text, dim):
    score_dct = {"poor": 1, "fair": 2, "good": 3, "excellent": 4, "perfect": 5}
    pattern = r'\[\[(.*?)\]\]'
    factors = text.split("\n")
    if len(factors) == 3:
        if dim.upper() == "ACCURACY":
            text = factors[0]
        elif dim.upper() == "ACCESSIBILITY":
            text = factors[1]
        elif dim.upper() == "INFORMATION":
            text = factors[2]
        matches = re.findall(pattern, text)
        if len(matches) != 0:
            return score_dct.get(matches[0].lower(), 2.5)
    
    matches = re.findall(pattern, text)
    if len(matches) >= 3:
        if dim.upper() == "ACCURACY":
            return score_dct.get(matches[0].lower(), 2.5)
        elif dim.upper() == "ACCESSIBILITY":
            return score_dct.get(matches[1].lower(), 2.5)
        elif dim.upper() == "INFORMATION":
            return score_dct.get(matches[2].lower(), 2.5)
    return 2.5

def extract_score_pair(text, exchange=False):
    # [[x]]
    pattern = r'\[\[(.*?)\]\]'
    matches = re.findall(pattern, text)
    if len(matches) >= 1:
        m = matches[0]
        if m.upper() == 'A':
            return 0 if not exchange else 1
        elif m.upper() == 'B':
            return 1 if not exchange else 0
    
    # [x]
    pattern = r'\[(.*?)\]'
    matches = re.findall(pattern, text)
    if len(matches) >= 1:
        m = matches[0]
        if m.upper() == 'A':
            return 0 if not exchange else 1
        elif m.upper() == 'B':
            return 1 if not exchange else 0
    # x
    a_count = text.count("Article A")
    b_count = text.count("Article B")
    if a_count > b_count:
        return 0 if not exchange else 1
    else:
        return 1 if not exchange else 0
    print("Not match")
    return 0


def extract_points(text):
    pattern = r"\d+\.\s*(.*?)(?=\n\d+\.|\Z|\n)"

    matches = re.findall(pattern, text)

    if len(matches) == 0:
        res = text.split("\n")
        if len(res) != 0:
            return [x.replace("[ADVICE_END]", "").replace("[ADVICE_START]", "").strip() for x in res]
        return []

    return [match.replace("[ADVICE_END]", "").replace("[ADVICE_START]", "").strip() for match in matches]

def has_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    return bool(pattern.search(text))

def remove_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    return pattern.sub('', text)

def find_idle_gpu():
    gpu_stats = gpustat.new_query()
    for gpu in gpu_stats:
        utilization = gpu.utilization
        if utilization < 5:
            # print(f"GPU {gpu.index}: Utilization {utilization}%")
            return gpu.index
    return None