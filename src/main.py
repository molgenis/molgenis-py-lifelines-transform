import json
import logging
import sys
import download
import upload

from transform import Transform

from os import path

log = logging.getLogger(__name__)

FORMAT = '[%(levelname)s] %(asctime)-15s %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)

project_dir = path.abspath(path.join(path.dirname(path.abspath(__file__)), '../'))

config_locations = [
    path.join(project_dir, 'config.json'),
    path.join(project_dir, '.config', 'config.json'),
]

for config_location in config_locations:
    if path.isfile(config_location):
        log.info('config found: %s' % config_location)
        with open(config_location, 'r') as config_file:
            config = json.load(config_file)
        break

config['project_dir'] = project_dir

s3_folder = download.download_bucket(config)

transform = Transform(config, s3_folder)
transform.transform_data()

upload.upload(config)
upload.set_permissions(config)
