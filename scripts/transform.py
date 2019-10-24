import pandas as pd
import numpy as np

fileFolder = './Catalogus_Tabellen/'
outputFolder = './output/'

print('age_group.txt                -> lifelines_age_group.tsv')
age_group = pd.read_csv(fileFolder + 'age_group.txt',
                        sep='\t', engine='python')
age_group.rename(columns={'age_group_id': 'id', 'label': 'name'}, inplace=True)
age_group.to_csv(outputFolder + 'lifelines_age_group.tsv',
                 sep='\t', index=False)

print('gender_group.txt             -> lifelines_gender_group.tsv')
gender_group = pd.read_csv(
    fileFolder + 'gender_group.txt', sep='\t', engine='python')
gender_group.rename(
    columns={'gender_group_id': 'id', 'label': 'name'}, inplace=True)
gender_group.to_csv(
    outputFolder + 'lifelines_gender_group.tsv', sep='\t', index=False)

print('assessment.txt               -> lifelines_assessment.tsv')
assessment = pd.read_csv(fileFolder + 'assessment.txt',
                         sep='\t', engine='python')
assessment.rename(columns={'assessment_id': 'id'}, inplace=True)
assessment.to_csv(outputFolder + 'lifelines_assessment.tsv',
                  sep='\t', index=False)

print('section.txt                  -> lifelines_section.tsv...')
df = pd.read_csv(fileFolder + 'section.txt', sep='\t', engine='python')
df.rename(columns={'section_id': 'id'}, inplace=True)
df.to_csv(outputFolder + 'lifelines_section.tsv',
          columns=['id', 'name'], sep='\t', index=False)

print('subsection.txt               -> lifelines_sub_section.tsv...')
df = pd.read_csv(fileFolder + 'subsection.txt', sep='\t', engine='python')
df.rename(columns={'subsection_id': 'id'}, inplace=True)
df.to_csv(outputFolder + 'lifelines_sub_section.tsv',
          columns=['id', 'name'], sep='\t', index=False)

print('variant.txt                  -> lifelines_variant.tsv...')
df = pd.read_csv(fileFolder + 'variant.txt', sep='\t', engine='python')
df.rename(columns={'variant_id': 'id'}, inplace=True)
df.to_csv(outputFolder + 'lifelines_variant.tsv',
          columns=['id', 'name', 'assessment_id'], sep='\t', index=False, float_format='%.f')

print('variable.txt + what_when.txt -> lifelines_variable.tsv...')
variable = pd.read_csv(fileFolder + 'variable.txt', sep='\t', engine='python')
variable.rename(columns={'variable_id': 'id', 'variable_name': 'name',
                         'description_english': 'label'}, inplace=True)

what_when = pd.read_csv(fileFolder + 'what_when.txt',
                        sep='\t', engine='python')
what_when.rename(columns={'variable_id': 'id'}, inplace=True)
grouped = what_when.groupby('id').agg(
    variants=('variant_id', lambda ids: ','.join(np.unique(ids.map(str))))).reset_index()

variable = pd.merge(variable, grouped, on='id', how='left')
variable.to_csv(outputFolder + 'lifelines_variable.tsv', columns=[
                'id', 'name', 'label', 'variants'], sep='\t', index=False, float_format='%.f')

print('variable.txt                 -> lifelines_tree.tsv')
variable = pd.read_csv(fileFolder + 'variable.txt', sep='\t', engine='python')
subsections = variable[['section_id', 'subsection_id']]
alt_subsections = variable[['alt_section_id', 'alt_subsection_id']].dropna().astype(
    {'alt_section_id': 'int32', 'alt_subsection_id': 'int32'}).rename(columns={'alt_section_id': 'section_id',
                                                                               'alt_subsection_id': 'subsection_id'})
tree = pd.concat(objs=[subsections, alt_subsections], sort=False).sort_values(
    by=['section_id', 'subsection_id']).drop_duplicates().reset_index()
tree.to_csv(outputFolder + 'lifelines_tree.tsv',
            columns=['section_id', 'subsection_id'], sep='\t', index_label='id')

print('variable.txt                 -> lifelines_subsection_variable.tsv')
variable = pd.read_csv(fileFolder + 'variable.txt', sep='\t', engine='python')
subvars = variable[['subsection_id', 'variable_id']]
alt_subvars = variable[['alt_subsection_id', 'variable_id']].dropna().astype(
    {'alt_subsection_id': 'int32'}).rename(columns={'alt_subsection_id': 'subsection_id'})
subsection_variable = pd.concat(objs=[subvars, alt_subvars], sort=False).sort_values(
    by=['subsection_id', 'variable_id']).drop_duplicates().reset_index()
subsection_variable.to_csv(outputFolder + 'lifelines_subsection_variable.tsv',
                           columns=['subsection_id', 'variable_id'], sep='\t', index_label='id')

print('who.txt                      -> lifelines_who.tsv')
who = pd.read_csv(fileFolder + 'who.txt', sep='\t',
                  engine='python', converters={'ll_nr': str})
who.rename(columns={'subcohortGWAS_group': 'subcohortgwas_group', 'subcohortUGLI_group': 'subcohortugli_group',
                    'subcohortDEEP_group': 'subcohortdeep_group', 'subcohortDAG3_group': 'subcohortdag3_group'}, inplace=True)
who.to_csv(outputFolder + 'lifelines_who.tsv', columns=['ll_nr', 'gender_group', 'age_group_at_1a', 'age_group_at_2a', 'age_group_at_3a', 'year_of_birth',
                                                        'subcohortgwas_group', 'subcohortugli_group', 'subcohortdeep_group', 'subcohortdag3_group'], float_format='%.f', sep='\t', index=False)

print('who_when.txt                 -> lifelines_who_when.tsv')
who_when = pd.read_csv(fileFolder + 'who_when.txt',
                       sep='\t', engine='python', converters={'ll_nr': str})
# TODO: remove this workaround.
# Join with the who table to filter out the ll_nrs present in who_when but missing in who
who['missing'] = who['ll_nr']
merged = pd.merge(
    left=who_when, right=who[['ll_nr', 'missing']], on='ll_nr', how='left')
merged.dropna(subset=['missing']).to_csv(outputFolder + 'lifelines_who_when.tsv', sep='\t', index_label='id',
                                         columns=['ll_nr', 'variant_id'])
