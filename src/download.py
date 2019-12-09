import logging
from os import path

from minio import Minio
from minio.error import ResponseError

log = logging.getLogger(__name__)

def download_bucket(config, target_dir):
    minioClient = Minio(
        config['s3_hostname'],
        access_key=config['accessKey'],
        secret_key=config['secretKey'],
        secure=False
    )

    try:
        s3_folder = list(minioClient.list_objects(config['bucket']))[-1].object_name
        files = minioClient.list_objects(config['bucket'], prefix=s3_folder, recursive=True)
        for file in files:
            minioClient.fget_object(config['bucket'], file.object_name, path.join(target_dir, file.object_name))
            log.info('saving %s' % file.object_name)

    except ResponseError as err:
        log.error(err)
        exit(1)

    return s3_folder
