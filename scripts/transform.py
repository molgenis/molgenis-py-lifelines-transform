import pandas as pd

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

print('variant.txt                  -> lifelines_variants.tsv...')
df = pd.read_csv(fileFolder + 'variant.txt', sep='\t', engine='python')
df.rename(columns={'variant_id': 'id'}, inplace=True)
df.to_csv(outputFolder + 'lifelines_variants.tsv',
          columns=['id', 'name', 'assessment_id'], sep='\t', index=False, float_format='%.f')

print('variable.txt + what_when.txt -> lifelines_variable.tsv...')
variable = pd.read_csv(fileFolder + 'variable.txt', sep='\t', engine='python')
variable.rename(columns={'variable_id': 'id', 'variable_name': 'name',
                         'description_english': 'label'}, inplace=True)

what_when = pd.read_csv(fileFolder + 'what_when.txt',
                        sep='\t', engine='python')
what_when.rename(columns={'variable_id': 'id'}, inplace=True)
grouped = what_when.groupby('id').agg(
    variants=('variant_id', lambda col: ','.join(col.map(str)))).reset_index()

variable = pd.merge(variable, grouped, on='id')
variable.to_csv(outputFolder + 'lifelines_variable.tsv', columns=[
                'id', 'name', 'label', 'variants'], sep='\t', index=False, float_format='%.f')

print('variable.txt                 -> lifelines_tree.tsv')
variable = pd.read_csv(fileFolder + 'variable.txt', sep='\t', engine='python')
grouped = variable.groupby(
    ['section_id', 'subsection_id']).count().reset_index()
altgrouped = variable.dropna(subset=['alt_section_id', 'alt_subsection_id']).astype(
    {'alt_section_id': 'int32', 'alt_subsection_id': 'int32'}).groupby(['alt_section_id', 'alt_subsection_id']).count().reset_index()
altgrouped.rename({'alt_section_id': 'section_id',
                   'alt_subsection_id': 'subsection_id'}, inplace=True)
tree = pd.concat(objs=[grouped, altgrouped], sort=True).groupby(
    ['section_id', 'subsection_id']).size().reset_index()
tree.to_csv(outputFolder + 'lifelines_tree.tsv',
            columns=['section_id', 'subsection_id'], sep='\t', index_label='id')

print('variable.txt                 -> lifelines_subsection_variable.tsv')
variable = pd.read_csv(fileFolder + 'variable.txt', sep='\t', engine='python')
grouped = variable.groupby(
    ['variable_id', 'subsection_id']).count().reset_index()
altgrouped = variable.dropna(subset=['alt_subsection_id']).astype(
    {'alt_subsection_id': 'int32'}).groupby(['variable_id', 'alt_subsection_id']).count().reset_index()
altgrouped.rename({'alt_subsection_id': 'subsection_id'}, inplace=True)
subsection_variable = pd.concat(objs=[grouped, altgrouped], sort=True).groupby(
    ['subsection_id', 'variable_id']).size().reset_index()
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
who_when.to_csv(outputFolder + 'lifelines_who_when.tsv',
                sep='\t', index_label='id')
