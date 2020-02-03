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

config = None

for config_location in config_locations:
    if os.path.isfile(config_location):
        log.info('using config: %s' % config_location)
        with open(config_location, 'r') as config_file:
            config = json.load(config_file)
        break

if not config:
    log.error('config.json not found in any of the valid config locations:')
    for config_location in config_locations:
        log.error('=> %s' % config_location)
    exit(1)

config['project_dir'] = project_dir
config['src_dir'] = os.path.join(project_dir, config['src_dir'])
config['target_dir'] = os.path.join(project_dir, config['target_dir'])

if not os.path.exists(config['src_dir']):
    os.makedirs(config['src_dir'])

if not os.path.exists(config['target_dir']):
    os.makedirs(config['target_dir'])

log.info('download enabled: %s' % ('yes' if config['actions']['download'] else 'no'))
log.info('transform enabled: %s' % ('yes' if config['actions']['transform'] else 'no'))
log.info('upload enabled: %s' % ('yes' if config['actions']['upload'] else 'no'))

if config['actions']['download']:
    s3_folder = download.download_bucket(config)
else:
    catalogs = sorted(os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'catalog')))
    if (config['s3']['catalog_folder'] == 'latest'):
        s3_folder = catalogs[-1]
    else:
        s3_folder = config['s3']['catalog_folder']

if config['actions']['transform']:
    transform = Transform(config, s3_folder)
    transform.transform_data()

if config['actions']['upload']:
    upload.upload(config)
    upload.set_permissions(config)
