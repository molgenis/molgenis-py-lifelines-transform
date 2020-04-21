import logging
from os import path

from minio import Minio
from minio.error import ResponseError

log = logging.getLogger('transform')

def download_bucket(config):
    log.info('[download] connecting to host: %s' % config['s3']['hostname'])
    log.info('[download] select s3 bucket: %s' % config['s3']['bucket'])

    minioClient = Minio(
        config['s3']['hostname'],
        access_key=config['s3']['accessKey'],
        secret_key=config['s3']['secretKey'],
        secure=config['s3']['secure'],
        region=config['s3']['region'],
    )

    try:
        catalog_versions = list(minioClient.list_objects(config['s3']['bucket']))

        log.info('[download] latest catalog versions:')
        for version in catalog_versions[-5:]:
            log.info(' - %s' % version.object_name)

        # (!) Assumes the object names are alphabetically ordered.
        if (config['catalog_folder'] == 'latest'):
            s3_folder = catalog_versions[-1].object_name
        else:
            s3_folder = config['catalog_folder']

        log.info('[download] target s3 catalog: %s' % s3_folder)
        files = minioClient.list_objects(config['s3']['bucket'], prefix=s3_folder, recursive=True)
        for file in files:
            target_file = path.join(config['src_dir'], file.object_name)
            log.info(' - %s' % file.object_name)
            minioClient.fget_object(config['s3']['bucket'], file.object_name, target_file)

    except ResponseError as err:
        log.error(err)
        exit(1)

    return s3_folder
