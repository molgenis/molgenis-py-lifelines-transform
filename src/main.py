import logging
import json
import sys
import os

import download
from transform import Transform
import upload

log = logging.getLogger(__name__)

FORMAT = '[%(levelname)s] %(asctime)-15s %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)

project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))

config_locations = [
    os.path.join(project_dir, 'config.json'),
    os.path.join(project_dir, '.config', 'config.json'),
]

for config_location in config_locations:
    if os.path.isfile(config_location):
        log.info('config found: %s' % config_location)
        with open(config_location, 'r') as config_file:
            config = json.load(config_file)
        break

config['project_dir'] = project_dir
config['src_dir'] = os.path.join(project_dir, config['src_dir'])
config['target_dir'] = os.path.join(project_dir, config['target_dir'])

if not os.path.exists(config['src_dir']):
    os.makedirs(config['src_dir'])

if not os.path.exists(config['target_dir']):
    os.makedirs(config['target_dir'])

s3_folder = download.download_bucket(config)

transform = Transform(config, s3_folder)
transform.transform_data()

upload.upload(config)
upload.set_permissions(config)
