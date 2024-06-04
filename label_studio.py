
import yaml

from label_studio_sdk import Client

cfg = yaml.safe_load(open('config/label-studio.yaml', 'r'))

ls = Client(url=cfg['url'], api_key=cfg['api_key'])

print(ls.check_connection())
project = ls.get_project(id=1)
project.import_tasks('sample.json')