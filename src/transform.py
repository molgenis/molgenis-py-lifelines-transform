import logging
import json
import numpy as np
import pandas as pd
import sys

from os import path
from minio import Minio
from minio.error import ResponseError

FORMAT = '[%(levelname)s] %(asctime)-15s %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=FORMAT)
log = logging.getLogger(__name__)

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

minioClient = Minio(
    config['hostname'],
    access_key=config['accessKey'],
    secret_key=config['secretKey'],
    secure=False
)

try:
    s3_folder = list(minioClient.list_objects(config['bucket']))[-1].object_name
    files = minioClient.list_objects(config['bucket'], prefix=s3_folder, recursive=True)
    for file in files:
        minioClient.fget_object(config['bucket'], file.object_name, './%s/%s' % (config['src_dir'], file.object_name))
        log.info('saving %s' % file.object_name)

except ResponseError as err:
    log.error(err)
    exit(1)

# s3_folder = '20191120_10.38.13_catalogueWww/'

config['src_dir'] = path.join(config['src_dir'], s3_folder)

log.info('agegroup.csv                -> lifelines_age_group.tsv')
age_group = pd.read_csv(path.join(config['src_dir'], 'agegroup.csv'), engine='python')
age_group.rename(columns={'AGEGROUP_ID': 'id', 'LABEL': 'name'}, inplace=True)
age_group.to_csv(path.join(config['target_dir'], 'lifelines_age_group.tsv'), sep='\t', index=False)


log.info('gender.csv             -> lifelines_gender_group.tsv')
gender_group = pd.read_csv(path.join(config['src_dir'], 'gender.csv'), engine='python')
gender_group.rename(
    columns={'GENDER_ID': 'id', 'LABEL': 'name'},
    inplace=True
)
gender_group['name'] = gender_group['name'].str.lower()
gender_group.to_csv(path.join(config['target_dir'], 'lifelines_gender_group.tsv'), sep='\t', index=False)


log.info('assessment.csv               -> lifelines_assessment.tsv')
assessment = pd.read_csv(path.join(config['src_dir'], 'assessment.csv'), engine='python')
assessment.rename(columns={'ASSESSMENT_ID': 'id', 'NAME': 'name'}, inplace=True)
assessment.to_csv(path.join(config['target_dir'], 'lifelines_assessment.tsv'), sep='\t', index=False)


log.info('section.txt                  -> lifelines_section.tsv...')
df = pd.read_csv(path.join(config['src_dir'], 'section.txt'), sep='\t', engine='python')
df.rename(columns={'section_id': 'id'}, inplace=True)
df.to_csv(path.join(config['target_dir'], 'lifelines_section.tsv'), columns=['id', 'name'], sep='\t', index=False)

log.info('subsection.txt               -> lifelines_sub_section.tsv...')
df = pd.read_csv(path.join(config['src_dir'], 'subsection.txt'), sep='\t', engine='python')
df.rename(columns={'subsection_id': 'id'}, inplace=True)
df.to_csv(path.join(config['target_dir'], 'lifelines_sub_section.tsv'), columns=['id', 'name'], sep='\t', index=False)


log.info('variant.csv                  -> lifelines_variant.tsv...')
df = pd.read_csv(path.join(config['src_dir'], 'variant.csv'), engine='python')
df.rename(columns={'VARIANT_ID': 'id', 'NAME': 'name', 'ASSESSMENT_ID': 'assessment_id'}, inplace=True)
df.to_csv(
    path.join(config['target_dir'], 'lifelines_variant.tsv'),
    columns=['id', 'name', 'assessment_id'], sep='\t', index=False, float_format='%.f'
)

log.info('variable.csv + whatwhen.csv -> lifelines_variable.tsv...')
variable = pd.read_csv(path.join(config['src_dir'], 'variable.csv'), engine='python')
variable.rename(
    columns={
        'VARIABLE_ID': 'id',
        'VARIABLE_NAME': 'name',
        'LABEL': 'label',
        'DEFINITION_EN': 'definition_en',
        'DEFINITION_NL': 'definition_nl',
        'SUBVARIABLE_OF': 'subvariable_of'
    }, inplace=True
)

what_when = pd.read_csv(path.join(config['src_dir'], 'whatwhen.csv'), engine='python')
what_when.rename(columns={'VARIABLE_ID': 'id', 'VARIANT_ID': 'variant_id'}, inplace=True)
grouped = what_when.groupby('id').agg(
    variants=(
        'variant_id', lambda ids: ','.join(np.unique(ids.map(str)))
    )
).reset_index()

variable = pd.merge(variable, grouped, on='id', how='left')
variable.to_csv(
    path.join(config['target_dir'], 'lifelines_variable.tsv'),
    columns=['id', 'name', 'label', 'variants', 'definition_en', 'definition_nl', 'subvariable_of'],
    sep='\t', index=False, float_format='%.f'
)

log.info('variable.csv                 -> lifelines_tree.tsv')
variable = pd.read_csv(path.join(config['src_dir'], 'variable.csv'), engine='python')
subsections = variable[['section_id', 'subsection_id']]
alt_subsections = variable[['alt_section_id', 'alt_subsection_id']].dropna().astype(
    {'alt_section_id': 'int32', 'alt_subsection_id': 'int32'}).rename(columns={'alt_section_id': 'section_id',
                                                                               'alt_subsection_id': 'subsection_id'})
tree = pd.concat(objs=[subsections, alt_subsections], sort=False).sort_values(
    by=['section_id', 'subsection_id']).drop_duplicates().reset_index()
tree.to_csv(
    path.join(config['target_dir'], 'lifelines_tree.tsv'),
    columns=['section_id', 'subsection_id'], sep='\t', index_label='id'
)

log.info('variable.csv                 -> lifelines_subsection_variable.tsv')
variable = pd.read_csv(path.join(config['src_dir'], 'variable.csv'), engine='python')
subvars = variable[['subsection_id', 'variable_id']]
alt_subvars = variable[['alt_subsection_id', 'variable_id']].dropna().astype(
    {'alt_subsection_id': 'int32'}).rename(columns={'alt_subsection_id': 'subsection_id'})
subsection_variable = pd.concat(objs=[subvars, alt_subvars], sort=False).sort_values(
    by=['subsection_id', 'variable_id']).drop_duplicates().reset_index()
subsection_variable.to_csv(config['target_dir'] + 'lifelines_subsection_variable.tsv',
                           columns=['subsection_id', 'variable_id'], sep='\t', index_label='id')

log.info('who.csv                      -> lifelines_who.tsv')
who = pd.read_csv(path.join(config['src_dir'], 'who.csv'), engine='python')
who.rename(
    columns={
        'PARTICIPANT_ID': 'll_nr',
        'GENDER': 'gender_group',
        'AGE_GROUP_AT1A': 'age_group_at_1a',
        'AGE_GROUP_AT2A': 'age_group_at_2a',
        'AGE_GROUP_AT3A': 'age_group_at_3a',
        'DATE_OF_BIRTH': 'year_of_birth',
        'SUBCOHORTDAG3': 'subcohortdag3_group',
        'SUBCOHORTDEEP': 'subcohortdeep_group',
        'SUBCOHORTGWAS': 'subcohortgwas_group',
        'SUBCOHORTUGLI': 'subcohortugli_group'
    },
    inplace=True
)
who.to_csv(
    path.join(config['target_dir'], 'lifelines_who.tsv'),
    columns=[
        'll_nr', 'gender_group', 'age_group_at_1a', 'age_group_at_2a', 'age_group_at_3a', 'year_of_birth',
        'subcohortgwas_group', 'subcohortugli_group', 'subcohortdeep_group', 'subcohortdag3_group'
    ],
    float_format='%.f', sep='\t', index=False
)
# PARTICIPANT_ID,VARIANT_ID,GENDER_TXT,AGE_INT
log.info('whowhen.csv                 -> lifelines_who_when.tsv')
who_when = pd.read_csv(path.join(config['src_dir'], 'whowhen.csv'), engine='python')
who_when.rename(
    columns={
        'PARTICIPANT_ID': 'll_nr',
        'VARIANT_ID': 'variant_id'
    },
    inplace=True
)
who_when.to_csv(
    path.join(config['target_dir'], 'lifelines_who_when.tsv'),
    sep='\t', index_label='id', columns=['ll_nr', 'variant_id']
)
