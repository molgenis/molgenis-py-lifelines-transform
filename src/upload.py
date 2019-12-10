import logging
import os
from shutil import copyfile

import zipfile

log = logging.getLogger(__name__)


def upload(config):
    target_dir = os.path.join(config['project_dir'], config['target_dir'])
    attributes_src = os.path.join(config['project_dir'], 'meta', 'attributes.tsv')
    attributes_target = os.path.join(target_dir, 'attributes.tsv')
    copyfile(attributes_src, attributes_target)
    zipf = zipfile.ZipFile('lifelines.zip', 'w', zipfile.ZIP_DEFLATED)
    for filename in os.listdir(target_dir):
        (_, ext) = os.path.splitext(filename)
        if ext == '.tsv':
            zipf.write(os.path.join(target_dir, filename), filename)

    zipf.close()
