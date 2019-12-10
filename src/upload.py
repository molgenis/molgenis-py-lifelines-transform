import logging
import os

import zipfile

log = logging.getLogger(__name__)


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.basename(file))


def upload(config, target_dir):
    zipf = zipfile.ZipFile('lifelines.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(target_dir, zipf)
    zipf.close()
