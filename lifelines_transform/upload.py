import logging
import json
import os
import polling
import requests
from shutil import copyfile

import zipfile

log = logging.getLogger(__name__)

def upload(config):
    log.info('[upload] using molgenis host: %s', config['molgenis']['hostname'])
    log.info('[upload] zip transformed data')
    attributes_src = os.path.join(config['project_dir'], 'meta', 'attributes.tsv')
    attributes_target = os.path.join(config['target_dir'], 'attributes.tsv')
    copyfile(attributes_src, attributes_target)

    zip_src = os.path.join(os.path.join(config['project_dir'], 'lifelines.zip'))

    zipf = zipfile.ZipFile(zip_src, 'w', zipfile.ZIP_DEFLATED)

    for filename in os.listdir(config['target_dir']):
        (_, ext) = os.path.splitext(filename)
        if ext == '.tsv':
            zipf.write(os.path.join(config['target_dir'], filename), filename)

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

    log.info('[upload] delete old dataset from molgenis')
    json_headers = {'Content-Type': 'application/json', 'x-molgenis-token': config['molgenis']['token']}
    batch_del_endpoint = '%s/api/v2/sys_md_EntityType' % config['molgenis']['hostname']

    res = requests.delete(batch_del_endpoint, headers=json_headers, data=json.dumps({'entityIds': entities}))
    res.raise_for_status()

    log.info('[upload] send new dataset to molgenis')
    files = {'file': open(zip_src, 'rb')}
    multipart_headers = {'x-molgenis-token': config['molgenis']['token']}
    import_endpoint = '%s/plugin/importwizard/importFile?packageId=lifelines' % config['molgenis']['hostname']
    res = requests.post(import_endpoint, headers=multipart_headers, files=files)
    res.raise_for_status()

    batch_status_endpoint = '%s%s' % (config['molgenis']['hostname'], res.text)

    log.debug('[upload] importing...')
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

    log.info('[upload] import finished with status: %s' % (batch_status))
    log.debug('batch response:\n%s' % json.dumps(res))

    log.info('[upload] modify indexing depth of subsection_variable to 2')
    indexing_endpoint = '%s/api/v2/sys_md_EntityType/indexingDepth' % config['molgenis']['hostname']
    indexing_payload = {
        'entities': [
            {"id": "lifelines_subsection_variable", "indexingDepth": 2}
        ]
    }
    res = requests.put(indexing_endpoint, headers=json_headers, data=json.dumps(indexing_payload))
    res.raise_for_status()

def set_permissions(config):
    entitytype_permissions = {
        'objects': [
            {'objectId': 'lifelines_who', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'COUNT'}]},
            {'objectId': 'lifelines_who_when', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'COUNT'}]},

            {'objectId': 'sys_L10nString', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
            {'objectId': 'lifelines_variable', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
            {'objectId': 'lifelines_section', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
            {'objectId': 'lifelines_assessment', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
            {'objectId': 'lifelines_age_group', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
            {'objectId': 'lifelines_sub_section', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
            {'objectId': 'lifelines_tree', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
            {'objectId': 'lifelines_variant', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
            {'objectId': 'lifelines_subsection_variable', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
            {'objectId': 'lifelines_variable_enum', 'permissions': [{'role': 'ANONYMOUS', 'permission': 'READ'}]},
        ]
    }

    json_headers = {'Content-Type': 'application/json', 'x-molgenis-token': config['molgenis']['token']}
    grant_endpoint = '%s/api/permissions/entityType' % config['molgenis']['hostname']
    res = requests.post(grant_endpoint, headers=json_headers, data=json.dumps(entitytype_permissions))
    res.raise_for_status()
