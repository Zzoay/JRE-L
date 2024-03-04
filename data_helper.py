
import json
import os
import yaml

def load_origin_data():
    cfg = yaml.safe_load(open('config/common.yaml', 'r'))
    data_file = os.path.join(cfg['data_path'], cfg['test_file'])
    print(data_file)
    data = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            data.append(json.loads(line))
    return data

if __name__ == "__main__":
    load_origin_data()