
import json
import os
import yaml
import re

def load_processed_data():
    cfg = yaml.safe_load(open('config/processed.yaml', 'r'))
    data_file = os.path.join(cfg['data_path'], cfg['test_file'])
    print(data_file)
    data = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            data.append(json.loads(line))
    return data

def load_origin_data():
    max_len = 1024
    cfg = yaml.safe_load(open('config/common.yaml', 'r'))
    data_file = os.path.join(cfg['data_path'], cfg['test_file'])
    # print(data_file)
    if "scitechnews" in cfg['data_path']:
        data = []
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = re.sub(r'@xcite\d+', '', line)
                data.append(json.loads(line))
        output_data = [f"""### Meta Info\nTitle: {data[i]['sc-title']}\n### Content\n{" ".join(data[i]['sc-abstract'].split(" ")[0:max_len])}""" for i in range(len(data))]
    elif "elife" in cfg['data_path'] or "plos" in cfg['data_path']:
        data = json.load(open(data_file, 'r', encoding='utf-8'))
        output_data = [f"""### Meta Info\nTitle: {data[i]['title']}\n### Content\n{" ".join(" ".join(data[i]['abstract']).split(" ")[0:max_len])}""" for i in range(len(data))]
    
    return output_data

def transfer_to_factory():
    data_file = "data/elife/train.json"
    # print(data_file)
    max_len = 1024
    if "scitechnews" in data_file:
        data = []
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = re.sub(r'@xcite\d+', '', line)
                data.append(json.loads(line))
    elif "elife" in data_file or "plos" in data_file:
        data = json.load(open(data_file, 'r', encoding='utf-8'))
        data = [
            # {
            #     "sc-abstract": f"# Input\n## Paper\n### Meta Info\nTitle: {data[i]['title']}\n### Content\n{' '.join(' '.join(data[i]['abstract']).split(' ')[0:max_len])}\n\n# Output\n",
            #     "pr-summary": "## Article\n" + " ".join(data[i]['summary']),
            # }
            {
                "sc-abstract": ' '.join(data[i]['abstract']),
                "pr-summary": ' '.join(data[i]['summary']),
            }
            for i in range(len(data))
        ]
    json.dump(data, open("elife_train.json", 'w', encoding='utf-8'))
    return 