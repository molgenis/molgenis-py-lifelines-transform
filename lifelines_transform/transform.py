import logging
import numpy as np
import pandas as pd

from os import path

log = logging.getLogger('transform')


class Transform:
    def __init__(self, config, s3_folder):
        self.config = config
        self.s3data_dir = path.join(self.config['src_dir'], s3_folder)

    def _subsection_list(self, x):
        colnames = ['subsection_id', 'alt_subsection_id']
        subsections = [str(int(x[colname])) for colname in colnames if not np.isnan(x[colname])]
        return ','.join(subsections)

    def transform_data(self):
        log.info('[transform] lifelines (csv) to molgenis (tsv):')
        self.transform_agegroup()
        self.transform_gendergroup()
        self.transform_assessment()

        sections = self.transform_section()
        subsections = self.transform_sub_section()

        self.transform_tree(sections, subsections)
        self.transform_subsection_variable(subsections)

        self.transform_variable_enum()
        self.transform_variant()
        self.transform_variable_whatwhen(subsections)

        who = self.transform_who()
        self.transform_whowhen(who)

    def transform_agegroup(self):
        log.info(' - agegroup.tsv')
        age_group = pd.read_csv(
            path.join(self.s3data_dir, 'agegroup.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )
        age_group.rename(columns={'AGEGROUP_ID': 'id', 'LABEL': 'name'}, inplace=True)
        age_group.to_csv(path.join(self.config['target_dir'], 'age_group.tsv'), sep='\t', index=False)

    def transform_gendergroup(self):
        log.info(' - gender_group.tsv')
        gender_group = pd.read_csv(
            path.join(self.s3data_dir, 'gender.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )
        gender_group.rename(
            columns={'GENDER_ID': 'id', 'LABEL': 'name'},
            inplace=True
        )
        gender_group['name'] = gender_group['name'].str.lower()
        gender_group.to_csv(path.join(self.config['target_dir'], 'gender_group.tsv'), sep='\t', index=False)

    def transform_assessment(self):
        log.info(' - assessment.tsv')
        assessment = pd.read_csv(
            path.join(self.s3data_dir, 'assessment.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )
        assessment.rename(columns={'ASSESSMENT_ID': 'id', 'NAME': 'name'}, inplace=True)
        assessment.to_csv(path.join(self.config['target_dir'], 'assessment.tsv'), sep='\t', index=False)

    def transform_section(self):
        log.info(' - section.tsv')
        variable = pd.read_csv(
            path.join(self.s3data_dir, 'variable.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )
        sections = pd.concat(objs=[
            variable[['SECTION_NAME']],
            variable[['ALT_SECTION_NAME']].rename(columns={'ALT_SECTION_NAME': 'SECTION_NAME'})
        ]).dropna().drop_duplicates().sort_values(by=['SECTION_NAME'])\
            .rename(columns={'SECTION_NAME': 'name'}).reset_index()
        sections['id'] = sections.index
        sections.to_csv(
            path.join(self.config['target_dir'], 'section.tsv'),
            columns=['id', 'name'], sep='\t', index=False
        )

        return sections

    def transform_sub_section(self):
        log.info(' - sub_section.tsv')
        variable = pd.read_csv(
            path.join(self.s3data_dir, 'variable.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )
        subsections = pd.concat(objs=[
            variable[['SUBSECTION_NAME', 'WIKI_HYPERLINK']],
            variable[['ALT_SUBSECTION_NAME', 'WIKI_HYPERLINK']]
            .rename(columns={'ALT_SUBSECTION_NAME': 'SUBSECTION_NAME'}),
        ]).dropna(how='all', subset=['SUBSECTION_NAME']) \
          .drop_duplicates(subset=['SUBSECTION_NAME']) \
          .sort_values(by=['SUBSECTION_NAME']) \
          .rename(columns={'SUBSECTION_NAME': 'name'}) \
          .rename(columns={'WIKI_HYPERLINK': 'wiki'}) \
          .reset_index()
        subsections['id'] = subsections.index
        subsections.to_csv(
            path.join(self.config['target_dir'], 'sub_section.tsv'),
            columns=['id', 'name', 'wiki'], sep='\t', index=False
        )

        subsections.drop(columns=['wiki'], inplace=True)

        return subsections

    def transform_variable_enum(self):
        log.info(' - variable_enum.tsv')
        variable_enum = pd.read_csv(
            path.join(self.s3data_dir, 'variable-enumeration.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode'], na_filter=False
        )
        variable_enum.rename(columns={
            'VARIABLE_ID': 'variable',
            'ENUMERATION_CODE': 'code',
            'ENUMERATION_NL': 'label_nl',
            'ENUMERATION_EN': 'label_en'
        }, inplace=True)
        variable_enum.to_csv(path.join(self.config['target_dir'], 'variable_enum.tsv'), sep='\t', index=False)

    def transform_variant(self):
        log.info(' - variant.tsv')
        df = pd.read_csv(
            path.join(self.s3data_dir, 'variant.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )
        df.rename(columns={'VARIANT_ID': 'id', 'NAME': 'name', 'ASSESSMENT_ID': 'assessment_id'}, inplace=True)
        df.to_csv(
            path.join(self.config['target_dir'], 'variant.tsv'),
            columns=['id', 'name', 'assessment_id'], sep='\t', index=False, float_format='%.f'
        )

    def transform_variable_whatwhen(self, subsections):
        log.info(' - variable.tsv')
        variable = pd.read_csv(
            path.join(self.s3data_dir, 'variable.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )

        variable = pd.merge(variable, subsections, left_on='SUBSECTION_NAME', right_on='name', how='left')\
            .rename(columns={'id': 'subsection_id'})

        variable = pd.merge(variable, subsections, left_on='ALT_SUBSECTION_NAME', right_on='name', how='left')\
            .rename(columns={'id': 'alt_subsection_id'})

        variable['subsections'] = variable.apply(self._subsection_list, axis=1)

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

        what_when = pd.read_csv(
            path.join(self.s3data_dir, 'whatwhen.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )
        what_when.rename(columns={'VARIABLE_ID': 'id', 'VARIANT_ID': 'variant_id'}, inplace=True)
        grouped = what_when.groupby('id').agg(
            variants=(
                'variant_id', lambda ids: ','.join(np.unique(ids.map(str)))
            )
        ).reset_index()

        variable = pd.merge(variable, grouped, on='id', how='left')
        variable.to_csv(
            path.join(self.config['target_dir'], 'variable.tsv'),
            columns=[
                'id', 'name', 'label', 'variants', 'definition_en',
                'definition_nl', 'subvariable_of', 'subsections'
            ],
            sep='\t', index=False, float_format='%.f'
        )
        return variable

    def transform_tree(self, sections, subsections):
        log.info(' - tree.tsv')
        variable = pd.read_csv(
            path.join(self.s3data_dir, 'variable.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        ).astype({
            'ALT_SECTION_NAME': 'object',
            'ALT_SUBSECTION_NAME': 'object',
        })

        section_tree = pd.merge(variable, sections, left_on='SECTION_NAME', right_on='name', how='left')\
            .rename(columns={'id': 'section_id'})
        section_tree = pd.merge(section_tree, subsections, left_on='SUBSECTION_NAME', right_on='name', how='left')\
            .rename(columns={'id': 'subsection_id'})

        alt_section_tree = pd.merge(variable, sections, left_on='ALT_SECTION_NAME', right_on='name', how='left')\
            .rename(columns={'id': 'section_id'})
        alt_section_tree = pd.merge(
            alt_section_tree, subsections, left_on='ALT_SUBSECTION_NAME', right_on='name', how='left')\
            .rename(columns={'id': 'subsection_id'})

        tree = pd.concat(objs=[
            section_tree[['section_id', 'subsection_id']],
            alt_section_tree[['section_id', 'subsection_id']],
        ], sort=False).dropna().astype({
            'section_id': 'int32',
            'subsection_id': 'int32',
        }).sort_values(by=['section_id', 'subsection_id']).drop_duplicates().reset_index()

        tree.to_csv(
            path.join(self.config['target_dir'], 'tree.tsv'),
            columns=['section_id', 'subsection_id'], sep='\t', index_label='id'
        )
        return tree

    def transform_subsection_variable(self, subsections):
        log.info(' - subsection_variable.tsv')

        variable = pd.read_csv(
            path.join(self.s3data_dir, 'variable.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        ).astype({
            'ALT_SECTION_NAME': 'object',
            'ALT_SUBSECTION_NAME': 'object',
        })

        subvars = pd.merge(variable, subsections, left_on='SUBSECTION_NAME', right_on='name', how='left')\
            .rename(columns={'id': 'subsection_id', 'VARIABLE_ID': 'variable_id'})

        alt_subvars = pd.merge(variable, subsections, left_on='ALT_SUBSECTION_NAME', right_on='name', how='left')\
            .rename(columns={'id': 'subsection_id', 'VARIABLE_ID': 'variable_id'})

        subsection_variable = pd.concat(objs=[
            subvars[['subsection_id', 'variable_id']],
            alt_subvars[['subsection_id', 'variable_id']]
        ], sort=False).dropna().astype({'subsection_id': 'int32', 'variable_id': 'int32'})\
            .sort_values(by=['subsection_id', 'variable_id']).drop_duplicates().reset_index()
        subsection_variable.to_csv(
            path.join(self.config['target_dir'], 'subsection_variable.tsv'),
            columns=['subsection_id', 'variable_id'], sep='\t', index_label='id'
        )
        return subsection_variable

    def transform_who(self):
        log.info(' - who.tsv')
        who = pd.read_csv(
            path.join(self.s3data_dir, 'who.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )
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
            path.join(self.config['target_dir'], 'who.tsv'),
            columns=[
                'gender_group', 'age_group_at_1a', 'age_group_at_2a', 'age_group_at_3a', 'year_of_birth',
                'subcohortgwas_group', 'subcohortugli_group', 'subcohortdeep_group', 'subcohortdag3_group'
            ],
            float_format='%.f', sep='\t',
            index_label='ll_nr'
        )
        return who

    def transform_whowhen(self, who):
        log.info(' - who_when.tsv')
        who_when = pd.read_csv(
            path.join(self.s3data_dir, 'whowhen.csv'),
            engine='python', error_bad_lines=not self.config['debug_mode']
        )
        who['ll_nr'] = who.index

        who_when = pd.merge(who, who_when, on='PARTICIPANT_ID', how='inner')
        who_when.rename(columns={'VARIANT_ID': 'variant_id'}, inplace=True)
        who_when.to_csv(
            path.join(self.config['target_dir'], 'who_when.tsv'),
            sep='\t', index_label='id', columns=['ll_nr', 'variant_id']
        )
        return who_when
