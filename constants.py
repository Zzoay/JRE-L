
import json
import yaml

OPENAI_CONFIG = json.load(open('config/openai.json'))

CFG = yaml.load(open('config/common.yaml', 'r'), Loader=yaml.FullLoader)