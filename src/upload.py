import logging
import json
import os
import polling
import requests
from shutil import copyfile

import zipfile

log = logging.getLogger(__name__)

def upload(config):
    log.info('zipping transformed data')
    target_dir = os.path.join(config['project_dir'], config['target_dir'])
    attributes_src = os.path.join(config['project_dir'], 'meta', 'attributes.tsv')
    attributes_target = os.path.join(target_dir, 'attributes.tsv')
    copyfile(attributes_src, attributes_target)

    zip_src = os.path.join(os.path.join(config['project_dir'], 'lifelines.zip'))

    zipf = zipfile.ZipFile(zip_src, 'w', zipfile.ZIP_DEFLATED)

    for filename in os.listdir(target_dir):
        (_, ext) = os.path.splitext(filename)
        if ext == '.tsv':
            zipf.write(os.path.join(target_dir, filename), filename)

    zipf.close()

    entities = [
        'lifelines_age_group',
        'lifelines_assessment',
        'lifelines_gender_group',
        'lifelines_section',
        'lifelines_sub_section',
        'lifelines_subsection_variable',
        'lifelines_tree',
        'lifelines_variable',
        'lifelines_variable_enum',
        'lifelines_variant',
        'lifelines_who',
        'lifelines_who_when'
    ]

    log.info('deleting old data from molgenis host: %s', config['molgenis']['hostname'])
    json_headers = {'Content-Type': 'application/json', 'x-molgenis-token': config['molgenis']['token']}
    batch_del_endpoint = '%s/api/v2/sys_md_EntityType' % config['molgenis']['hostname']
    res = requests.delete(batch_del_endpoint, headers=json_headers, data=json.dumps({'entityIds': entities}))
    res.raise_for_status()

    log.info('importing new data to molgenis host: %s', config['molgenis']['hostname'])
    files = {'file': open(zip_src, 'rb')}
    multipart_headers = {'x-molgenis-token': config['molgenis']['token']}
    import_endpoint = '%s/plugin/importwizard/importFile?packageId=lifelines' % config['molgenis']['hostname']
    res = requests.post(import_endpoint, headers=multipart_headers, files=files)
    res.raise_for_status()

    batch_status_endpoint = '%s%s' % (config['molgenis']['hostname'], res.text)

    log.debug('waiting for import to finish')
    polling.poll(lambda: requests.get(batch_status_endpoint, headers=json_headers).json()['status'] != 'RUNNING',
                 step=20,
                 timeout=3600)
    res = requests.get(batch_status_endpoint, headers=json_headers)
    res.raise_for_status()

    res = res.json()
    batch_status = res['status']

    if batch_status != 'FINISHED':
        log.error('failed to import: %s' % json.dumps(res))
        raise Exception('failed to import:\n%s' % json.dumps(res))

    log.info('import completed with status: %s' % (batch_status))
    log.debug('batch response:\n%s' % json.dumps(res))
