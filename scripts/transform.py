import pandas as pd 

fileFolder = './Catalogus_Tabellen/'

outputFolder = './output/'

print('section.txt -> lifelines_section.tsv...')
df = pd.read_csv(fileFolder + 'section.txt', sep='\t', engine='python')
df['id'] = df['section_id']
df.to_csv(outputFolder + 'lifelines_section.tsv', columns=['id', 'name'], sep='\t', index=False)

print('subsection.txt -> lifelines_sub_section.tsv...')
df = pd.read_csv(fileFolder + 'subsection.txt', sep='\t', engine='python')
df['id'] = df['subsection_id']
df.to_csv(outputFolder + 'lifelines_sub_section.tsv', columns=['id', 'name'], sep='\t', index=False)

print('variant.txt -> lifelines_variants.tsv...')
df = pd.read_csv(fileFolder + 'variant.txt', sep='\t', engine='python')
df['id'] = df['variant_id']
df.to_csv(outputFolder + 'lifelines_variants.tsv', columns=['id', 'name', 'assessment_id'], sep='\t', index=False, float_format='%.f')