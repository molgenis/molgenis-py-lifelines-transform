from datetime import datetime, timedelta
import logging
import json
import os
import time

import download
from lifelines_transform import __version__
from transform import Transform
from upload import Upload


execution_start_time = time.time()
project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))

# Use UTC time for all logging.
logging.Formatter.converter = time.gmtime

log = logging.getLogger('transform')

# Format datetime in logs to ISO-String.
formatter = logging.Formatter('%(asctime)s.%(msecs)03dZ [%(levelname)s] %(message)s', '%Y-%m-%dT%H:%M:%S')

log_filename = 'transform-%s.log' % datetime.today().strftime('%Y-%m-%d')
file_handler = logging.FileHandler(os.path.join(project_dir, 'logs', log_filename))
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Default log level.
log.setLevel(logging.DEBUG)

log.addHandler(file_handler)
log.addHandler(console_handler)

log.info('transform version: %s' % __version__)

config_locations = [
    os.path.join(project_dir, 'config.json'),
    os.path.join(project_dir, '.config', 'config.json'),
]

config = None
for config_location in config_locations:
    if os.path.isfile(config_location):
        log.info('config file: %s' % config_location)
        with open(config_location, 'r') as config_file:
            config = json.load(config_file)
        break

if not config:
    log.error('config.json not found in any of the valid config locations:')
    for config_location in config_locations:
        log.error('=> %s' % config_location)
    exit(1)


log.info('loglevel: %s' % config['log_level'])
log.setLevel(getattr(logging, config['log_level']))

config['project_dir'] = project_dir
config['src_dir'] = os.path.join(project_dir, config['src_dir'])
config['target_dir'] = os.path.join(project_dir, config['target_dir'])

if not os.path.exists(config['src_dir']):
    os.makedirs(config['src_dir'])

if not os.path.exists(config['target_dir']):
    os.makedirs(config['target_dir'])

log.info('download from s3: %s' % ('yes' if config['actions']['download'] else 'no'))
log.info('transform data: %s' % ('yes' if config['actions']['transform'] else 'no'))
log.info('upload to molgenis: %s' % ('yes' if config['actions']['upload'] else 'no'))

try:
    if config['actions']['download']:
        catalog_folder = download.download_bucket(config)
    else:
        catalogs = sorted(os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'catalog')))
        if config['catalog_folder'] == 'latest':
            catalog_folder = catalogs[-1]
        else:
            catalog_folder = config['catalog_folder']
except Exception as e:
    log.error(e)
    exit(1)
else:
    log.info('selected catalog folder: %s' % catalog_folder)


if config['actions']['transform']:
    try:
        transform = Transform(config, catalog_folder)
        transform.transform_data()
    except Exception as e:
        log.error(e)
        exit(1)
    else:
        log.info('data transformed succesfully')

if config['actions']['upload']:
    if config['debug_mode']:
        # Data with errors is logged and skipped in debug mode.
        # Do not allow potentialy broken data to be uploaded to Molgenis.
        log.warn('upload is not allowed in debug mode')
    else:
        try:
            upload = Upload(config)
            upload.delete_molgenis_entities()
            upload.zip_transformed_data()
            upload.upload_transformed_data_zip()
            upload.set_entities_permissions()
            upload.set_entity_indexing_depth('lifelines_subsection_variable')
        except Exception as e:
            log.error(e)
            exit(1)

log.info('execution time: %s' % (timedelta(seconds=time.time() - execution_start_time)))
