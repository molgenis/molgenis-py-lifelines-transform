import json
import logging
import sys
import download
import upload

from transform import Transform

from os import path

FORMAT = '[%(levelname)s] %(asctime)-15s %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)

project_dir = path.abspath(path.join(path.dirname(path.abspath(__file__)), '../'))
with open(path.join(project_dir, 'config.json'), 'r') as config_file:
    config = json.load(config_file)

target_dir = path.join(project_dir, config['target_dir'])
# s3_folder = download.download_bucket(config, target_dir)
s3_folder = '20191206_09.42.42_catalogueWww/'
transform = Transform(config, s3_folder)
transform.transform_data()

upload.upload(config, target_dir)
