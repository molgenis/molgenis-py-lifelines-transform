import logging
import numpy as np
import pandas as pd

from os import path

log = logging.getLogger(__name__)


def transform_data(config, s3_folder):
    config['src_dir'] = path.join(config['src_dir'], s3_folder)
    log.info('{:<30} -> {}'.format('agegroup.csv', 'lifelines_age_group.tsv'))
    age_group = pd.read_csv(path.join(config['src_dir'], 'agegroup.csv'), engine='python')
    age_group.rename(columns={'AGEGROUP_ID': 'id', 'LABEL': 'name'}, inplace=True)
    age_group.to_csv(path.join(config['target_dir'], 'lifelines_age_group.tsv'), sep='\t', index=False)

    log.info('{:<30} -> {}'.format('gender.csv', 'lifelines_gender_group.tsv'))
    gender_group = pd.read_csv(path.join(config['src_dir'], 'gender.csv'), engine='python')
    gender_group.rename(
        columns={'GENDER_ID': 'id', 'LABEL': 'name'},
        inplace=True
    )
    gender_group['name'] = gender_group['name'].str.lower()
    gender_group.to_csv(path.join(config['target_dir'], 'lifelines_gender_group.tsv'), sep='\t', index=False)

    log.info('{:<30} -> {}'.format('assessment.csv', 'lifelines_assessment.tsv'))
    assessment = pd.read_csv(path.join(config['src_dir'], 'assessment.csv'), engine='python')
    assessment.rename(columns={'ASSESSMENT_ID': 'id', 'NAME': 'name'}, inplace=True)
    assessment.to_csv(path.join(config['target_dir'], 'lifelines_assessment.tsv'), sep='\t', index=False)

    log.info('{:<30} -> {}'.format('variable.csv', 'lifelines_section.tsv'))
    variable = pd.read_csv(path.join(config['src_dir'], 'variable.csv'), engine='python')
    sections = pd.concat(objs=[
        variable[['SECTION_NAME']],
        variable[['ALT_SECTION_NAME']].rename(columns={'ALT_SECTION_NAME': 'SECTION_NAME'})
    ]).dropna().drop_duplicates().sort_values(by=['SECTION_NAME'])\
        .rename(columns={'SECTION_NAME': 'name'}).reset_index()

    sections.to_csv(
        path.join(config['target_dir'], 'lifelines_section.tsv'),
        columns=['name'], sep='\t', index_label='id'
    )
    sections = pd.read_csv(path.join(config['target_dir'], 'lifelines_section.tsv'), sep='\t', engine='python')

    log.info('{:<30} -> {}'.format('variable.csv', 'lifelines_subsection.tsv'))
    variable = pd.read_csv(path.join(config['src_dir'], 'variable.csv'), engine='python')
    subsections = pd.concat(objs=[
        variable[['SUBSECTION_NAME']],
        variable[['ALT_SUBSECTION_NAME']].rename(columns={'ALT_SUBSECTION_NAME': 'SUBSECTION_NAME'})
    ]).dropna().drop_duplicates().sort_values(by=['SUBSECTION_NAME'])\
        .rename(columns={'SUBSECTION_NAME': 'name'}).reset_index()

    subsections.to_csv(
        path.join(config['target_dir'], 'lifelines_subsection.tsv'),
        columns=['name'], sep='\t', index_label='id'
    )

    subsections = pd.read_csv(path.join(config['target_dir'], 'lifelines_subsection.tsv'), sep='\t', engine='python')

    log.info('{:<30} -> {}'.format('variant.csv', 'lifelines_variant.tsv'))
    df = pd.read_csv(path.join(config['src_dir'], 'variant.csv'), engine='python')
    df.rename(columns={'VARIANT_ID': 'id', 'NAME': 'name', 'ASSESSMENT_ID': 'assessment_id'}, inplace=True)
    df.to_csv(
        path.join(config['target_dir'], 'lifelines_variant.tsv'),
        columns=['id', 'name', 'assessment_id'], sep='\t', index=False, float_format='%.f'
    )

    log.info('{:<30} -> {}'.format('variable.csv + whatwhen.csv', 'lifelines_variable.tsv'))
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

    log.info('{:<30} -> {}'.format('variable.csv', 'lifelines_tree.tsv'))
    variable = pd.read_csv(path.join(config['src_dir'], 'variable.csv'), engine='python')

    section_tree = pd.merge(variable, sections, left_on='SECTION_NAME', right_on='name', how='left').rename(columns={'id': 'section_id'})
    section_tree = pd.merge(section_tree, subsections, left_on='SUBSECTION_NAME', right_on='name', how='left').rename(columns={'id': 'subsection_id'})

    alt_section_tree = pd.merge(
        variable, sections, left_on='ALT_SECTION_NAME', right_on='name', how='left').rename(columns={'id': 'section_id'}
    )
    alt_section_tree = pd.merge(
        alt_section_tree, subsections, left_on='ALT_SUBSECTION_NAME', right_on='name', how='left'
    ).rename(columns={'id': 'subsection_id'})

    tree = pd.concat(objs=[
        section_tree[['section_id', 'subsection_id']],
        alt_section_tree[['section_id', 'subsection_id']],
        ], sort=False).dropna().astype({
            'section_id': 'int32',
            'subsection_id': 'int32',
        }).sort_values(by=['section_id', 'subsection_id']).drop_duplicates().reset_index()
    tree.to_csv(
        path.join(config['target_dir'], 'lifelines_tree.tsv'),
        columns=['section_id', 'subsection_id'], sep='\t', index_label='id'
    )

    log.info('{:<30} -> {}'.format('variable.csv', 'lifelines_subsection_variable.tsv'))
    variable = pd.read_csv(path.join(config['src_dir'], 'variable.csv'), engine='python')

    subvars = pd.merge(variable, subsections, left_on='SUBSECTION_NAME', right_on='name', how='left')\
        .rename(columns={'id': 'subsection_id', 'VARIABLE_ID': 'variable_id'})

    alt_subvars = pd.merge(
        variable, subsections, left_on='ALT_SUBSECTION_NAME', right_on='name', how='left')\
        .rename(columns={'id': 'subsection_id', 'VARIABLE_ID': 'variable_id'})

    subsection_variable = pd.concat(objs=[
        subvars[['subsection_id', 'variable_id']],
        alt_subvars[['subsection_id', 'variable_id']]
    ], sort=False).dropna().astype({
        'subsection_id': 'int32',
        'variable_id': 'int32',
    }).sort_values(by=['subsection_id', 'variable_id']).drop_duplicates().reset_index()
    subsection_variable.to_csv(path.join(config['target_dir'], 'lifelines_subsection_variable.tsv'),
                            columns=['subsection_id', 'variable_id'], sep='\t', index_label='id')

    log.info('{:<30} -> {}'.format('who.csv', 'lifelines_who.tsv'))
    who = pd.read_csv(path.join(config['src_dir'], 'who.csv'), engine='python')
    who.rename(
        columns={
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
            'gender_group', 'age_group_at_1a', 'age_group_at_2a', 'age_group_at_3a', 'year_of_birth',
            'subcohortgwas_group', 'subcohortugli_group', 'subcohortdeep_group', 'subcohortdag3_group'
        ],
        float_format='%.f', sep='\t',
        index_label='ll_nr'
    )

    log.info('{:<30} -> {}'.format('whowhen.csv', 'lifelines_who_when.tsv'))
    who_when = pd.read_csv(path.join(config['src_dir'], 'whowhen.csv'), engine='python')
    who['ll_nr'] = who.index

    who_when = pd.merge(who, who_when, on='PARTICIPANT_ID', how='inner')
    who_when.rename(columns={'VARIANT_ID': 'variant_id'}, inplace=True)
    who_when.to_csv(
        path.join(config['target_dir'], 'lifelines_who_when.tsv'),
        sep='\t', index_label='id', columns=['ll_nr', 'variant_id']
    )
