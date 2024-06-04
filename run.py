
import argparse
import json
import os
import re
import random
import time
import threading
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from multiprocessing import Process, Queue, Pool
from itertools import chain

import textstat
from tqdm import tqdm

from constants import CFG
from data_helper import load_origin_data, load_processed_data
from prompts import QUESTIONS_PROMPT,JOURNALIST_PROMPT, TEACHER_PROMPT, STUDENT_PROMPT, REVISION_PROMPT, EVAL_PROMPT, ADVICE_SUMMARY_PROMPT, JUDGE_PAIR_PROMPT
from utils import get_response, extract_section, extract_score, extract_points, extract_score_pair, find_idle_gpu


global_lock = threading.RLock()


def act(input_text, agent_type, model, top_p=0.9, port=8000):
    if agent_type == "questions_gen":
        prompt_template = QUESTIONS_PROMPT
    elif agent_type == "journalist":
        prompt_template = JOURNALIST_PROMPT
    elif agent_type == "teacher":
        prompt_template = TEACHER_PROMPT
    elif agent_type == "judge":
        prompt_template = JUDGE_PAIR_PROMPT
    elif agent_type == "student":
        prompt_template = STUDENT_PROMPT
    elif agent_type == "revision":
        prompt_template = REVISION_PROMPT
    elif agent_type == "summary":
        prompt_template = ADVICE_SUMMARY_PROMPT
    else:
        raise ValueError("Invalid agent type")
    
    if model == "gpt-3.5-turbo":
        return get_response(prompt_template, input_text, model=model, top_p=top_p, mode='1')
    elif model == "gpt-4":
        return get_response(prompt_template, input_text, model=model, top_p=top_p, mode='1')
    else:
        return get_response(prompt_template, input_text, mode='llama', model=f"{CFG['model_path']}/{model}/", top_p=top_p, port=port)

def process_batch(batch_data, step, start_idx, scores, new_articles, questions_list, advice_list, advice_cache, initial_articles):
    local_scores = {name: [0 for _ in range(len(scores[name]))] for name in scores}
    local_advice_list = [[]] * len(batch_data)
    local_new_articles = [""] * len(batch_data)
    local_questions_list = [""] * len(batch_data)

    lock = threading.Lock()
    def handle_item(i, item):
        if step == 0:
            with global_lock:
                item_s = item.find("### Content\n")
                content = item[item_s+len("### Content\n"):]
                local_scores["flesch_reading_ease"][0] += textstat.flesch_reading_ease(content)
                local_scores["smog_index"][0] += textstat.smog_index(content)
                local_scores["flesch_kincaid_grade"][0] += textstat.flesch_kincaid_grade(content)
                local_scores["coleman_liau_index"][0] += textstat.coleman_liau_index(content)
                local_scores["dale_chall_readability_score"][0] += textstat.dale_chall_readability_score(content)
                local_scores["gunning_fog"][0] += textstat.gunning_fog(content)
                local_scores["automated_readability_index"][0] += textstat.automated_readability_index(content)

        data_idx = start_idx + i
        if step == 0:
            press = act(f"# Input\n## Paper\n{item}\n\n# Output\n", agent_type="journalist", model="Qwen1.5-7B-Chat", top_p=0.4, port=journalist_port)
            new_article = extract_section(press, "Article").strip()
            local_questions_list[i] = ""
            local_new_articles[i] = new_article
        else:
            questions = questions_list[data_idx]
            new_article = new_articles[data_idx]

            advice_specific_general = "\n".join([f"{j+1}. {adv}" for j, adv in enumerate(chain(advice_list[data_idx], advice_cache))])
            advice_specific_general = f"## Advice\n{advice_specific_general}"
            input_wrap = f"# Input\n## Paper\n{item}\n{new_article}\n{advice_specific_general}\n\n# Output\n"
            press = act(input_wrap, agent_type="revision", model="Qwen1.5-7B-Chat", top_p=0.4, port=journalist_port)
            new_article = extract_section(press, "Revised Article").replace("Revised", "").strip()
            local_new_articles[i] = new_article

        with global_lock:
            local_scores["flesch_reading_ease"][step+1] += textstat.flesch_reading_ease(new_article)
            local_scores["smog_index"][step+1] += textstat.smog_index(new_article)
            local_scores["flesch_kincaid_grade"][step+1] += textstat.flesch_kincaid_grade(new_article)
            local_scores["coleman_liau_index"][step+1] += textstat.coleman_liau_index(new_article)
            local_scores["dale_chall_readability_score"][step+1] += textstat.dale_chall_readability_score(new_article)
            local_scores["gunning_fog"][step+1] += textstat.gunning_fog(new_article)
            local_scores["automated_readability_index"][step+1] += textstat.automated_readability_index(new_article)

        content_questions = f"# Input\n{new_article}\n\n# Output\n"
        answers = act(content_questions, agent_type="student", model="Qwen1.5-1.8B-Chat", top_p=0.4, port=reader_port)
        
        teacher_output = act(f"# Input\n## Paper\n{item}]\n{new_article}\n## Reading Notes\n{answers}\n\n# Output\n", agent_type="teacher", model="Qwen1.5-7B-Chat", top_p=0.4, port=editor_port)
        advice = extract_section(teacher_output, "Advice").strip()
        advice_points = [x for x in extract_points(advice) if x != '']
        local_advice_list[i] = advice_points

    threads = []
    for i, item in enumerate(batch_data):
        t = threading.Thread(target=handle_item, args=(i, item))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    
    return local_scores, local_advice_list, local_new_articles, local_questions_list, advice_cache

def run():
    scores = {
        "flesch_reading_ease": [0 for _ in range(total_steps+1)],
        "smog_index": [0 for _ in range(total_steps+1)],
        "flesch_kincaid_grade": [0 for _ in range(total_steps+1)],
        "coleman_liau_index": [0 for _ in range(total_steps+1)],
        "dale_chall_readability_score": [0 for _ in range(total_steps+1)],
        "gunning_fog": [0 for _ in range(total_steps+1)],
        "automated_readability_index": [0 for _ in range(total_steps+1)],
        "questeval": [0 for _ in range(total_steps+1)],
    }
    new_articles = []  # store each item's new article
    questions_list = []
    advice_list = []  # store each item's advice
    advice_cache = []  # cache the general advice

    initial_articles = [] # store the popular articles in the first round

    all_origin_data = load_origin_data()[:sample_nums] if sample_nums != -1 else load_origin_data()
    total_items = len(all_origin_data)
    for step in range(total_steps):
        print(f"Step {step+1}/{total_steps} \t {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=================================================================================================")
        
        # batch processing
        results = []
        # cnt = 0
        for start_idx in tqdm(range(0, total_items, batch_size)):
            end_idx = min(start_idx + batch_size, total_items)
            batch_data = all_origin_data[start_idx:end_idx]

            result = process_batch(batch_data, step, start_idx, scores, new_articles, questions_list, advice_list, advice_cache, initial_articles)
            advice_cache = result[-1]
            results.append(result)        
            # cnt += 1   

        # merge
        merged_results = []
        start_idx, end_idx = 0, 0
        for i, r in enumerate(results):
        #     merged_results.append(r)
            local_scores, local_advice_list, local_new_articles, local_questions_list, advice_cache = r
            if i == 0:
                start_idx = 0
                end_idx = len(local_new_articles)
            else:
                start_idx = end_idx
                end_idx += len(local_new_articles)
            for k in local_scores:
                if step == 0:
                    scores[k][0] += local_scores[k][0] / total_items
                scores[k][step+1] += local_scores[k][step+1] / total_items
            if step == 0:
                new_articles.extend(local_new_articles)
                questions_list.extend(local_questions_list)
                advice_list.extend(local_advice_list)

                initial_articles.extend(local_new_articles)
            else:
                new_articles[start_idx:end_idx] = local_new_articles
                advice_list[start_idx:end_idx] = local_advice_list
        
        print(scores)

    with open("scores.json", "w") as f:
        json.dump(scores, f, separators=(',', ':'), indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")

    parser.add_argument("--total-steps", type=int, default=3, help="Total number of steps")
    parser.add_argument("--sample-nums", type=int, default=-1, help="Number of samples, use -1 for all data")
    parser.add_argument("--batch-size", type=int, default=10, help="Size of each batch")
    parser.add_argument("--journalist-port", type=int, default=8000, help="Port for journalist model, should be the same of the running model")
    parser.add_argument("--reader-port", type=int, default=8001, help="Port for reader model, should be the same of the running model")
    parser.add_argument("--editor-port", type=int, default=8002, help="Port for editor model, should be the same of the running model")

    args = parser.parse_args()
    
    total_steps = args.total_steps
    sample_nums = args.sample_nums
    batch_size = args.batch_size
    journalist_port = args.journalist_port
    reader_port = args.reader_port
    editor_port = args.editor_port

    run()