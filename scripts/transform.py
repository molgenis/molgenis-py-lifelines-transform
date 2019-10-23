import pandas as pd 

fileFolder = './Catalogus_Tabellen/'
outputFolder = './output/'

print('section.txt                  -> lifelines_section.tsv...')
df = pd.read_csv(fileFolder + 'section.txt', sep='\t', engine='python')
df.rename(columns={'section_id': 'id'}, inplace=True)
df.to_csv(outputFolder + 'lifelines_section.tsv', columns=['id', 'name'], sep='\t', index=False)

print('subsection.txt               -> lifelines_sub_section.tsv...')
df = pd.read_csv(fileFolder + 'subsection.txt', sep='\t', engine='python')
df.rename(columns={'subsection_id':'id'}, inplace=True)
df.to_csv(outputFolder + 'lifelines_sub_section.tsv', columns=['id', 'name'], sep='\t', index=False)

print('variant.txt                  -> lifelines_variants.tsv...')
df = pd.read_csv(fileFolder + 'variant.txt', sep='\t', engine='python')
df.rename(columns={'variant_id':'id'}, inplace=True)
df.to_csv(outputFolder + 'lifelines_variants.tsv', columns=['id', 'name', 'assessment_id'], sep='\t', index=False, float_format='%.f')

print('variable.txt + what_when.txt -> lifelines_variable.tsv...')
variable = pd.read_csv(fileFolder + 'variable.txt', sep='\t', engine='python')
variable.rename(columns={'variable_id':'id', 'variable_name': 'name', 'description_english': 'label'}, inplace=True)

what_when = pd.read_csv(fileFolder + 'what_when.txt', sep='\t', engine='python')
what_when.rename(columns={'variable_id': 'id'},inplace=True)
grouped = what_when.groupby('id').agg(
  variants=('variant_id', lambda col: ','.join(col.map(str)))).reset_index()

variable = pd.merge(variable, grouped, on='id')
variable.to_csv(outputFolder + 'lifelines_variable.tsv', columns=['id','name','label','variants'], sep='\t', index=False, float_format='%.f')

print('variable.txt -> lifelines_tree.tsv')
variable = pd.read_csv(fileFolder + 'variable.txt', sep='\t', engine='python')
variable.rename(columns={'variable_id': 'id'}, inplace=True)
grouped = variable.groupby(['id','section_id','subsection_id']).count().reset_index()
altgrouped = variable.dropna(subset=['alt_section_id', 'alt_subsection_id']).astype({'alt_section_id': 'int32', 'alt_subsection_id': 'int32'}).groupby(['id', 'alt_section_id', 'alt_subsection_id']).count().reset_index()
altgrouped['section_id']=altgrouped['alt_section_id']
altgrouped['subsection_id']=altgrouped['alt_subsection_id']
tree = pd.concat([grouped, altgrouped])
tree.to_csv(outputFolder + 'lifelines_tree.tsv', columns=['id','section_id','subsection_id'], sep='\t', index=False)