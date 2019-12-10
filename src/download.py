import logging
from os import path

from minio import Minio
from minio.error import ResponseError

log = logging.getLogger(__name__)

def download_bucket(config):
    log.info('downloading from s3 bucket: %s' % config['s3']['bucket'])

    minioClient = Minio(
        config['s3']['hostname'],
        access_key=config['s3']['accessKey'],
        secret_key=config['s3']['secretKey'],
        secure=False
    )

    try:
        s3_folder = list(minioClient.list_objects(config['s3']['bucket']))[-1].object_name
        files = minioClient.list_objects(config['s3']['bucket'], prefix=s3_folder, recursive=True)
        for file in files:
            target_file = path.join(config['project_dir'], config['target_dir'], file.object_name)
            minioClient.fget_object(config['s3']['bucket'], file.object_name, target_file)
            log.info('saving %s' % file.object_name)

    except ResponseError as err:
        log.error(err)
        exit(1)

    return s3_folder
